"""Base classes for model backends."""

from abc import ABC, abstractmethod


class BaseModelBackend(ABC):
    """Abstract base class for audio transcription model backends."""

    @abstractmethod
    def transcribe_audio_file(self, audio_file_path: str) -> str | None:
        """
        Transcribe an audio file to text.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Transcribed text or None if transcription failed
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model backend is available and properly configured."""
        pass
