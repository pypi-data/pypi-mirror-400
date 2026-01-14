"""Fast audio format converter using PyDub for M4A/AAC support."""

import tempfile
from pathlib import Path

from liqui_speak.core.config import get_config


def convert_audio_for_transcription(input_file: str, output_format: str = "wav") -> str:
    """
    Convert audio file to format supported by the transcription tool.

    Uses PyDub for fast in-memory conversion without external ffmpeg calls.

    Args:
        input_file: Path to input audio file (M4A, AAC, etc.)
        output_format: Target format ("wav", "mp3", "flac")

    Returns:
        Path to converted audio file (temporary file)

    Raises:
        ImportError: If PyDub is not installed
        ValueError: If conversion fails
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError(
            "PyDub is required for audio conversion. "
            "Install with: pip install pydub"
        ) from None

    input_path = Path(input_file)

    try:

        audio = AudioSegment.from_file(str(input_path))


        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(int(get_config()["sample_rate"]))


        temp_file = tempfile.NamedTemporaryFile(
            suffix=f".{output_format}",
            delete=False,
            prefix="liqui_speak_"
        )
        temp_file.close()


        audio.export(temp_file.name, format=output_format,
                    codec="pcm_s16le" if output_format == "wav" else None)

        return temp_file.name

    except Exception as e:
        raise ValueError(f"Audio conversion failed: {e}") from e
