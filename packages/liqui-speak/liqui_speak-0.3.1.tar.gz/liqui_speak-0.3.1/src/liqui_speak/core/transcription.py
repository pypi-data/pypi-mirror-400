"""Audio transcription functionality for Liqui-Speak."""

import logging
from pathlib import Path

from liqui_speak.audio.converter import convert_audio_for_transcription
from liqui_speak.audio.formats import needs_conversion
from liqui_speak.core.config import get_config
from liqui_speak.models.wrapper import LFM2AudioWrapper

logger = logging.getLogger(__name__)


def transcribe_audio(
    audio_file_path: str,
    verbose: bool = False
) -> str | None:
    """
    Transcribe an audio file to text.

    Args:
        audio_file_path: Path to audio file
        verbose: Whether to show detailed progress

    Returns:
        Transcribed text or None if failed
    """
    audio_path = Path(audio_file_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")


    if needs_conversion(audio_file_path):
        if verbose:
            print(f"🔄 Converting {audio_path.suffix} to WAV format...")

        try:

            converted_file = convert_audio_for_transcription(audio_file_path, "wav")

            try:
                return _transcribe_wav_file(converted_file, verbose)
            finally:

                try:
                    Path(converted_file).unlink()
                except OSError:
                    pass
        except Exception as e:
            if verbose:
                logger.error(f"❌ Audio conversion failed: {e}")
            return None
    else:

        return _transcribe_wav_file(audio_file_path, verbose)


def _transcribe_wav_file(
    audio_file_path: str,
    verbose: bool = False
) -> str | None:
    """
    Transcribe a WAV file using the LFM2 model.

    Args:
        audio_file_path: Path to WAV file
        verbose: Whether to show detailed progress

    Returns:
        Transcribed text or None if failed
    """

    config = get_config()

    if verbose:
        print(f"🎵 Starting transcription of {Path(audio_file_path).name}")
        print(f"📊 Duration: {config.get('duration', 'unknown')}")

    try:

        model = LFM2AudioWrapper(config)


        transcription = model.transcribe_audio_file(audio_file_path)

        if verbose:
            print("✅ Transcription complete")

        return transcription

    except Exception as e:
        if verbose:
            logger.error(f"❌ Transcription failed: {e}")
        return None
