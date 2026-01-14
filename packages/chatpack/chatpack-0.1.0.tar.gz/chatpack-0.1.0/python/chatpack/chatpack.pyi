"""Type stubs for chatpack"""

from typing import List, Optional, Iterator, Dict, Any
from datetime import datetime

class Message:
    """Universal message representation across all platforms"""

    sender: str
    content: str
    timestamp: Optional[str]
    platform: Optional[str]

    def __init__(
        self,
        sender: str,
        content: str,
        timestamp: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> None: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class FilterConfig:
    """Configuration for filtering messages"""

    min_length: Optional[int]
    max_length: Optional[int]
    sender: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        sender: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> None: ...
    def with_min_length(self, length: int) -> "FilterConfig": ...
    def with_max_length(self, length: int) -> "FilterConfig": ...
    def with_sender(self, sender: str) -> "FilterConfig": ...
    def with_date_from(self, date: str) -> "FilterConfig": ...
    def with_date_to(self, date: str) -> "FilterConfig": ...

class OutputConfig:
    """Configuration for output formatting"""

    include_timestamps: bool
    include_platform: bool

    def __init__(
        self, include_timestamps: bool = True, include_platform: bool = False
    ) -> None: ...
    def with_timestamps(self) -> "OutputConfig": ...
    def with_platform(self) -> "OutputConfig": ...

class TelegramParser:
    """Parser for Telegram JSON exports"""

    def __init__(self) -> None: ...
    def parse(
        self,
        path: str,
        merge: bool = False,
        min_length: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Message]: ...
    def parse_str(self, content: str) -> List[Message]: ...

class WhatsAppParser:
    """Parser for WhatsApp TXT exports"""

    def __init__(self) -> None: ...
    def parse(
        self,
        path: str,
        merge: bool = False,
        min_length: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Message]: ...
    def parse_str(self, content: str) -> List[Message]: ...

class InstagramParser:
    """Parser for Instagram JSON exports"""

    def __init__(self) -> None: ...
    def parse(
        self,
        path: str,
        merge: bool = False,
        min_length: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Message]: ...
    def parse_str(self, content: str) -> List[Message]: ...

class DiscordParser:
    """Parser for Discord exports"""

    def __init__(self) -> None: ...
    def parse(
        self,
        path: str,
        merge: bool = False,
        min_length: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Message]: ...
    def parse_str(self, content: str) -> List[Message]: ...

class TelegramStreamParser:
    """Streaming parser for large Telegram exports"""

    def __init__(self, path: str) -> None: ...
    def __iter__(self) -> Iterator[Message]: ...

class WhatsAppStreamParser:
    """Streaming parser for large WhatsApp exports"""

    def __init__(self, path: str) -> None: ...
    def __iter__(self) -> Iterator[Message]: ...

class InstagramStreamParser:
    """Streaming parser for large Instagram exports"""

    def __init__(self, path: str) -> None: ...
    def __iter__(self) -> Iterator[Message]: ...

class DiscordStreamParser:
    """Streaming parser for large Discord exports"""

    def __init__(self, path: str) -> None: ...
    def __iter__(self) -> Iterator[Message]: ...

def parse_telegram(
    path: str,
    merge: bool = False,
    min_length: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Message]:
    """
    Parse Telegram JSON export

    Args:
        path: Path to the Telegram export file (result.json)
        merge: Merge consecutive messages from the same sender
        min_length: Minimum message length to include
        date_from: Filter messages from this date (ISO format)
        date_to: Filter messages until this date (ISO format)

    Returns:
        List of parsed messages
    """
    ...

def parse_whatsapp(
    path: str,
    merge: bool = False,
    min_length: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Message]:
    """
    Parse WhatsApp TXT export

    Args:
        path: Path to the WhatsApp export file (chat.txt)
        merge: Merge consecutive messages from the same sender
        min_length: Minimum message length to include
        date_from: Filter messages from this date (ISO format)
        date_to: Filter messages until this date (ISO format)

    Returns:
        List of parsed messages
    """
    ...

def parse_instagram(
    path: str,
    merge: bool = False,
    min_length: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Message]:
    """
    Parse Instagram JSON export (GDPR dump)

    Args:
        path: Path to the Instagram export file (messages.json)
        merge: Merge consecutive messages from the same sender
        min_length: Minimum message length to include
        date_from: Filter messages from this date (ISO format)
        date_to: Filter messages until this date (ISO format)

    Returns:
        List of parsed messages
    """
    ...

def parse_discord(
    path: str,
    merge: bool = False,
    min_length: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Message]:
    """
    Parse Discord export (JSON/CSV/TXT from DiscordChatExporter)

    Args:
        path: Path to the Discord export file
        merge: Merge consecutive messages from the same sender
        min_length: Minimum message length to include
        date_from: Filter messages from this date (ISO format)
        date_to: Filter messages until this date (ISO format)

    Returns:
        List of parsed messages
    """
    ...

def merge_consecutive(
    messages: List[Message], time_threshold: int = 300
) -> List[Message]:
    """
    Merge consecutive messages from the same sender

    Args:
        messages: List of messages to merge
        time_threshold: Maximum time gap in seconds between messages

    Returns:
        List of merged messages
    """
    ...

def apply_filters(messages: List[Message], config: FilterConfig) -> List[Message]:
    """
    Apply filters to messages

    Args:
        messages: List of messages to filter
        config: Filter configuration

    Returns:
        Filtered list of messages
    """
    ...

PyMessage = Message
PyFilterConfig = FilterConfig
PyOutputConfig = OutputConfig
