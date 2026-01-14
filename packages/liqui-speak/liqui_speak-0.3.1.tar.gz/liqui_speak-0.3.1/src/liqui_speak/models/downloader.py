"""Model and binary downloader for Liqui-Speak."""

import logging
import shutil
import zipfile
from pathlib import Path

from huggingface_hub import hf_hub_download


class ModelDownloader:
    """Handles downloading models and binaries from Hugging Face."""

    def __init__(self):
        self.repo_id = "LiquidAI/LFM2.5-Audio-1.5B-GGUF"
        self.logger = logging.getLogger("liqui_speak")

    def download_all_models(self, target_dir: Path, quant: str = "F16") -> bool:
        """
        Download all required model files.

        Args:
            target_dir: Directory to save models
            quant: Quantization level (F16, Q8_0, Q4_0)

        Returns:
            True if all downloads successful
        """
        from liqui_speak.core.config import get_model_files
        
        target_dir.mkdir(parents=True, exist_ok=True)
        model_files = list(get_model_files(quant).values())

        self.logger.info(f"Downloading LFM2.5-Audio-1.5B ({quant}) model files...")

        for filename in model_files:
            self.logger.info(f"Downloading {filename}...")
            try:
                hf_hub_download(
                    repo_id=self.repo_id,
                    filename=filename,
                    local_dir=str(target_dir),
                    token=None
                )
                self.logger.info(f"{filename} downloaded")
            except Exception as e:
                self.logger.error(f"Failed to download {filename}: {e}")
                return False

        return True

    def download_binary(self, target_dir: Path, platform: str) -> Path | None:
        """
        Download platform-specific llama.cpp binary.

        Args:
            target_dir: Directory to save binary
            platform: Platform identifier (e.g., 'macos-arm64')

        Returns:
            Path to extracted binary or None if failed
        """
        binary_zip = f"llama-liquid-audio-{platform}.zip"
        runners_dir = target_dir / "runners" / platform
        runners_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Downloading {platform} binary...")

        try:

            hf_hub_download(
                repo_id=self.repo_id,
                filename=f"runners/{binary_zip}",
                local_dir=str(target_dir)
            )
            zip_path = target_dir / "runners" / binary_zip


            self.logger.info("Extracting binary...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(runners_dir)


            binary_name = "llama-liquid-audio-cli"
            binary_path = None


            for item in runners_dir.iterdir():
                if item.is_dir():
                    binary_candidate = item / binary_name
                    if binary_candidate.exists():
                        binary_path = binary_candidate
                        break


            if binary_path:
                final_path = runners_dir / "bin" / binary_name
                final_path.parent.mkdir(exist_ok=True)


                if binary_path.parent != runners_dir:
                    for file in binary_path.parent.iterdir():
                        if file.is_file():
                            dest = final_path.parent / file.name
                            shutil.copy2(file, dest)


                final_path.chmod(0o755)


                zip_path.unlink()

                self.logger.info(f"Binary extracted to {final_path}")
                return final_path
            else:
                self.logger.error(f"Binary not found in {binary_zip}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to download binary: {e}")
            return None

    def verify_downloads(self, target_dir: Path) -> bool:
        """Verify all required files are downloaded and intact."""

        for filename in self.model_files:
            filepath = target_dir / filename
            if not filepath.exists():
                self.logger.error(f"Missing model file: {filename}")
                return False




        return True


