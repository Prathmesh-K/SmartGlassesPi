"""Minimal SmartGlasses entry point.

This module exposes a helper that performs OCR on an image and converts the
detected text to speech using Piper, saving the result as a WAV file. A thin
CLI wrapper is provided for manual testing.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from OCR.piOCR import detect_text
from TTS.piper_tts import initialize_piper_voice, save_wav, synthesise_to_memory

DEFAULT_MODEL_PATH = Path("TTS/en_US-amy-low.onnx")
DEFAULT_CONFIG_PATH = Path("TTS/en_US-amy-low.onnx.json")


def image_to_speech(
    image_path: str,
    output_wav_path: str,
    *,
    ocr_gpu: bool = False,
    tts_gpu: bool = False,
    model_path: Optional[str] = None,
    config_path: Optional[str] = None,
    fallback_text: str = "No text detected in image.",
) -> str:
    """Run OCR on *image_path* and save spoken audio to *output_wav_path*.

    Returns the absolute path to the generated WAV file.
    """

    image = Path(image_path)
    if not image.exists():
        raise FileNotFoundError(f"Image not found: {image}")

    detected_text = detect_text(str(image), gpu=ocr_gpu)
    joined_text = " ".join(detected_text).strip() or fallback_text

    model = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    config = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not model.exists():
        raise FileNotFoundError(f"Piper model not found: {model}")
    if not config.exists():
        raise FileNotFoundError(f"Piper config not found: {config}")

    voice = initialize_piper_voice(str(model), str(config), use_gpu=tts_gpu)
    samples = synthesise_to_memory(voice, joined_text)
    sample_rate = getattr(getattr(voice, "config", None), "sample_rate", 22050)

    output_path = Path(output_wav_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_wav(samples, sample_rate, str(output_path))

    return str(output_path.resolve())


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run OCR on an image and convert the result to speech",
    )
    parser.add_argument("image", help="Path to the image to analyse")
    parser.add_argument(
        "--output",
        default="output.wav",
        help="Where to save the generated WAV file (defaults to ./output.wav)",
    )
    parser.add_argument("--model", help="Optional override for the Piper .onnx model path")
    parser.add_argument("--config", help="Optional override for the Piper config JSON path")
    parser.add_argument("--ocr-gpu", action="store_true", help="Try to run OCR with GPU acceleration")
    parser.add_argument("--tts-gpu", action="store_true", help="Try to run TTS with GPU acceleration")
    parser.add_argument(
        "--fallback-text",
        default="No text detected in image.",
        help="Message to speak if OCR finds no text",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    wav_path = image_to_speech(
        image_path=args.image,
        output_wav_path=args.output,
        ocr_gpu=args.ocr_gpu,
        tts_gpu=args.tts_gpu,
        model_path=args.model,
        config_path=args.config,
        fallback_text=args.fallback_text,
    )
    print(f"Saved synthesised audio to {wav_path}")


if __name__ == "__main__":
    main()
