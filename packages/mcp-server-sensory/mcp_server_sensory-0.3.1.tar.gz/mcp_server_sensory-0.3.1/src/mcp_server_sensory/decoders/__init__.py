"""
Sensory Decoders - Transform sensory data back to text

McMurdo Off-Grid Communication - REFLUX:
- SSTV: Audio → Image → OCR → Text (complete the loop!)
"""

from . import sstv

__all__ = ["sstv"]
