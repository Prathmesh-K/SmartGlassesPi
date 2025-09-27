"""Text-to-speech utilities for the SmartGlasses project."""

from .piper_tts import (  # noqa: F401
    initialize_piper_voice,
    synthesise_to_memory,
    save_wav,
)
