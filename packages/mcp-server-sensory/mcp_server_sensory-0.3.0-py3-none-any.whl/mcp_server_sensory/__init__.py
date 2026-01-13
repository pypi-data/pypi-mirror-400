"""
MCP Server Sensory - Multi-Sensory AI Communication
====================================================

Off-grid communication for AI systems using:
- Morse code (audio/visual/tactile)
- Braille (visual/tactile/punchcard)
- SSTV/Robot36 (images via audio) - "Een 7B model krijgt opeens ogen"
- ggwave (ultrasonic data) - future

Part of HumoticaOS McMurdo Off-Grid Communication Layer.

Usage:
    from mcp_server_sensory import morse, braille, sstv

    # Encode message to Morse
    morse_msg = morse.encode("HELLO")  # .... . .-.. .-.. ---

    # Encode to Braille
    braille_msg = braille.encode("hello")  # ⠓⠑⠇⠇⠕

    # Encode text to SSTV audio (Robot36)
    audio = sstv.encode_text("STATUS: OK")  # WAV bytes

    # Create authenticated ponskaart via SSTV
    ponskaart = sstv.encode_ponskaart("jasper", "token123", "REBOOT")

One love, one fAmIly!
"""

__version__ = "0.3.0"

from .encoders import morse, braille, sstv
from .decoders import sstv as sstv_decoder

__all__ = ["morse", "braille", "sstv", "sstv_decoder", "__version__"]
