"""Model wrapper for llama.cpp LFM2.5-Audio integration."""

import logging
import subprocess
from pathlib import Path

from liqui_speak.core.config import get_config
from liqui_speak.models.base import BaseModelBackend
from liqui_speak.platform.detector import PlatformDetector


class LFM2AudioWrapper(BaseModelBackend):
    """Wrapper for llama-lfm2-audio binary."""

    def __init__(self, config: dict[str, str | int | float] | None = None):
        """
        Initialize the model wrapper.

        Args:
            config: Configuration dictionary (auto-detected if None)
        """
        self.config = config or get_config()
        self._validate_config()
        self.logger = logging.getLogger("liqui_speak")

    def _validate_config(self) -> None:
        """Validate that all required files exist."""
        required_files = [
            str(self.config["model_path"]),
            str(self.config["mmproj_path"]),
            str(self.config["vocoder_path"]),
            str(self.config["tokenizer_path"]),
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                raise ValueError(f"Missing required file: {file_path}")

    def transcribe_audio_file(self, audio_file_path: str) -> str | None:
        """
        Transcribe audio file to text using LFM2.5 model.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Transcribed text or None if transcription failed

        Raises:
            RuntimeError: If transcription fails
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")


        detector = PlatformDetector()
        platform = detector.get_supported_platform()

        if not platform:
            raise RuntimeError(f"Unsupported platform: {detector.system}-{detector.machine}")

        binary_path = Path(str(self.config["binary_path"])) / platform / "bin" / "llama-liquid-audio-cli"

        if not binary_path.exists():
            raise ValueError(f"Binary not found: {binary_path}")


        cmd = [
            str(binary_path),
            "-m", str(self.config["model_path"]),
            "--mmproj", str(self.config["mmproj_path"]),
            "-mv", str(self.config["vocoder_path"]),
            "--tts-speaker-file", str(self.config["tokenizer_path"]),
            "-sys", "Perform ASR.",
            "--audio", str(audio_path)
        ]

        try:

            timeout = float(self.config.get("transcription_timeout", 60))


            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=timeout,
                check=False,
                shell=False
            )

            if result.returncode != 0:
                error_msg = f"Transcription failed with code {result.returncode}"
                if result.stdout:
                    error_msg += f": {result.stdout}"
                raise RuntimeError(error_msg)


            transcription = self._parse_output(result.stdout)
            return transcription

        except subprocess.TimeoutExpired:
            raise RuntimeError("Transcription timed out") from None
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}") from e

    def _parse_output(self, output: str | None) -> str | None:
        """Parse model output to extract transcription from LFM2.5 output."""
        if output is None:
            return None

        # LFM2.5 output format includes metadata followed by:
        # === GENERATED TEXT === <actual transcription>
        # Extract only the text after the marker
        marker = "=== GENERATED TEXT ==="
        if marker in output:
            # Get everything after the marker
            text = output.split(marker, 1)[1].strip()
            return text if text else None

        # Fallback: filter out known metadata patterns
        lines = output.strip().split('\n')
        transcription_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip metadata lines
            if any(pattern in line for pattern in [
                "load_gguf:", "main:", "encoding audio", "audio slice",
                "decoding audio", "n_tokens_batch", "audio decoded",
                "audio samples per second", "text tokens per second",
                "samples per second", "tokens per second", " ms"
            ]):
                continue

            transcription_lines.append(line)

        transcription = ' '.join(transcription_lines).strip()
        return transcription if transcription else None

    def test_model(self, test_audio_path: str | None = None) -> bool:
        """Test if the model is working correctly."""
        try:
            if test_audio_path:

                result = self.transcribe_audio_file(test_audio_path)
                return len(result.strip()) > 0 if result is not None else False
            else:



                return True

        except Exception as e:
            self.logger.error(f"Model test failed: {e}")
            return False

    def is_available(self) -> bool:
        """Check if the model backend is available and properly configured."""
        try:
            self._validate_config()
            return True
        except (ValueError, FileNotFoundError):
            return False
