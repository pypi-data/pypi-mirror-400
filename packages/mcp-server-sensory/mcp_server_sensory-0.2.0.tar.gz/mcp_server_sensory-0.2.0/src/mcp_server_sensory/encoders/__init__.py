"""
Sensory Encoders - Transform data between modalities

McMurdo Off-Grid Communication:
- Morse: Audio/visual/tactile signaling
- Braille: Visual/tactile/punchcard patterns
- SSTV: Visual data via audio (Robot36, Martin, Scottie)
"""

from . import morse
from . import braille
from . import sstv

__all__ = ["morse", "braille", "sstv"]
