"""
Braille Encoder/Decoder
=======================

Converts text to Braille patterns and back.
Supports:
- Unicode Braille characters (⠁⠃⠉...)
- Dot matrix representation (for physical encoding)
- Binary grid (for punchcard generation)

BRAILLE AS PUNCHCARD:
Each Braille cell is a 2x3 grid of dots.
This can be physically punched into paper/card
creating a PHYSICAL AUDIT TRAIL readable by
both humans (trained) and machines (sensors)!

Part of HumoticaOS McMurdo Off-Grid Communication
"""

from typing import List, Tuple, Optional

# Braille dot positions:
# 1 4
# 2 5
# 3 6

# Grade 1 Braille (basic letter-by-letter)
BRAILLE_MAP = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
    ' ': '⠀',  # Braille space
    '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖', "'": '⠄',
    '-': '⠤', ':': '⠒', ';': '⠆', '(': '⠶', ')': '⠶',
}

# Number indicator (precedes numbers in proper Braille)
NUMBER_INDICATOR = '⠼'

# Reverse lookup
BRAILLE_TO_CHAR = {v: k for k, v in BRAILLE_MAP.items() if k.isalpha()}


def encode(text: str, include_number_indicators: bool = False) -> str:
    """
    Encode text to Braille Unicode characters.

    Args:
        text: Text to encode
        include_number_indicators: Add ⠼ before numbers (proper Braille)

    Returns:
        Braille string
    """
    text = text.lower()
    result = []
    in_number = False

    for char in text:
        if char.isdigit():
            if include_number_indicators and not in_number:
                result.append(NUMBER_INDICATOR)
                in_number = True
        else:
            in_number = False

        if char in BRAILLE_MAP:
            result.append(BRAILLE_MAP[char])
        else:
            result.append(char)  # Keep unknown chars

    return ''.join(result)


def decode(braille: str) -> str:
    """
    Decode Braille to text.

    Args:
        braille: Braille Unicode string

    Returns:
        Decoded text
    """
    result = []
    skip_next = False

    for char in braille:
        if skip_next:
            skip_next = False
            continue

        if char == NUMBER_INDICATOR:
            skip_next = False  # Next char is a number
            continue

        if char in BRAILLE_TO_CHAR:
            result.append(BRAILLE_TO_CHAR[char])
        elif char == '⠀':
            result.append(' ')
        else:
            result.append(char)

    return ''.join(result)


def to_dot_matrix(char: str) -> List[List[bool]]:
    """
    Convert a single Braille character to a 3x2 dot matrix.

    Returns:
        3x2 matrix where True = raised dot, False = flat

    Layout:
        [0][0] [0][1]   (dots 1, 4)
        [1][0] [1][1]   (dots 2, 5)
        [2][0] [2][1]   (dots 3, 6)
    """
    if char not in BRAILLE_MAP.values():
        if char in BRAILLE_MAP:
            char = BRAILLE_MAP[char]
        else:
            return [[False, False], [False, False], [False, False]]

    # Unicode Braille starts at U+2800
    # The pattern is encoded in the lower 8 bits
    code = ord(char) - 0x2800

    # Bit positions: 1=dot1, 2=dot2, 4=dot3, 8=dot4, 16=dot5, 32=dot6
    matrix = [
        [bool(code & 1), bool(code & 8)],    # dots 1, 4
        [bool(code & 2), bool(code & 16)],   # dots 2, 5
        [bool(code & 4), bool(code & 32)],   # dots 3, 6
    ]

    return matrix


def to_punchcard_pattern(text: str, cell_width: int = 4, cell_height: int = 6) -> str:
    """
    Convert text to ASCII art punchcard pattern.

    This pattern can be:
    1. Printed and physically punched
    2. Read by optical sensors
    3. Used as visual encoding in images

    Args:
        text: Text to encode
        cell_width: Width of each Braille cell in chars
        cell_height: Height of each cell (must be multiple of 3)

    Returns:
        ASCII art string representing punchcard
    """
    braille = encode(text)
    matrices = [to_dot_matrix(char) for char in braille]

    dot_char = '●'
    empty_char = '○'
    row_scale = cell_height // 3
    col_scale = cell_width // 2

    lines = [[] for _ in range(cell_height)]

    for matrix in matrices:
        for row_idx, row in enumerate(matrix):
            for scale in range(row_scale):
                line_idx = row_idx * row_scale + scale
                for col_idx, dot in enumerate(row):
                    char = dot_char if dot else empty_char
                    lines[line_idx].extend([char] * col_scale)
                lines[line_idx].append(' ')  # Cell separator

    return '\n'.join([''.join(line) for line in lines])


def to_binary_grid(text: str) -> List[List[int]]:
    """
    Convert text to binary grid for machine reading.

    Perfect for:
    - CNC/laser punchcard creation
    - QR-like machine reading
    - Physical TIBET audit tokens

    Returns:
        2D list of 0s and 1s
    """
    braille = encode(text)
    matrices = [to_dot_matrix(char) for char in braille]

    # Combine all matrices horizontally
    if not matrices:
        return []

    grid = [[] for _ in range(3)]
    for matrix in matrices:
        for row_idx, row in enumerate(matrix):
            grid[row_idx].extend([int(dot) for dot in row])
            grid[row_idx].append(0)  # Separator

    return grid


def from_binary_grid(grid: List[List[int]]) -> str:
    """
    Decode a binary grid back to text.
    """
    if not grid or len(grid) != 3:
        return ""

    # Find cell boundaries (columns of zeros)
    width = len(grid[0])
    cells = []
    cell_start = 0

    for col in range(width):
        if all(grid[row][col] == 0 for row in range(3)):
            if col > cell_start:
                # Extract cell
                cell_bits = []
                for row in range(3):
                    cell_bits.append(grid[row][cell_start:col])
                cells.append(cell_bits)
            cell_start = col + 1

    # Convert cells back to Braille
    result = []
    for cell in cells:
        if len(cell[0]) >= 2:
            code = 0
            if cell[0][0]: code |= 1
            if cell[1][0]: code |= 2
            if cell[2][0]: code |= 4
            if len(cell[0]) > 1:
                if cell[0][1]: code |= 8
                if cell[1][1]: code |= 16
                if cell[2][1]: code |= 32

            braille_char = chr(0x2800 + code)
            result.append(braille_char)

    return decode(''.join(result))


# Quick test
if __name__ == "__main__":
    test = "hello"
    print(f"Original: {test}")
    print(f"Braille: {encode(test)}")
    print(f"Decoded: {decode(encode(test))}")
    print(f"\nPunchcard pattern:")
    print(to_punchcard_pattern(test))
    print(f"\nBinary grid: {to_binary_grid(test)}")
