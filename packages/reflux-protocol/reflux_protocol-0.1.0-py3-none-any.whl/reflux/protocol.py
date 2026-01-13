"""
REFLUX Protocol - Encode/decode messages for transmission.

The protocol converts Message objects to/from audio signals
that can be transmitted over any analog channel.
"""

import json
import logging
from typing import Optional, Tuple
from io import BytesIO

from .message import Message

logger = logging.getLogger(__name__)

# Try to import SSTV encoder/decoder from sensory
try:
    from sensory import SSTVEncoder, SSTVDecoder
    HAS_SENSORY = True
except ImportError:
    HAS_SENSORY = False
    logger.warning("sensory package not available, using fallback encoding")


def message_to_image(message: Message, width: int = 320, height: int = 256) -> bytes:
    """
    Convert a message to an image for SSTV transmission.

    The image contains:
    - Header with REFLUX magic bytes
    - QR code with message JSON
    - Fallback text rendering
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import qrcode
    except ImportError:
        # Fallback: return raw JSON as bytes
        return message.to_json().encode()

    # Create image
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)

    # Add REFLUX header
    draw.text((10, 10), "REFLUX", fill='cyan')
    draw.text((10, 30), f"ID: {message.message_id}", fill='white')

    # Generate QR code with message
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(message.to_json())
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="white", back_color="black")

    # Paste QR code
    qr_size = min(width - 20, height - 80)
    qr_img = qr_img.resize((qr_size, qr_size))
    img.paste(qr_img, (10, 60))

    # Add text fallback
    intent_str = message.intent.value if hasattr(message.intent, 'value') else str(message.intent)
    draw.text((qr_size + 20, 60), f"Intent: {intent_str}", fill='yellow')
    draw.text((qr_size + 20, 80), f"From: {message.sender}", fill='green')
    draw.text((qr_size + 20, 100), f"To: {message.receiver}", fill='green')

    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def image_to_message(image_data: bytes) -> Optional[Message]:
    """
    Extract a message from a received SSTV image.
    """
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode as decode_qr
    except ImportError:
        # Fallback: try to parse as raw JSON
        try:
            return Message.from_json(image_data.decode())
        except:
            return None

    # Open image
    img = Image.open(BytesIO(image_data))

    # Try to decode QR code
    qr_codes = decode_qr(img)
    if qr_codes:
        try:
            json_data = qr_codes[0].data.decode()
            return Message.from_json(json_data)
        except:
            pass

    return None


def encode_message(message: Message, mode: str = "Robot36") -> bytes:
    """
    Encode a message as SSTV audio.

    Args:
        message: The Message to encode
        mode: SSTV mode (Robot36, Martin1, Scottie1, etc.)

    Returns:
        WAV audio data as bytes
    """
    # Convert message to image
    image_data = message_to_image(message)

    if HAS_SENSORY:
        # Use sensory SSTV encoder
        encoder = SSTVEncoder(mode=mode)
        return encoder.encode(image_data)
    else:
        # Fallback: use pysstv directly if available
        try:
            from PIL import Image
            from pysstv.color import Robot36
            from io import BytesIO
            import wave

            img = Image.open(BytesIO(image_data))
            sstv = Robot36(img, 44100, 16)

            buffer = BytesIO()
            sstv.write_wav(buffer)
            return buffer.getvalue()
        except ImportError:
            logger.error("No SSTV encoder available")
            # Return raw image data as fallback
            return image_data


def decode_message(audio_data: bytes) -> Optional[Message]:
    """
    Decode SSTV audio back to a message.

    Args:
        audio_data: WAV audio data

    Returns:
        Decoded Message or None if decoding fails
    """
    if HAS_SENSORY:
        decoder = SSTVDecoder()
        image_data = decoder.decode(audio_data)
        if image_data:
            return image_to_message(image_data)

    # TODO: Fallback SSTV decoder
    logger.warning("SSTV decoding not fully implemented")
    return None


def calculate_transmission_time(message: Message, mode: str = "Robot36") -> float:
    """
    Calculate estimated transmission time in seconds.

    Different SSTV modes have different speeds:
    - Robot36: ~36 seconds per frame
    - Martin1: ~114 seconds per frame
    - Scottie1: ~110 seconds per frame
    """
    mode_times = {
        "Robot36": 36.0,
        "Robot72": 72.0,
        "Martin1": 114.0,
        "Martin2": 58.0,
        "Scottie1": 110.0,
        "Scottie2": 71.0,
    }
    return mode_times.get(mode, 36.0)
