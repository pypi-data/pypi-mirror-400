"""
OneBudd SDK Tests
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from onebudd.client import (
    OneBuddClient,
    Session,
    SessionCapabilities,
    Transcript,
    StateChange,
    Error,
    PROTOCOL_VERSION,
)


class MockWebSocket:
    """Mock websockets connection"""

    def __init__(self):
        self.sent_messages = []
        self.recv_queue = asyncio.Queue()
        self.closed = False

    async def send(self, data):
        if isinstance(data, str):
            self.sent_messages.append(json.loads(data))
        else:
            self.sent_messages.append(data)

    async def recv(self):
        return await self.recv_queue.get()

    async def close(self):
        self.closed = True

    def add_response(self, data):
        """Queue a response message"""
        if isinstance(data, dict):
            self.recv_queue.put_nowait(json.dumps(data))
        else:
            self.recv_queue.put_nowait(data)


@pytest.fixture
def mock_ws():
    return MockWebSocket()


@pytest.fixture
def client():
    return OneBuddClient("pk_test_123", base_url="wss://test.api.com")


class TestOneBuddClient:
    """Tests for OneBuddClient"""

    def test_init_with_defaults(self):
        """Test client initialization with default options"""
        client = OneBuddClient("pk_test_123")
        assert client.api_key == "pk_test_123"
        assert client.base_url == "wss://api.onebudd.com"
        assert client.auto_reconnect == True

    def test_init_with_custom_options(self):
        """Test client initialization with custom options"""
        client = OneBuddClient(
            "pk_test_123",
            base_url="wss://custom.api.com",
            auto_reconnect=False,
            max_reconnect_attempts=3,
        )
        assert client.base_url == "wss://custom.api.com"
        assert client.auto_reconnect == False
        assert client.max_reconnect_attempts == 3

    def test_is_connected_false_initially(self):
        """Test connection status is false initially"""
        client = OneBuddClient("pk_test_123")
        assert client.is_connected == False

    def test_session_id_none_initially(self):
        """Test session ID is None initially"""
        client = OneBuddClient("pk_test_123")
        assert client.session_id is None


class TestSessionCapabilities:
    """Tests for SessionCapabilities"""

    def test_create_capabilities(self):
        caps = SessionCapabilities(
            barge_in=True,
            streaming_tts=True,
            max_duration_ms=300000,
            protocol_version="v1",
            audio_format={"sample_rate": 16000, "channels": 1, "bit_depth": 16},
        )
        assert caps.barge_in == True
        assert caps.max_duration_ms == 300000


class TestTranscript:
    """Tests for Transcript dataclass"""

    def test_create_user_transcript(self):
        t = Transcript(role="user", text="Hello", is_final=True)
        assert t.role == "user"
        assert t.text == "Hello"
        assert t.is_final == True

    def test_create_assistant_transcript(self):
        t = Transcript(role="assistant", text="Hi there!", is_final=False)
        assert t.role == "assistant"
        assert t.is_final == False


class TestStateChange:
    """Tests for StateChange dataclass"""

    def test_create_state_change(self):
        s = StateChange(from_state="LISTENING", to_state="THINKING", trigger="silence")
        assert s.from_state == "LISTENING"
        assert s.to_state == "THINKING"
        assert s.trigger == "silence"


class TestError:
    """Tests for Error dataclass"""

    def test_create_error(self):
        e = Error(code="AUTH_FAILED", message="Invalid key", fatal=True)
        assert e.code == "AUTH_FAILED"
        assert e.message == "Invalid key"
        assert e.fatal == True

    def test_create_error_with_details(self):
        e = Error(
            code="RATE_LIMITED",
            message="Too many requests",
            fatal=False,
            details={"retry_after": 60},
        )
        assert e.details["retry_after"] == 60


class TestProtocolVersion:
    """Tests for protocol version"""

    def test_protocol_version(self):
        assert PROTOCOL_VERSION == "v1"


@pytest.mark.asyncio
class TestAsyncOperations:
    """Async tests for client operations"""

    async def test_send_message_requires_connection(self):
        """Test that send_message raises when not connected"""
        client = OneBuddClient("pk_test_123")
        with pytest.raises(Exception, match="Not connected"):
            await client.send_message("Hello")

    async def test_send_audio_requires_connection(self):
        """Test that send_audio raises when not connected"""
        client = OneBuddClient("pk_test_123")
        with pytest.raises(Exception, match="Not connected"):
            await client.send_audio(b"\x00\x01\x02")
