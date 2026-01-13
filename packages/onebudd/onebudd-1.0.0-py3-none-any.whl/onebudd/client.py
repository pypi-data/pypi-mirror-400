"""
OneBudd SDK - Python

Real-time voice AI SDK for OneBudd STS.
"""

import asyncio
import json
import base64
import time
from typing import Callable, Optional, Dict, Any, Union
from dataclasses import dataclass
import websockets
from websockets.asyncio.client import ClientConnection

PROTOCOL_VERSION = "v1"


# ============= Types =============

@dataclass
class SessionCapabilities:
    barge_in: bool
    streaming_tts: bool
    max_duration_ms: int
    protocol_version: str
    audio_format: Dict[str, int]


@dataclass
class Transcript:
    role: str  # 'user' | 'assistant'
    text: str
    is_final: bool


@dataclass
class StateChange:
    from_state: str
    to_state: str
    trigger: str


@dataclass
class Error:
    code: str
    message: str
    fatal: bool
    details: Optional[Dict[str, Any]] = None


@dataclass
class Session:
    id: str
    capabilities: SessionCapabilities
    connected: bool


# ============= Client =============

class OneBuddClient:
    """OneBudd STS Client - Real-time voice AI conversations"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "wss://api.onebudd.com",
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5,
        reconnect_delay_ms: int = 1000,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay_ms = reconnect_delay_ms

        self._ws: Optional[ClientConnection] = None
        self._session: Optional[Session] = None
        self._audio_seq = 0
        self._reconnect_attempts = 0
        self._running = False

        # Callbacks
        self._on_audio: Optional[Callable[[bytes], None]] = None
        self._on_transcript: Optional[Callable[[Transcript], None]] = None
        self._on_state_change: Optional[Callable[[StateChange], None]] = None
        self._on_error: Optional[Callable[[Error], None]] = None
        self._on_connected: Optional[Callable[[SessionCapabilities], None]] = None
        self._on_disconnected: Optional[Callable[[str], None]] = None

    # ============= Connection =============

    async def start_session(self) -> Session:
        """Start a new session"""
        self._ws = await websockets.connect(self.base_url)
        self._running = True

        # Send session.init
        await self._send({
            "type": "session.init",
            "version": PROTOCOL_VERSION,
            "session_id": "",
            "timestamp": self._now(),
            "payload": {"auth_token": self.api_key},
        })

        # Wait for session.started
        while self._running:
            msg = await self._ws.recv()
            data = json.loads(msg)

            if data["type"] == "session.started":
                caps = data["payload"]["capabilities"]
                self._session = Session(
                    id=data["session_id"],
                    capabilities=SessionCapabilities(
                        barge_in=caps["barge_in"],
                        streaming_tts=caps["streaming_tts"],
                        max_duration_ms=caps["max_duration_ms"],
                        protocol_version=caps["protocol_version"],
                        audio_format=caps["audio_format"],
                    ),
                    connected=True,
                )
                self._reconnect_attempts = 0
                if self._on_connected:
                    self._on_connected(self._session.capabilities)
                return self._session

            elif data["type"] == "error":
                payload = data["payload"]
                raise Exception(f"Connection failed: {payload['message']}")

        raise Exception("Connection closed before session started")

    async def run(self):
        """Run the message loop (call after start_session)"""
        if not self._ws or not self._session:
            raise Exception("Not connected. Call start_session first.")

        try:
            async for msg in self._ws:
                await self._handle_message(msg)
        except websockets.ConnectionClosed as e:
            self._handle_disconnect(str(e))

    async def end_session(self):
        """End the current session"""
        if not self._ws or not self._session:
            return

        await self._send({
            "type": "session.end",
            "version": PROTOCOL_VERSION,
            "session_id": self._session.id,
            "timestamp": self._now(),
            "payload": {"reason": "user_request"},
        })

        self._running = False
        await self._ws.close()
        self._session = None
        self._ws = None

    # ============= Audio =============

    async def send_audio(self, chunk: bytes):
        """Send audio chunk (raw PCM bytes)"""
        if not self._ws or not self._session:
            raise Exception("Not connected")

        # Send as binary for lowest latency
        await self._ws.send(chunk)

    async def send_audio_with_meta(self, chunk: bytes, seq: Optional[int] = None):
        """Send audio chunk with metadata (JSON)"""
        if not self._ws or not self._session:
            raise Exception("Not connected")

        if seq is None:
            self._audio_seq += 1
            seq = self._audio_seq

        await self._send({
            "type": "audio.chunk",
            "version": PROTOCOL_VERSION,
            "session_id": self._session.id,
            "timestamp": self._now(),
            "payload": {
                "data": base64.b64encode(chunk).decode("utf-8"),
                "seq": seq,
                "client_timestamp": self._now(),
            },
        })

    # ============= Text Input =============

    async def send_message(self, text: str):
        """Send text message (bypasses STT)"""
        if not self._ws or not self._session:
            raise Exception("Not connected")

        await self._send({
            "type": "user.message",
            "version": PROTOCOL_VERSION,
            "session_id": self._session.id,
            "timestamp": self._now(),
            "payload": {"text": text},
        })

    # ============= Control =============

    async def cancel(self, target: str = "all"):
        """Cancel active operations ('llm', 'tts', or 'all')"""
        if not self._ws or not self._session:
            return

        await self._send({
            "type": "control.cancel",
            "version": PROTOCOL_VERSION,
            "session_id": self._session.id,
            "timestamp": self._now(),
            "payload": {"target": target},
        })

    # ============= Events =============

    def on_audio(self, handler: Callable[[bytes], None]):
        """Set audio callback"""
        self._on_audio = handler

    def on_transcript(self, handler: Callable[[Transcript], None]):
        """Set transcript callback"""
        self._on_transcript = handler

    def on_state_change(self, handler: Callable[[StateChange], None]):
        """Set state change callback"""
        self._on_state_change = handler

    def on_error(self, handler: Callable[[Error], None]):
        """Set error callback"""
        self._on_error = handler

    def on_connected(self, handler: Callable[[SessionCapabilities], None]):
        """Set connected callback"""
        self._on_connected = handler

    def on_disconnected(self, handler: Callable[[str], None]):
        """Set disconnected callback"""
        self._on_disconnected = handler

    # ============= Internal =============

    async def _handle_message(self, msg):
        if isinstance(msg, bytes):
            if self._on_audio:
                self._on_audio(msg)
            return

        data = json.loads(msg)
        msg_type = data["type"]

        if msg_type == "audio.playback":
            audio_bytes = base64.b64decode(data["payload"]["data"])
            if self._on_audio:
                self._on_audio(audio_bytes)

        elif msg_type == "transcript":
            if self._on_transcript:
                p = data["payload"]
                self._on_transcript(Transcript(
                    role=p["role"],
                    text=p["text"],
                    is_final=p["is_final"],
                ))

        elif msg_type == "state.change":
            if self._on_state_change:
                p = data["payload"]
                self._on_state_change(StateChange(
                    from_state=p["from"],
                    to_state=p["to"],
                    trigger=p["trigger"],
                ))

        elif msg_type == "error":
            if self._on_error:
                p = data["payload"]
                self._on_error(Error(
                    code=p["code"],
                    message=p["message"],
                    fatal=p["fatal"],
                    details=p.get("details"),
                ))

        elif msg_type == "ping":
            await self._send_pong(data["payload"]["event_id"])

    def _handle_disconnect(self, reason: str):
        if self._on_disconnected:
            self._on_disconnected(reason)

        if self.auto_reconnect and self._reconnect_attempts < self.max_reconnect_attempts:
            self._reconnect_attempts += 1
            delay = self.reconnect_delay_ms * (2 ** (self._reconnect_attempts - 1)) / 1000
            print(f"[OneBudd SDK] Reconnecting in {delay}s (attempt {self._reconnect_attempts})")
            asyncio.create_task(self._reconnect(delay))

    async def _reconnect(self, delay: float):
        await asyncio.sleep(delay)
        try:
            await self.start_session()
            asyncio.create_task(self.run())
        except Exception as e:
            print(f"[OneBudd SDK] Reconnect failed: {e}")

    async def _send_pong(self, event_id: int):
        if not self._ws or not self._session:
            return

        await self._send({
            "type": "pong",
            "version": PROTOCOL_VERSION,
            "session_id": self._session.id,
            "timestamp": self._now(),
            "payload": {"event_id": event_id},
        })

    async def _send(self, msg: dict):
        if self._ws:
            await self._ws.send(json.dumps(msg))

    def _now(self) -> int:
        return int(time.time() * 1000)

    # ============= Properties =============

    @property
    def is_connected(self) -> bool:
        return self._session is not None and self._session.connected

    @property
    def session_id(self) -> Optional[str]:
        return self._session.id if self._session else None

    @property
    def capabilities(self) -> Optional[SessionCapabilities]:
        return self._session.capabilities if self._session else None
