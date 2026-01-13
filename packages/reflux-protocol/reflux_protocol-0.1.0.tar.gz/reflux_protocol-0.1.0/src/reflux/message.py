"""
REFLUX Message - Intent-based messaging for out-of-band AI communication.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime
import hashlib
import json


class Intent(Enum):
    """Standard REFLUX intents."""
    PING = "ping"
    PONG = "pong"
    STATUS = "status"
    COMMAND = "command"
    ALERT = "alert"
    SYNC = "sync"
    ACK = "ack"
    EMERGENCY = "emergency"


@dataclass
class Message:
    """
    A REFLUX message with intent and payload.

    Example:
        msg = Message(
            intent=Intent.STATUS,
            payload={"agent": "root_ai", "health": "ok"}
        )
    """
    intent: Intent | str
    payload: Dict[str, Any] = field(default_factory=dict)
    sender: str = "unknown"
    receiver: str = "broadcast"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: Optional[str] = None

    def __post_init__(self):
        # Convert string intent to enum if needed
        if isinstance(self.intent, str):
            try:
                self.intent = Intent(self.intent)
            except ValueError:
                pass  # Keep as string for custom intents

        # Generate message ID if not provided
        if self.message_id is None:
            content = f"{self.sender}:{self.receiver}:{self.intent}:{self.timestamp.isoformat()}"
            self.message_id = hashlib.sha256(content.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "id": self.message_id,
            "intent": self.intent.value if isinstance(self.intent, Intent) else self.intent,
            "payload": self.payload,
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            intent=data.get("intent", "unknown"),
            payload=data.get("payload", {}),
            sender=data.get("sender", "unknown"),
            receiver=data.get("receiver", "broadcast"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow(),
            message_id=data.get("id"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def __str__(self) -> str:
        intent_str = self.intent.value if isinstance(self.intent, Intent) else self.intent
        return f"[{self.message_id}] {self.sender} -> {self.receiver}: {intent_str}"
