"""
REFLUX Channels - Transport layers for out-of-band communication.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any
import logging

from .message import Message

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Available channel types."""
    SIP = "sip"           # VoIP/SIP trunk
    HAM_RADIO = "ham"     # Amateur radio (HF/VHF)
    SATELLITE = "sat"     # Satellite link
    PSTN = "pstn"         # Plain old telephone
    ACOUSTIC = "acoustic" # Direct audio (speaker/mic)


@dataclass
class ChannelConfig:
    """Configuration for a REFLUX channel."""
    channel_type: ChannelType
    endpoint: str
    port: Optional[int] = None
    frequency: Optional[str] = None  # For radio: "7.074MHz"
    callsign: Optional[str] = None   # For ham radio
    mode: str = "SSTV"               # SSTV, RTTY, PSK31, etc.


class Channel(ABC):
    """
    Abstract base class for REFLUX communication channels.

    A channel handles the physical transport of encoded messages.
    """

    def __init__(self, config: ChannelConfig):
        self.config = config
        self._connected = False
        self._on_receive: Optional[Callable[[Message], None]] = None

    @property
    def connected(self) -> bool:
        return self._connected

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the channel."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the channel connection."""
        pass

    @abstractmethod
    def send(self, message: Message) -> bool:
        """Send a message through the channel."""
        pass

    @abstractmethod
    def receive(self, timeout: float = 30.0) -> Optional[Message]:
        """Receive a message from the channel."""
        pass

    def on_receive(self, callback: Callable[[Message], None]) -> None:
        """Set callback for incoming messages."""
        self._on_receive = callback

    @classmethod
    def SIP(cls, endpoint: str, port: int = 5060) -> "SIPChannel":
        """Create a SIP channel."""
        config = ChannelConfig(
            channel_type=ChannelType.SIP,
            endpoint=endpoint,
            port=port,
        )
        return SIPChannel(config)

    @classmethod
    def HamRadio(cls, frequency: str, callsign: str, mode: str = "SSTV") -> "HamRadioChannel":
        """Create a Ham Radio channel."""
        config = ChannelConfig(
            channel_type=ChannelType.HAM_RADIO,
            endpoint=frequency,
            frequency=frequency,
            callsign=callsign,
            mode=mode,
        )
        return HamRadioChannel(config)

    @classmethod
    def Satellite(cls, endpoint: str) -> "SatelliteChannel":
        """Create a Satellite channel."""
        config = ChannelConfig(
            channel_type=ChannelType.SATELLITE,
            endpoint=endpoint,
        )
        return SatelliteChannel(config)


class SIPChannel(Channel):
    """SIP/VoIP channel using Asterisk or similar."""

    def __init__(self, config: ChannelConfig):
        super().__init__(config)
        self._sip_client = None

    def connect(self) -> bool:
        """Connect to SIP endpoint."""
        logger.info(f"Connecting to SIP endpoint: {self.config.endpoint}:{self.config.port}")
        # TODO: Implement actual SIP connection via PJSIP or similar
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from SIP endpoint."""
        logger.info("Disconnecting SIP channel")
        self._connected = False

    def send(self, message: Message) -> bool:
        """Send message via SIP audio channel."""
        if not self._connected:
            logger.error("Channel not connected")
            return False

        from .protocol import encode_message

        # Encode message to SSTV audio
        audio_data = encode_message(message)

        # TODO: Transmit audio via SIP call
        logger.info(f"Transmitting via SIP: {message}")
        return True

    def receive(self, timeout: float = 30.0) -> Optional[Message]:
        """Receive message from SIP audio channel."""
        # TODO: Receive and decode SSTV audio from SIP
        return None


class HamRadioChannel(Channel):
    """Amateur radio channel (HF/VHF with SSTV/digital modes)."""

    def connect(self) -> bool:
        """Connect to radio (via rigctld or similar)."""
        logger.info(f"Tuning to {self.config.frequency} ({self.config.callsign})")
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from radio."""
        self._connected = False

    def send(self, message: Message) -> bool:
        """Transmit message via radio."""
        if not self._connected:
            return False

        from .protocol import encode_message
        audio_data = encode_message(message)

        # TODO: Key PTT and transmit audio
        logger.info(f"TX on {self.config.frequency}: {message}")
        return True

    def receive(self, timeout: float = 30.0) -> Optional[Message]:
        """Receive message from radio."""
        # TODO: Monitor frequency and decode SSTV
        return None


class SatelliteChannel(Channel):
    """Satellite communication channel."""

    def connect(self) -> bool:
        """Establish satellite link."""
        logger.info(f"Connecting to satellite: {self.config.endpoint}")
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Close satellite link."""
        self._connected = False

    def send(self, message: Message) -> bool:
        """Send via satellite."""
        if not self._connected:
            return False

        logger.info(f"Uplink via satellite: {message}")
        return True

    def receive(self, timeout: float = 30.0) -> Optional[Message]:
        """Receive from satellite."""
        return None
