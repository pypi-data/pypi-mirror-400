"""Audio format detection and validation."""

from pathlib import Path

SUPPORTED_FORMATS: set[str] = {
    '.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma'
}


CONVERSION_REQUIRED_FORMATS: set[str] = {
    '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma'
}


def is_format_supported(file_path: str) -> bool:
    """
    Check if an audio format is supported for transcription.

    Args:
        file_path: Path to the audio file

    Returns:
        True if format is supported, False otherwise
    """
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_FORMATS


def needs_conversion(file_path: str) -> bool:
    """
    Check if an audio file needs to be converted to WAV for transcription.

    Args:
        file_path: Path to the audio file

    Returns:
        True if conversion is needed, False otherwise
    """
    path = Path(file_path)
    return path.suffix.lower() in CONVERSION_REQUIRED_FORMATS


def get_audio_info(file_path: str) -> dict:
    """
    Get basic information about an audio file.

    Args:
        file_path: Path to the audio file

    Returns:
        Dictionary with audio file information
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    return {
        'path': str(path),
        'name': path.name,
        'suffix': path.suffix.lower(),
        'size': path.stat().st_size,
        'is_supported': is_format_supported(file_path),
        'needs_conversion': needs_conversion(file_path)
    }
