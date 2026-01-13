"""
SSTV (Slow Scan Television) Decoder
====================================

Part of REFLUX - The complete sensory loop.

REFLUX Flow:
    Text → Image → SSTV Audio → Radio → Audio → Image → OCR → Text

This module provides:
    1. SSTV signal detection (VIS code identification)
    2. Integration with external decoders (qsstv)
    3. OCR for text extraction from decoded images

"Een 7B model krijgt opeens ogen" - Multi-modal bridge for small LLMs
"""

import io
import wave
import struct
import subprocess
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import tempfile

# Try to import numpy/scipy for audio processing
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Try to import PIL for image handling and OCR
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# SSTV VIS (Vertical Interval Signaling) codes
# These identify the mode at the start of transmission
VIS_CODES = {
    8: "Robot36",
    12: "Robot72",
    40: "Martin M1",
    44: "Martin M2",
    56: "Scottie S1",
    60: "Scottie S2",
    # Add more as needed
}

# SSTV frequency constants
SSTV_FREQUENCIES = {
    "leader_tone": 1900,  # Hz
    "break": 1200,  # Hz
    "vis_start": 1200,  # Hz
    "vis_bit_0": 1300,  # Hz
    "vis_bit_1": 1100,  # Hz
    "sync": 1200,  # Hz
    "black": 1500,  # Hz
    "white": 2300,  # Hz
}


