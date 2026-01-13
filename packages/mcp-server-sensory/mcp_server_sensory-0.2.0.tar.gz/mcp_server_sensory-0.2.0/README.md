# MCP Server Sensory

**Multi-Sensory AI Communication for Off-Grid Networks**

Part of the HumoticaOS McMurdo Off-Grid Communication Layer.

## The Vision

Make non-multimodal AI models "multi-sensitive" by encoding data across different sensory channels:

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR MESSAGE                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │  MORSE  │      │  BRAILLE │      │  SSTV*   │
   │  .--.   │      │  ⠓⠑⠇⠇⠕  │      │  [IMG]   │
   └────┬────┘      └────┬─────┘      └────┬─────┘
        ↓                ↓                 ↓
     AUDIO           VISUAL            AUDIO
     LIGHT          TACTILE           IMAGES
     VISUAL        PUNCHCARD          RADIO
```

*SSTV support coming soon (Robot36, Scottie, Martin modes)

## Installation

```bash
pip install mcp-server-sensory
```

With audio support:
```bash
pip install mcp-server-sensory[audio]
```

Full installation (all features):
```bash
pip install mcp-server-sensory[full]
```

## Features

### Morse Code
- Encode/decode text to Morse
- Multiple output formats: standard (.-), visual (█▄), binary (10)
- Timing data for audio/light generation
- Embeddable in images for visual transmission

### Braille
- Encode/decode text to Braille Unicode
- Generate punchcard patterns (ASCII art)
- Binary grid output for CNC/laser cutting
- **Physical audit trail** - punch into paper/card!

### Coming Soon
- **ggwave** - Ultrasonic data transmission (inaudible to humans)
- **SSTV** - Robot36, Scottie, Martin image modes
- **RTTY** - Classic radio teletype

## Usage

### As MCP Server

```json
{
  "mcpServers": {
    "sensory": {
      "command": "mcp-server-sensory"
    }
  }
}
```

### As Python Library

```python
from mcp_server_sensory import morse, braille

# Morse encoding
message = morse.encode("HELLO")
print(message)  # .... . .-.. .-.. ---

# Visual Morse (for images)
visual = morse.encode("SOS", morse.MorseFormat.VISUAL)
print(visual)  # ▄▄▄ ███ ▄▄▄

# Braille encoding
braille_msg = braille.encode("hello")
print(braille_msg)  # ⠓⠑⠇⠇⠕

# Punchcard pattern (for physical encoding)
pattern = braille.to_punchcard_pattern("hello")
print(pattern)
# ●○ ●○ ●○ ●○ ●○
# ●○ ○○ ●○ ●○ ●○
# ○○ ○○ ●○ ●○ ○○

# Binary grid (for CNC/laser)
grid = braille.to_binary_grid("hi")
print(grid)
# [[1, 0, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 0, 0, 0]]
```

## Use Cases

### Off-Grid AI Communication
Two Raspberry Pi's with speakers/mics can exchange messages via Morse audio - no internet required!

### Physical Audit Trail (TIBET Integration)
Encode TIBET tokens as Braille punchcards. Physical, tamper-evident, human and machine readable.

### Radio Communication
Ham radio operators can relay AI messages using Morse code or SSTV images.

### Accessibility
Braille output enables tactile reading of AI responses.

### Stealth Communication
ggwave ultrasonic mode transmits data above human hearing range.

## The Stack

```
┌─────────────────────────────────────┐
│  mcp-server-sensory                 │
│  (Morse, Braille, SSTV, ggwave)     │
├─────────────────────────────────────┤
│  I-Poll (AI messaging)              │
├─────────────────────────────────────┤
│  AINS (agent discovery)             │
├─────────────────────────────────────┤
│  TIBET (trust & provenance)         │
└─────────────────────────────────────┘
```

## Part of HumoticaOS

McMurdo Off-Grid Communication Layer

One love, one fAmIly! 💙
