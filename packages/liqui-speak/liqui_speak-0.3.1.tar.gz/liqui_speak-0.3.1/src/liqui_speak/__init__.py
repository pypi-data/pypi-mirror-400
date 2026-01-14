"""Liqui-Speak: Automated audio transcription with LFM2.5-Audio model."""

from importlib.metadata import version

__version__ = version("liqui-speak")
__author__ = "Abhishek Bhakat"
__description__ = "One-command setup for real-time audio transcription"

from liqui_speak.core.config import get_config
from liqui_speak.core.transcription import transcribe_audio

transcribe = transcribe_audio

__all__ = ["transcribe_audio", "transcribe", "get_config"]
