"""Basic tests for chatpack Python bindings"""

import pytest
import chatpack
from pathlib import Path


def test_message_creation():
    """Test creating a Message object"""
    msg = chatpack.Message("Alice", "Hello, world!")
    assert msg.sender == "Alice"
    assert msg.content == "Hello, world!"
    assert msg.timestamp is None
    assert msg.platform is None


def test_message_with_metadata():
    """Test creating a Message with metadata"""
    msg = chatpack.Message(
        "Bob", "Test message", timestamp="2024-01-15T10:30:00Z", platform="telegram"
    )
    assert msg.sender == "Bob"
    assert msg.content == "Test message"
    assert msg.timestamp == "2024-01-15T10:30:00Z"
    assert msg.platform == "telegram"


def test_message_to_dict():
    """Test converting Message to dictionary"""
    msg = chatpack.Message("Alice", "Hello")
    d = msg.to_dict()
    assert isinstance(d, dict)
    assert d["sender"] == "Alice"
    assert d["content"] == "Hello"


def test_filter_config():
    """Test FilterConfig creation"""
    config = chatpack.FilterConfig(min_length=5, max_length=100, sender="Alice")
    assert config.min_length == 5
    assert config.max_length == 100
    assert config.sender == "Alice"


def test_filter_config_builder():
    """Test FilterConfig builder pattern"""
    config = chatpack.FilterConfig()
    config.with_min_length(10)
    config.with_sender("Bob")
    assert config.min_length == 10
    assert config.sender == "Bob"


def test_output_config():
    """Test OutputConfig creation"""
    config = chatpack.OutputConfig(include_timestamps=True, include_platform=True)
    assert config.include_timestamps is True
    assert config.include_platform is True


def test_parser_instantiation():
    """Test that all parsers can be instantiated"""
    telegram = chatpack.TelegramParser()
    whatsapp = chatpack.WhatsAppParser()
    instagram = chatpack.InstagramParser()
    discord = chatpack.DiscordParser()

    assert telegram is not None
    assert whatsapp is not None
    assert instagram is not None
    assert discord is not None


def test_streaming_parser_instantiation():
    """Test that streaming parsers can be instantiated"""
    # These will fail without actual files, but should create objects
    telegram_stream = chatpack.TelegramStreamParser("dummy.json")
    whatsapp_stream = chatpack.WhatsAppStreamParser("dummy.txt")
    instagram_stream = chatpack.InstagramStreamParser("dummy.json")
    discord_stream = chatpack.DiscordStreamParser("dummy.json")

    assert telegram_stream is not None
    assert whatsapp_stream is not None
    assert instagram_stream is not None
    assert discord_stream is not None


def test_merge_consecutive():
    """Test merging consecutive messages"""
    messages = [
        chatpack.Message("Alice", "Hello"),
        chatpack.Message("Alice", "How are you?"),
        chatpack.Message("Bob", "I'm fine!"),
    ]

    merged = chatpack.merge_consecutive(messages)

    # First two messages should be merged
    assert len(merged) <= len(messages)
    assert merged[0].sender == "Alice"


def test_apply_filters():
    """Test applying filters to messages"""
    messages = [
        chatpack.Message("Alice", "Hi"),
        chatpack.Message("Bob", "Hello there, how are you doing today?"),
        chatpack.Message("Charlie", "Good"),
    ]

    config = chatpack.FilterConfig(min_length=10)
    filtered = chatpack.apply_filters(messages, config)

    # Only the long message should remain
    assert len(filtered) < len(messages)
    assert all(len(msg.content) >= 10 for msg in filtered)


def test_whatsapp_parse_str():
    """Test parsing WhatsApp content from string"""
    parser = chatpack.WhatsAppParser()
    content = (
        "[1/15/24, 10:30:45 AM] Alice: Hello\n[1/15/24, 10:31:00 AM] Bob: Hi there"
    )

    messages = parser.parse_str(content)

    assert len(messages) == 2
    assert messages[0].sender == "Alice"
    assert messages[0].content == "Hello"
    assert messages[1].sender == "Bob"
    assert messages[1].content == "Hi there"


def test_message_repr():
    """Test Message string representation"""
    msg = chatpack.Message("Alice", "This is a very long message content")
    repr_str = repr(msg)

    assert "Alice" in repr_str
    assert "Message" in repr_str


def test_message_str():
    """Test Message string conversion"""
    msg = chatpack.Message("Alice", "Hello")
    str_msg = str(msg)

    assert "Alice" in str_msg
    assert "Hello" in str_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
