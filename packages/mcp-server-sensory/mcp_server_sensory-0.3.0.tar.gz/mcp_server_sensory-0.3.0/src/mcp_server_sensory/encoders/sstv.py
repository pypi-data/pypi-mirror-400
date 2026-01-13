"""
SSTV (Slow Scan Television) Encoder/Decoder
Supports Robot36, Martin, Scottie, PD modes

Part of McMurdo fallback - visual communication when all else fails.
"Een 7B model krijgt opeens ogen" - Multi-modal bridge for small LLMs
"""

import io
import wave
import struct
from typing import Optional, Tuple, List
from pathlib import Path

# SSTV encoding
try:
    from pysstv.color import Robot36, MartinM1, MartinM2, ScottieS1, ScottieS2
    from pysstv.grayscale import Robot8BW, Robot24BW
    from PIL import Image, ImageDraw, ImageFont
    SSTV_AVAILABLE = True
except ImportError:
    SSTV_AVAILABLE = False

# SSTV mode configurations
SSTV_MODES = {
    "robot36": {"class": "Robot36", "color": True, "size": (320, 240), "time_sec": 36},
    "robot8bw": {"class": "Robot8BW", "color": False, "size": (160, 120), "time_sec": 8},
    "robot24bw": {"class": "Robot24BW", "color": False, "size": (160, 120), "time_sec": 24},
    "martin1": {"class": "MartinM1", "color": True, "size": (320, 256), "time_sec": 114},
    "martin2": {"class": "MartinM2", "color": True, "size": (320, 256), "time_sec": 58},
    "scottie1": {"class": "ScottieS1", "color": True, "size": (320, 256), "time_sec": 110},
    "scottie2": {"class": "ScottieS2", "color": True, "size": (320, 256), "time_sec": 71},
}


def get_available_modes() -> List[str]:
    """Get list of available SSTV modes"""
    return list(SSTV_MODES.keys())


def get_mode_info(mode: str) -> dict:
    """Get information about an SSTV mode"""
    if mode.lower() in SSTV_MODES:
        return SSTV_MODES[mode.lower()]
    return {"error": f"Unknown mode: {mode}. Available: {list(SSTV_MODES.keys())}"}


def text_to_image(text: str, size: Tuple[int, int] = (320, 240),
                  bg_color: str = "black", text_color: str = "white") -> Image.Image:
    """
    Convert text to an image for SSTV transmission.
    This is how we give "eyes" to text-only LLMs via McMurdo.

    Args:
        text: Text to embed in image (can be commands, ponskaart, status)
        size: Image dimensions (width, height)
        bg_color: Background color
        text_color: Text color

    Returns:
        PIL Image ready for SSTV encoding
    """
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use a monospace font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    except:
        font = ImageFont.load_default()

    # Word wrap text to fit image
    max_chars = size[0] // 10  # Approximate chars per line
    lines = []
    for paragraph in text.split('\n'):
        while len(paragraph) > max_chars:
            lines.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars:]
        lines.append(paragraph)

    # Draw text
    y_offset = 10
    for line in lines:
        draw.text((10, y_offset), line, fill=text_color, font=font)
        y_offset += 18
        if y_offset > size[1] - 20:
            break

    # Add McMurdo header
    draw.text((10, size[1] - 20), "McMurdo // Humotica", fill="gray", font=font)

    return img


