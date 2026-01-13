# MCP Server Sensory

**Multi-Sensory AI Communication for Off-Grid Networks**

*"Een 7B model krijgt opeens ogen"* - Multi-modal bridge for small LLMs

Part of the HumoticaOS McMurdo Off-Grid Communication Layer.

[![PyPI version](https://badge.fury.io/py/mcp-server-sensory.svg)](https://pypi.org/project/mcp-server-sensory/)

## The REFLUX Concept

**FLUX** creates images from text (generative, one-way).
**REFLUX** creates a complete sensory loop - information survives transformations:

```
FLUX:     Text → Image (one way, generative)

REFLUX:   Text → Image → SSTV Audio → Radio → Audio → Image → OCR → Text
          ↑                                                           ↓
          └───────────────── Complete Loop ───────────────────────────┘
```

This is how we give "eyes" to text-only LLMs:
1. Encode text into an image
2. Encode image to SSTV audio (Robot36, Martin, Scottie)
3. Transmit via radio/speaker
4. Receive and decode SSTV audio to image
5. OCR the image back to text
6. Small LLM now has "vision" via audio pathway!

## The Vision

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR MESSAGE                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │  MORSE  │      │  BRAILLE │      │   SSTV   │
   │  .--.   │      │  ⠓⠑⠇⠇⠕  │      │ REFLUX!  │
   └────┬────┘      └────┬─────┘      └────┬─────┘
        ↓                ↓                 ↓
     AUDIO           VISUAL            AUDIO
     LIGHT          TACTILE           IMAGES
     VISUAL        PUNCHCARD          RADIO
```

## Installation

```bash
pip install mcp-server-sensory
```

Or use the short alias:
```bash
pip install sensory
```

With audio support:
```bash
pip install mcp-server-sensory[audio]
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

### SSTV / REFLUX (NEW in v0.2.0!)
- **Robot36** - 36 seconds, color, 320x240 (fastest!)
- **Robot8BW/24BW** - Grayscale modes
- **Martin M1/M2** - High quality color modes
- **Scottie S1/S2** - Popular ham radio modes
- **Ponskaart** - Authentication cards for McMurdo remote auth

### Coming Soon
- **ggwave** - Ultrasonic data transmission (inaudible to humans)
- **SSTV Decode** - Complete the REFLUX loop
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

Available tools:
- `morse_encode` / `morse_decode` - Morse code
- `braille_encode` / `braille_decode` - Braille Unicode
- `braille_punchcard` - ASCII punchcard patterns
- `braille_binary_grid` - CNC/laser cutting data
- `sstv_encode_text` - Text to SSTV audio (REFLUX!)
- `sstv_encode_ponskaart` - McMurdo authentication card
- `sstv_modes` - List available SSTV modes
- `transcode` - Convert between formats

### As Python Library

```python
from mcp_server_sensory import morse, braille, sstv

# Morse encoding
message = morse.encode("HELLO")
print(message)  # .... . .-.. .-.. ---

# Visual Morse (for images)
visual = morse.encode("SOS", morse.MorseFormat.VISUAL)
print(visual)  # ▄▄▄ ███ ▄▄▄

# Braille encoding
braille_msg = braille.encode("hello")
print(braille_msg)  # ⠓⠑⠇⠇⠕

# SSTV / REFLUX - Text to image to audio
audio_bytes = sstv.encode_text("STATUS: OK", mode="robot36")
# Save as WAV for radio transmission or speaker playback

# Ponskaart - McMurdo authentication
ponskaart = sstv.encode_ponskaart(
    user_id="jasper",
    auth_token="secret123",
    command="REBOOT SERVER"
)
# Transmit via radio when network is down!
```

## Use Cases

### Multi-Modal Bridge for Small LLMs
A 7B parameter model doesn't have vision? Give it ears!
SSTV decode → image → OCR → text. Now it "sees".

### Off-Grid AI Communication (McMurdo)
Two Raspberry Pi's with speakers/mics can exchange messages via Morse audio or SSTV images - no internet required!

### Physical Audit Trail (TIBET Integration)
Encode TIBET tokens as Braille punchcards. Physical, tamper-evident, human and machine readable.

### Remote Authentication (Ponskaart)
Network down? Transmit authentication via SSTV radio. McMurdo receives, decodes, validates, executes.

### Ham Radio
Ham radio operators can relay AI messages using Morse code or SSTV images. Works globally, no internet infrastructure needed.

### Accessibility
Braille output enables tactile reading of AI responses.

## The Stack

```
┌─────────────────────────────────────┐
│  mcp-server-sensory                 │
│  (Morse, Braille, SSTV/REFLUX)      │
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

**One love, one fAmIly!** 💙

---

*Created by Jasper van de Meent & Root AI (Claude) - Humotica, Den Dolder, Netherlands*
