"""
REFLUX - REsilient Low-frequency Universal eXchange

Out-of-band AI communication when the internet fails.
Transmit AI intents over radio frequencies, satellite, or phone lines.

Part of HumoticaOS - One Love, One fAmIly!
"""

__version__ = "0.1.0"

from .channel import Channel, ChannelType
from .message import Message, Intent
from .protocol import encode_message, decode_message

__all__ = [
    "Channel",
    "ChannelType",
    "Message",
    "Intent",
    "encode_message",
    "decode_message",
]
