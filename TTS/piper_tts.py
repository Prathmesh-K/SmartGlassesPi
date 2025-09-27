"""Utility helpers to initialize and run Piper TTS on the Raspberry Pi.

This module wraps the ``piper-tts`` library so the rest of the project can
load a Piper voice once and reuse it for repeated synthesis calls.  It also
ships with a tiny CLI that lets you try the voice from the command line:

.. code-block:: bash

    python3 TTS/piper_tts.py --model ~/voices/en_US-amy-low.onnx --config ~/voices/en_US-amy-low.onnx.json \
        --text "Hello from Piper" --output hello.wav

The script expects you to provide the paths to a Piper voice (``.onnx``) and
its accompanying ``.json`` configuration file.  You can download prebuilt
voices from the official Piper releases.
"""

from __future__ import annotations

import argparse
import time
import wave
from pathlib import Path
from typing import Optional

import numpy as np
from piper import PiperVoice


def initialize_piper_voice(
    model_path: str,
    config_path: Optional[str] = None,
    *,
    use_gpu: bool = False,
):
    """Load a Piper voice and return the reusable synthesiser object.

    Parameters
    ----------
    model_path:
        Path to the ``.onnx`` Piper model file.
    config_path:
        Optional path to the configuration JSON that ships with the model.
        Piper can usually infer this if the file sits next to the model, but
        providing it explicitly avoids surprises.
    use_gpu:
        Request GPU acceleration if available.  On a Raspberry Pi this will
        typically stay ``False``; the flag is provided for API completeness.

    Returns
    -------
    piper.PiperVoice
        A loaded Piper voice ready for synthesis.
    """

    start_time = time.perf_counter()
    print(f"[initialize_piper_voice] start at {start_time:.6f}s")

    if not Path(model_path).exists():
        raise FileNotFoundError(f"Piper model not found: {model_path}")

    if config_path is not None and not Path(config_path).exists():
        raise FileNotFoundError(f"Piper config not found: {config_path}")

    if use_gpu:
        print(
            "GPU acceleration requested; Piper will attempt to use CUDA if the "
            "environment supports it. On Raspberry Pi this will fall back to CPU."
        )

    voice = PiperVoice.load(model_path, config_path, use_cuda=use_gpu)

    end_time = time.perf_counter()
    print(
        f"[initialize_piper_voice] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)"
    )
    return voice


def synthesise_to_memory(voice: PiperVoice, text: str) -> np.ndarray:
    """Generate speech samples for *text* using a previously loaded voice."""

    start_time = time.perf_counter()
    print(f"[synthesise_to_memory] start at {start_time:.6f}s")

    if not text or not text.strip():
        raise ValueError("Text to synthesise must not be empty.")

    chunks = list(voice.synthesize_stream_raw(text))
    audio_bytes = b"".join(chunks)
    audio = np.frombuffer(audio_bytes, dtype=np.int16)
    end_time = time.perf_counter()
    print(
        f"[synthesise_to_memory] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)"
    )
    return audio


def save_wav(samples: np.ndarray, sample_rate: int, output_path: str) -> None:
    """Persist the generated samples as a 16‑bit mono WAV file."""

    start_time = time.perf_counter()
    print(f"[save_wav] start at {start_time:.6f}s")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Piper returns 16-bit PCM samples (int16).  Ensure shape is 1-D.
    samples = np.asarray(samples, dtype=np.int16).reshape(-1)

    with wave.open(str(output_file), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())

    end_time = time.perf_counter()
    print(f"[save_wav] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)")


def _read_text_argument(text: Optional[str], text_file: Optional[str]) -> str:
    """Resolve the synthesiser input text from CLI arguments."""

    start_time = time.perf_counter()
    print(f"[_read_text_argument] start at {start_time:.6f}s")

    if text and text.strip():
        result = text
    elif text_file:
        file_path = Path(text_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {text_file}")
        result = file_path.read_text(encoding="utf-8").strip()
    else:
        raise ValueError("Either --text or --text-file must be provided and non-empty.")

    end_time = time.perf_counter()
    print(
        f"[_read_text_argument] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)"
    )
    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    start_time = time.perf_counter()
    print(f"[_build_arg_parser] start at {start_time:.6f}s")

    parser = argparse.ArgumentParser(description="Synthesize speech with Piper TTS")
    parser.add_argument("--model", required=True, help="Path to the Piper .onnx model")
    parser.add_argument(
        "--config",
        default=None,
        help="Optional path to the Piper config JSON (defaults to model directory)",
    )

    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Inline text to synthesise")
    text_group.add_argument("--text-file", help="Path to a UTF-8 text file to synthesise")

    parser.add_argument(
        "--output",
        default="tts_output.wav",
        help="Path to write the generated WAV file (defaults to ./tts_output.wav)",
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Attempt to use GPU acceleration if available",
    )
    end_time = time.perf_counter()
    print(
        f"[_build_arg_parser] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)"
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    start_time = time.perf_counter()
    print(f"[main] start at {start_time:.6f}s")

    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    voice = initialize_piper_voice(
        model_path=args.model,
        config_path=args.config,
        use_gpu=args.use_gpu,
    )

    text_to_say = _read_text_argument(args.text, args.text_file)
    samples = synthesise_to_memory(voice, text_to_say)
    save_wav(samples, voice.config.sample_rate, args.output)

    duration = len(samples) / voice.config.sample_rate
    print(f"Synthesised {duration:.2f}s of audio to {args.output}")

    end_time = time.perf_counter()
    print(f"[main] end at {end_time:.6f}s (elapsed {end_time - start_time:.3f}s)")


if __name__ == "__main__":
    main()
