"""
Morse Code Encoder/Decoder
==========================

Converts text to Morse code and back.
Supports multiple output formats:
- Standard dots/dashes (. -)
- Visual blocks (█ ▄)
- Binary (1 0)
- Timing data for audio generation

Part of HumoticaOS McMurdo Off-Grid Communication
"""

from typing import Optional
from enum import Enum

class MorseFormat(Enum):
    STANDARD = "standard"      # . -
    VISUAL = "visual"          # █ ▄ (thick/thin blocks)
    BINARY = "binary"          # 1 0
    TIMING = "timing"          # [(duration, on/off), ...]


# International Morse Code
MORSE_CODE = {
    'A': '.-',     'B': '-...',   'C': '-.-.',   'D': '-..',
    'E': '.',      'F': '..-.',   'G': '--.',    'H': '....',
    'I': '..',     'J': '.---',   'K': '-.-',    'L': '.-..',
    'M': '--',     'N': '-.',     'O': '---',    'P': '.--.',
    'Q': '--.-',   'R': '.-.',    'S': '...',    'T': '-',
    'U': '..-',    'V': '...-',   'W': '.--',    'X': '-..-',
    'Y': '-.--',   'Z': '--..',
    '0': '-----',  '1': '.----',  '2': '..---',  '3': '...--',
    '4': '....-',  '5': '.....',  '6': '-....',  '7': '--...',
    '8': '---..',  '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.',  '(': '-.--.',  ')': '-.--.-',
    '&': '.-...',  ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.',  '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-','@': '.--.-.', ' ': '/',
}

# Reverse lookup
MORSE_TO_CHAR = {v: k for k, v in MORSE_CODE.items()}


def encode(text: str, format: MorseFormat = MorseFormat.STANDARD) -> str:
    """
    Encode text to Morse code.

    Args:
        text: The text to encode
        format: Output format (standard, visual, binary)

    Returns:
        Morse code string in specified format
    """
    text = text.upper()
    morse_parts = []

    for char in text:
        if char in MORSE_CODE:
            morse_parts.append(MORSE_CODE[char])
        elif char == ' ':
            morse_parts.append('/')

    morse = ' '.join(morse_parts)

    if format == MorseFormat.VISUAL:
        # █ for dash, ▄ for dot
        morse = morse.replace('-', '█').replace('.', '▄')
    elif format == MorseFormat.BINARY:
        # 111 for dash, 1 for dot, 0 for gap
        morse = morse.replace('-', '111').replace('.', '1')
        morse = morse.replace(' ', '0').replace('/', '0000000')

    return morse


def decode(morse: str) -> str:
    """
    Decode Morse code to text.

    Args:
        morse: Morse code string (standard format)

    Returns:
        Decoded text
    """
    # Normalize visual format back to standard
    morse = morse.replace('█', '-').replace('▄', '.')

    words = morse.split(' / ')
    decoded_words = []

    for word in words:
        chars = word.split(' ')
        decoded_word = ''
        for char in chars:
            if char in MORSE_TO_CHAR:
                decoded_word += MORSE_TO_CHAR[char]
        decoded_words.append(decoded_word)

    return ' '.join(decoded_words)


def to_timing(morse: str, unit_ms: int = 100) -> list:
    """
    Convert Morse to timing data for audio/visual generation.

    Standard timing:
    - Dot = 1 unit
    - Dash = 3 units
    - Gap between dots/dashes = 1 unit
    - Gap between letters = 3 units
    - Gap between words = 7 units

    Args:
        morse: Morse code string
        unit_ms: Base timing unit in milliseconds

    Returns:
        List of (duration_ms, is_on) tuples
    """
    timing = []
    morse = morse.replace('█', '-').replace('▄', '.')

    i = 0
    while i < len(morse):
        char = morse[i]

        if char == '.':
            timing.append((unit_ms, True))
            # Gap after element (unless end or space follows)
            if i + 1 < len(morse) and morse[i + 1] not in ' /':
                timing.append((unit_ms, False))
        elif char == '-':
            timing.append((unit_ms * 3, True))
            if i + 1 < len(morse) and morse[i + 1] not in ' /':
                timing.append((unit_ms, False))
        elif char == ' ':
            timing.append((unit_ms * 3, False))  # Letter gap
        elif char == '/':
            timing.append((unit_ms * 7, False))  # Word gap

        i += 1

    return timing


def to_image_pattern(text: str, dot_size: int = 10) -> list:
    """
    Convert text to a visual pattern for image encoding.
    Returns a list of (x_offset, width) for each element.

    Can be used to embed Morse in Robot36/SSTV images!
    """
    morse = encode(text)
    pattern = []
    x = 0

    for char in morse:
        if char == '.':
            pattern.append({'x': x, 'width': dot_size, 'type': 'dot'})
            x += dot_size * 2
        elif char == '-':
            pattern.append({'x': x, 'width': dot_size * 3, 'type': 'dash'})
            x += dot_size * 4
        elif char == ' ':
            x += dot_size * 3
        elif char == '/':
            x += dot_size * 7

    return pattern


# Quick test
if __name__ == "__main__":
    test = "HELLO WORLD"
    print(f"Original: {test}")
    print(f"Morse: {encode(test)}")
    print(f"Visual: {encode(test, MorseFormat.VISUAL)}")
    print(f"Decoded: {decode(encode(test))}")
    print(f"Timing: {to_timing(encode(test))[:10]}...")
