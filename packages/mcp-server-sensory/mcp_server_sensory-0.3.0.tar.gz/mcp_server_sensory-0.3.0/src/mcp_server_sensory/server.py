"""
MCP Server Sensory - Multi-Sensory AI Communication Server
==========================================================

Provides tools for encoding/decoding messages across
multiple sensory modalities for off-grid AI communication.

Part of HumoticaOS McMurdo Off-Grid Communication Layer.
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .encoders import morse, braille, sstv
from .decoders import sstv as sstv_decoder
import base64

# Create server instance
server = Server("sensory")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available sensory tools."""
    return [
        Tool(
            name="morse_encode",
            description="Encode text to Morse code. Formats: standard (.-), visual (█▄), binary (10)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode"},
                    "format": {
                        "type": "string",
                        "enum": ["standard", "visual", "binary"],
                        "default": "standard",
                        "description": "Output format"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="morse_decode",
            description="Decode Morse code back to text",
            inputSchema={
                "type": "object",
                "properties": {
                    "morse": {"type": "string", "description": "Morse code to decode"}
                },
                "required": ["morse"]
            }
        ),
        Tool(
            name="morse_timing",
            description="Get timing data for Morse audio/light generation",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"},
                    "unit_ms": {"type": "integer", "default": 100, "description": "Base time unit in milliseconds"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="braille_encode",
            description="Encode text to Braille Unicode characters",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="braille_decode",
            description="Decode Braille back to text",
            inputSchema={
                "type": "object",
                "properties": {
                    "braille": {"type": "string", "description": "Braille text to decode"}
                },
                "required": ["braille"]
            }
        ),
        Tool(
            name="braille_punchcard",
            description="Generate ASCII punchcard pattern from text - can be physically punched for audit trail!",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"},
                    "cell_width": {"type": "integer", "default": 4, "description": "Width of each cell"},
                    "cell_height": {"type": "integer", "default": 6, "description": "Height of each cell"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="braille_binary_grid",
            description="Generate binary grid for machine-readable punchcard or CNC/laser cutting",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="transcode",
            description="Convert between different sensory encodings",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input data"},
                    "from_format": {
                        "type": "string",
                        "enum": ["text", "morse", "braille"],
                        "description": "Source format"
                    },
                    "to_format": {
                        "type": "string",
                        "enum": ["text", "morse", "braille", "morse_visual", "punchcard"],
                        "description": "Target format"
                    }
                },
                "required": ["input", "from_format", "to_format"]
            }
        ),
        # SSTV Tools - "Een 7B model krijgt opeens ogen"
        Tool(
            name="sstv_encode_text",
            description="Encode text to SSTV audio (Robot36/Martin/Scottie). Returns base64 WAV. Multi-modal bridge for small LLMs!",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to encode into image then SSTV audio"},
                    "mode": {
                        "type": "string",
                        "enum": ["robot36", "robot8bw", "robot24bw", "martin1", "martin2", "scottie1", "scottie2"],
                        "default": "robot36",
                        "description": "SSTV mode (robot36 is fastest)"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="sstv_encode_ponskaart",
            description="Create authenticated ponskaart (punch card) for McMurdo remote authentication via SSTV",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "auth_token": {"type": "string", "description": "Authentication token"},
                    "command": {"type": "string", "description": "Command to execute remotely"},
                    "mode": {
                        "type": "string",
                        "enum": ["robot36", "robot8bw", "robot24bw", "martin1", "martin2", "scottie1", "scottie2"],
                        "default": "robot36",
                        "description": "SSTV mode"
                    }
                },
                "required": ["user_id", "auth_token", "command"]
            }
        ),
        Tool(
            name="sstv_modes",
            description="List available SSTV modes with their specifications",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # SSTV Decode - Complete the REFLUX loop!
        Tool(
            name="sstv_detect",
            description="Detect if audio contains an SSTV signal. First step of REFLUX decode.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_base64": {"type": "string", "description": "Base64 encoded WAV audio"}
                },
                "required": ["audio_base64"]
            }
        ),
        Tool(
            name="sstv_decoder_info",
            description="Get SSTV decoder capabilities and REFLUX readiness status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="reflux_decode",
            description="Complete REFLUX decode: SSTV Audio → Image → OCR → Text. Gives small LLMs 'eyes' via audio!",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_base64": {"type": "string", "description": "Base64 encoded SSTV WAV audio"}
                },
                "required": ["audio_base64"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "morse_encode":
        text = arguments["text"]
        fmt = arguments.get("format", "standard")
        format_enum = {
            "standard": morse.MorseFormat.STANDARD,
            "visual": morse.MorseFormat.VISUAL,
            "binary": morse.MorseFormat.BINARY
        }.get(fmt, morse.MorseFormat.STANDARD)

        result = morse.encode(text, format_enum)
        return [TextContent(type="text", text=result)]

    elif name == "morse_decode":
        morse_code = arguments["morse"]
        result = morse.decode(morse_code)
        return [TextContent(type="text", text=result)]

    elif name == "morse_timing":
        text = arguments["text"]
        unit_ms = arguments.get("unit_ms", 100)
        morse_code = morse.encode(text)
        timing = morse.to_timing(morse_code, unit_ms)
        return [TextContent(type="text", text=json.dumps(timing))]

    elif name == "braille_encode":
        text = arguments["text"]
        result = braille.encode(text)
        return [TextContent(type="text", text=result)]

    elif name == "braille_decode":
        braille_text = arguments["braille"]
        result = braille.decode(braille_text)
        return [TextContent(type="text", text=result)]

    elif name == "braille_punchcard":
        text = arguments["text"]
        cell_width = arguments.get("cell_width", 4)
        cell_height = arguments.get("cell_height", 6)
        result = braille.to_punchcard_pattern(text, cell_width, cell_height)
        return [TextContent(type="text", text=result)]

    elif name == "braille_binary_grid":
        text = arguments["text"]
        grid = braille.to_binary_grid(text)
        return [TextContent(type="text", text=json.dumps(grid))]

    elif name == "transcode":
        input_data = arguments["input"]
        from_fmt = arguments["from_format"]
        to_fmt = arguments["to_format"]

        # First convert to text
        if from_fmt == "morse":
            text = morse.decode(input_data)
        elif from_fmt == "braille":
            text = braille.decode(input_data)
        else:
            text = input_data

        # Then convert to target
        if to_fmt == "morse":
            result = morse.encode(text)
        elif to_fmt == "morse_visual":
            result = morse.encode(text, morse.MorseFormat.VISUAL)
        elif to_fmt == "braille":
            result = braille.encode(text)
        elif to_fmt == "punchcard":
            result = braille.to_punchcard_pattern(text)
        else:
            result = text

        return [TextContent(type="text", text=result)]

    # SSTV Tools
    elif name == "sstv_encode_text":
        text = arguments["text"]
        mode = arguments.get("mode", "robot36")
        try:
            audio_bytes = sstv.encode_text(text, mode)
            audio_b64 = base64.b64encode(audio_bytes).decode()
            result = {
                "status": "success",
                "mode": mode,
                "text_length": len(text),
                "audio_bytes": len(audio_bytes),
                "audio_base64": audio_b64[:100] + "...[truncated]",
                "full_audio_base64": audio_b64,
                "note": "Multi-modal bridge: text -> image -> SSTV audio"
            }
            return [TextContent(type="text", text=json.dumps(result))]
        except ImportError as e:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": "pysstv not installed. Run: pip install mcp-server-sensory[sstv]"
            }))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"status": "error", "error": str(e)}))]

    elif name == "sstv_encode_ponskaart":
        user_id = arguments["user_id"]
        auth_token = arguments["auth_token"]
        command = arguments["command"]
        mode = arguments.get("mode", "robot36")
        try:
            audio_bytes = sstv.encode_ponskaart(user_id, auth_token, command, mode)
            audio_b64 = base64.b64encode(audio_bytes).decode()
            result = {
                "status": "success",
                "mode": mode,
                "ponskaart": {
                    "user": user_id,
                    "command": command,
                    "auth_prefix": auth_token[:8] + "..."
                },
                "audio_bytes": len(audio_bytes),
                "full_audio_base64": audio_b64,
                "note": "McMurdo authentication ponskaart - transmit via radio when network fails"
            }
            return [TextContent(type="text", text=json.dumps(result))]
        except ImportError as e:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": "pysstv not installed. Run: pip install mcp-server-sensory[sstv]"
            }))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"status": "error", "error": str(e)}))]

    elif name == "sstv_modes":
        modes = sstv.get_available_modes() if hasattr(sstv, 'get_available_modes') else []
        mode_info = {}
        for m in modes:
            info = sstv.get_mode_info(m) if hasattr(sstv, 'get_mode_info') else {}
            mode_info[m] = info
        result = {
            "status": "success",
            "available_modes": modes,
            "mode_details": mode_info,
            "note": "SSTV = Slow Scan Television. Used by ham radio operators to send images over audio."
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    # SSTV Decode / REFLUX tools
    elif name == "sstv_detect":
        audio_b64 = arguments["audio_base64"]
        try:
            audio_bytes = base64.b64decode(audio_b64)
            result = sstv_decoder.detect_sstv_signal(audio_bytes)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": str(e)
            }))]

    elif name == "sstv_decoder_info":
        result = sstv_decoder.get_decoder_info()
        result["concept"] = "REFLUX: Text → Image → SSTV Audio → Radio → Audio → Image → OCR → Text"
        result["purpose"] = "Give 'eyes' to text-only LLMs via audio pathway"
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "reflux_decode":
        audio_b64 = arguments["audio_base64"]
        try:
            audio_bytes = base64.b64decode(audio_b64)
            result = sstv_decoder.reflux_decode(audio_bytes)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({
                "status": "error",
                "error": str(e),
                "note": "REFLUX decode failed. Check audio format (WAV, mono, 16-bit)"
            }))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def main():
    """Run the MCP server."""
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