def detect_sstv_signal(audio_data: bytes, sample_rate: int = 44100) -> Dict[str, Any]:
    """
    Detect if audio contains an SSTV signal.

    Looks for:
    - Leader tone (1900 Hz)
    - VIS code pattern

    Args:
        audio_data: Raw audio bytes (mono, 16-bit PCM)
        sample_rate: Sample rate in Hz

    Returns:
        Dict with detection results:
        - detected: bool
        - mode: str (if VIS code found)
        - confidence: float (0.0-1.0)
    """
    if not NUMPY_AVAILABLE:
        return {
            "detected": False,
            "error": "numpy not installed",
            "note": "Install numpy for signal detection"
        }

    # Convert bytes to numpy array
    samples = np.frombuffer(audio_data, dtype=np.int16)
    samples = samples.astype(np.float32) / 32768.0

    # Simple frequency detection using FFT
    # Look for 1900 Hz leader tone in first 2 seconds
    chunk_size = min(len(samples), sample_rate * 2)
    chunk = samples[:chunk_size]

    # FFT
    fft = np.fft.fft(chunk)
    freqs = np.fft.fftfreq(len(chunk), 1/sample_rate)

    # Find dominant frequency
    magnitude = np.abs(fft)
    positive_freqs = freqs[:len(freqs)//2]
    positive_magnitude = magnitude[:len(magnitude)//2]

    # Look for peak near 1900 Hz (leader tone)
    leader_range = (1850, 1950)
    leader_indices = np.where((positive_freqs >= leader_range[0]) &
                               (positive_freqs <= leader_range[1]))[0]

    if len(leader_indices) > 0:
        leader_power = np.max(positive_magnitude[leader_indices])
        total_power = np.sum(positive_magnitude)
        confidence = float(leader_power / total_power) if total_power > 0 else 0

        if confidence > 0.05:  # At least 5% of power in leader tone
            return {
                "detected": True,
                "confidence": min(confidence * 10, 1.0),  # Scale up
                "mode": "unknown",  # Would need VIS decode for mode
                "note": "Leader tone detected, likely SSTV signal"
            }

    return {
        "detected": False,
        "confidence": 0.0,
        "note": "No SSTV signal detected"
    }


def decode_with_external(audio_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Decode SSTV using external tools (qsstv, msstv).

    This is the recommended approach for production use.

    Args:
        audio_path: Path to WAV file
        output_dir: Directory for decoded image (default: temp)

    Returns:
        Dict with decode results
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="sstv_decode_")

    # Try qsstv (Linux)
    try:
        result = subprocess.run(
            ["qsstv", "--decode", audio_path, "--output", output_dir],
            capture_output=True,
            timeout=120  # SSTV can take up to 2 minutes
        )
        if result.returncode == 0:
            # Look for output image
            images = list(Path(output_dir).glob("*.png"))
            if images:
                return {
                    "status": "success",
                    "decoder": "qsstv",
                    "image_path": str(images[0]),
                    "output_dir": output_dir
                }
    except FileNotFoundError:
        pass  # qsstv not installed
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Decode timeout"}

    return {
        "status": "not_available",
        "error": "No SSTV decoder found",
        "recommendation": "Install qsstv: sudo apt install qsstv",
        "manual_decode": "Open the audio in qsstv GUI or use online decoder"
    }


def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """
    Extract text from decoded SSTV image using OCR.

    This completes the REFLUX loop:
    Text → Image → SSTV → Image → OCR → Text

    Args:
        image_path: Path to decoded SSTV image

    Returns:
        Dict with extracted text
    """
    if not PIL_AVAILABLE:
        return {
            "status": "error",
            "error": "PIL not installed",
            "note": "Install Pillow for OCR"
        }

    # Try pytesseract for OCR
    try:
        import pytesseract

        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        return {
            "status": "success",
            "text": text.strip(),
            "image_path": image_path,
            "note": "REFLUX complete! Text extracted from SSTV image"
        }

    except ImportError:
        return {
            "status": "partial",
            "image_path": image_path,
            "error": "pytesseract not installed",
            "recommendation": "pip install pytesseract && apt install tesseract-ocr"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "image_path": image_path
        }


def reflux_decode(audio_input, sample_rate: int = 44100) -> Dict[str, Any]:
    """
    Complete REFLUX decode: Audio → Image → Text

    This is the main entry point for REFLUX decoding.

    Args:
        audio_input: SSTV audio - either bytes (WAV data) or str (file path)
        sample_rate: Audio sample rate (used when passing bytes)

    Returns:
        Dict with full decode results including extracted text
    """
    result = {
        "status": "processing",
        "steps": []
    }

    # Handle both file path and bytes input
    if isinstance(audio_input, str):
        # It's a file path
        audio_path = audio_input
        # Read the audio data for signal detection
        try:
            with wave.open(audio_path, 'rb') as wav:
                sample_rate = wav.getframerate()
                audio_data = wav.readframes(wav.getnframes())
        except Exception as e:
            return {"status": "error", "error": f"Could not read audio file: {e}"}
    elif isinstance(audio_input, bytes):
        audio_data = audio_input
        # Save to temp file for external decoder
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            with wave.open(f.name, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(audio_data)
            audio_path = f.name
    else:
        return {"status": "error", "error": "audio_input must be bytes or file path string"}

    # Step 1: Detect signal (informational - external decoders do their own detection)
    detection = detect_sstv_signal(audio_data, sample_rate)
    result["steps"].append({"step": "detection", "result": detection})

    # Note: We continue even if detection fails - external decoders are more reliable

    # Step 2: Decode with external tool
    decode_result = decode_with_external(audio_path)
    result["steps"].append({"step": "decode", "result": decode_result})

    if decode_result.get("status") != "success":
        result["status"] = "decode_failed"
        result["note"] = "External decoder not available or failed"
        result["audio_path"] = audio_path
        return result

    # Step 4: OCR
    image_path = decode_result.get("image_path")
    if image_path:
        ocr_result = extract_text_from_image(image_path)
        result["steps"].append({"step": "ocr", "result": ocr_result})

        if ocr_result.get("status") == "success":
            result["status"] = "success"
            result["text"] = ocr_result.get("text", "")
            result["image_path"] = image_path
            result["note"] = "REFLUX complete! Full sensory loop achieved"
        else:
            result["status"] = "partial"
            result["image_path"] = image_path
            result["note"] = "Image decoded, OCR failed - see image_path"

    return result


def get_decoder_info() -> Dict[str, Any]:
    """
    Get information about available SSTV decode capabilities.
    """
    info = {
        "signal_detection": NUMPY_AVAILABLE,
        "image_processing": PIL_AVAILABLE,
        "external_decoders": [],
        "ocr_available": False,
        "supported_modes": list(VIS_CODES.values())
    }

    # Check for external decoders
    for decoder in ["qsstv", "msstv", "slowrx"]:
        try:
            subprocess.run([decoder, "--version"], capture_output=True, timeout=5)
            info["external_decoders"].append(decoder)
        except:
            pass

    # Check for OCR
    try:
        import pytesseract
        info["ocr_available"] = True
    except ImportError:
        pass

    info["reflux_ready"] = (
        info["signal_detection"] and
        len(info["external_decoders"]) > 0 and
        info["ocr_available"]
    )

    if not info["reflux_ready"]:
        info["missing"] = []
        if not info["signal_detection"]:
            info["missing"].append("numpy (pip install numpy)")
        if not info["external_decoders"]:
            info["missing"].append("qsstv (apt install qsstv)")
        if not info["ocr_available"]:
            info["missing"].append("pytesseract (pip install pytesseract)")

    return info


# Quick test
if __name__ == "__main__":
    print("🔧 SSTV Decoder Info")
    print("=" * 40)

    info = get_decoder_info()
    print(f"Signal detection: {'✅' if info['signal_detection'] else '❌'}")
    print(f"Image processing: {'✅' if info['image_processing'] else '❌'}")
    print(f"External decoders: {info['external_decoders'] or 'None'}")
    print(f"OCR available: {'✅' if info['ocr_available'] else '❌'}")
    print(f"REFLUX ready: {'✅' if info['reflux_ready'] else '❌'}")

    if info.get("missing"):
        print(f"\nMissing components:")
        for m in info["missing"]:
            print(f"  - {m}")
