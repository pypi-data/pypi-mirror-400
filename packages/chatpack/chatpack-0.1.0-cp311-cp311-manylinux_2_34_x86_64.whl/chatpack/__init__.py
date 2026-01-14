"""
chatpack - High-performance chat export parser for Python

Parse and convert chat exports from Telegram, WhatsApp, Instagram, and Discord
into LLM-friendly formats. Built with Rust for maximum performance.
"""

from ._chatpack import (  # type: ignore
    # Message types
    PyMessage,
    PyFilterConfig,
    PyOutputConfig,
    # Parsers (classes)
    TelegramParser,
    WhatsAppParser,
    InstagramParser,
    DiscordParser,
    # Streaming parsers (пока закомментированы в Rust, но если они есть в pyi, можно оставить)
    TelegramStreamParser,
    WhatsAppStreamParser,
    InstagramStreamParser,
    DiscordStreamParser,
    # Convenience functions
    parse_telegram,
    parse_whatsapp,
    parse_instagram,
    parse_discord,
    # Utilities
    merge_consecutive,
    apply_filters,
)

# Compatibility aliases (Делаем красивые имена для пользователей)
Message = PyMessage
FilterConfig = PyFilterConfig
OutputConfig = PyOutputConfig

__version__ = "0.1.0"

__all__ = [
    # Types
    "Message",
    "PyMessage",
    "FilterConfig",
    "PyFilterConfig",
    "OutputConfig",
    "PyOutputConfig",
    # Parsers
    "TelegramParser",
    "WhatsAppParser",
    "InstagramParser",
    "DiscordParser",
    # Streaming Parsers
    "TelegramStreamParser",
    "WhatsAppStreamParser",
    "InstagramStreamParser",
    "DiscordStreamParser",
    # Functions
    "parse_telegram",
    "parse_whatsapp",
    "parse_instagram",
    "parse_discord",
    "merge_consecutive",
    "apply_filters",
]