def encode_image(image: Image.Image, mode: str = "robot36",
                 output_path: Optional[str] = None) -> bytes:
    """
    Encode an image to SSTV audio.

    Args:
        image: PIL Image to encode
        mode: SSTV mode (robot36, martin1, scottie1, etc.)
        output_path: Optional path to save WAV file

    Returns:
        WAV audio bytes
    """
    if not SSTV_AVAILABLE:
        raise ImportError("pysstv not installed. Run: pip install pysstv Pillow")

    mode_info = SSTV_MODES.get(mode.lower())
    if not mode_info:
        raise ValueError(f"Unknown mode: {mode}. Available: {list(SSTV_MODES.keys())}")

    # Resize image to mode requirements
    image = image.resize(mode_info["size"])

    # Convert to grayscale if needed
    if not mode_info["color"]:
        image = image.convert('L').convert('RGB')

    # Get the SSTV class
    sstv_class = {
        "Robot36": Robot36,
        "Robot8BW": Robot8BW,
        "Robot24BW": Robot24BW,
        "MartinM1": MartinM1,
        "MartinM2": MartinM2,
        "ScottieS1": ScottieS1,
        "ScottieS2": ScottieS2,
    }.get(mode_info["class"])

    if not sstv_class:
        raise ValueError(f"SSTV class not found for mode: {mode}")

    # Generate SSTV audio
    sstv = sstv_class(image, 44100, 16)

    # Write to buffer
    buffer = io.BytesIO()
    sstv.write_wav(buffer)
    audio_bytes = buffer.getvalue()

    # Optionally save to file
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)

    return audio_bytes


def encode_text(text: str, mode: str = "robot36",
                output_path: Optional[str] = None) -> bytes:
    """
    Encode text directly to SSTV audio.
    Convenience function combining text_to_image and encode_image.

    This is the "ponskaart" function - send commands visually!

    Args:
        text: Text to transmit (commands, auth tokens, status)
        mode: SSTV mode
        output_path: Optional path to save WAV file

    Returns:
        WAV audio bytes
    """
    mode_info = SSTV_MODES.get(mode.lower(), SSTV_MODES["robot36"])
    image = text_to_image(text, size=mode_info["size"])
    return encode_image(image, mode, output_path)


def encode_ponskaart(user_id: str, auth_token: str, command: str,
                     mode: str = "robot36", output_path: Optional[str] = None) -> bytes:
    """
    Create and encode a "ponskaart" (punch card) for McMurdo authentication.

    This is how we authenticate remotely when the network is down:
    - Encode credentials + command into SSTV
    - Transmit via radio
    - McMurdo receives, decodes, validates, executes

    Args:
        user_id: User identifier (e.g., "jasper")
        auth_token: Authentication token
        command: Command to execute
        mode: SSTV mode
        output_path: Optional path to save WAV

    Returns:
        WAV audio bytes containing the ponskaart
    """
    ponskaart_text = f"""===== PONSKAART =====
USER: {user_id}
AUTH: {auth_token[:16]}...
TIME: NOW
---
CMD: {command}
---
TIBET: AUDIT_REQUIRED
====================="""

    return encode_text(ponskaart_text, mode, output_path)


# Decoding functions (requires additional setup for full decode)
def decode_info() -> dict:
    """
    Information about SSTV decoding capabilities.
    Full decode requires audio input processing.
    """
    return {
        "status": "partial",
        "note": "Full SSTV decode requires audio input processing",
        "recommendation": "Use qsstv or direwolf for real-time decode",
        "integration": "McMurdo can receive decoded images and OCR the text",
        "available_modes": list(SSTV_MODES.keys())
    }


# Quick test
if __name__ == "__main__":
    print("🔧 Testing SSTV encoder...")

    # Test text to SSTV
    test_text = """SENTINEL STATUS
CPU: 45%
MEM: 62%
DISK: 78%
STATUS: ONLINE
CMD: READY"""

    audio = encode_text(test_text, "robot36", "/tmp/test_sstv.wav")
    print(f"✅ Generated SSTV audio: {len(audio)} bytes")
    print(f"✅ Saved to /tmp/test_sstv.wav")

    # Test ponskaart
    audio2 = encode_ponskaart("jasper", "abc123secret", "REBOOT SERVER",
                               "robot36", "/tmp/test_ponskaart.wav")
    print(f"✅ Generated ponskaart: {len(audio2)} bytes")
    print(f"✅ Saved to /tmp/test_ponskaart.wav")
