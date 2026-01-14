"""Automated setup manager for Liqui-Speak."""

import importlib
import importlib.util
import logging
import subprocess
import sys
from pathlib import Path

from liqui_speak.models.downloader import ModelDownloader
from liqui_speak.platform.detector import PlatformDetector
from liqui_speak.setup.shortcut_template import install_shortcut


class SetupManager:
    """Handles automatic installation of system dependencies and models."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.model_downloader = ModelDownloader()
        self.setup_dir = Path.home() / ".liqui_speak"
        self.setup_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("liqui_speak")

    def run_full_setup(self, verbose: bool = True, force: bool = False, quant: str = "F16") -> bool:
        """
        Run complete setup process.

        Args:
            verbose: Show detailed progress
            force: Force reinstallation even if dependencies already exist
            quant: Quantization level (F16, Q8_0, Q4_0)

        Returns:
            True if setup successful
        """
        if verbose:
            self.logger.info("Starting Liqui-Speak setup...")

        try:

            if verbose:
                self.logger.info("Installing system dependencies...")
            self._install_system_dependencies(force=force)


            if verbose:
                self.logger.info("Setting up Python environment...")
            self._setup_python_environment(force=force)


            if verbose:
                self.logger.info("Downloading models...")
            self._download_models(force=force, quant=quant)
            
            # Save user configuration
            from liqui_speak.core.config import save_user_config
            save_user_config({"quant": quant})
            if verbose:
                self.logger.info(f"Saved configuration (quant={quant})")


            if verbose:
                self.logger.info("Verifying installation...")
            self._verify_installation()

            # Install macOS Shortcut (macOS only)
            if self.platform.system == "Darwin":
                if verbose:
                    self.logger.info("Installing macOS Shortcut...")
                self._install_shortcut(verbose=verbose)

            if verbose:
                self.logger.info("Setup complete! You can now use: liqui-speak your_audio.m4a")

            return True

        except Exception as e:

            self.logger.error(f"Setup failed: {e}")
            if not verbose:
                self.logger.info("Try running with --verbose for more details")
            return False

    def _install_system_dependencies(self, force: bool = False) -> None:
        """Install PortAudio and FFmpeg system dependencies."""
        system = self.platform.system

        if system == "Darwin":
            self._install_macos_dependencies(force=force)
        elif system == "Linux":
            self._install_linux_dependencies(force=force)
        elif system == "Windows":
            self._install_windows_dependencies(force=force)
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def _install_macos_dependencies(self, force: bool = False) -> None:
        """Install dependencies on macOS."""
        if not self._command_exists("brew"):
            raise RuntimeError("Homebrew not found. Please install from https://brew.sh")

        packages = ["portaudio", "ffmpeg"]
        for package in packages:
            if force or not self._command_exists(package):
                self.logger.info(f"Installing {package}...")
                subprocess.run(["brew", "install", package], check=True)
            else:
                self.logger.info(f"{package} already installed, skipping...")

    def _confirm_sudo_action(self, action_description: str) -> bool:
        """Ask user for confirmation before running sudo commands."""
        self.logger.warning(f"This will run sudo commands to {action_description}")
        response = input("Continue? [y/N]: ").strip().lower()
        return response in ('y', 'yes')

    def _install_linux_dependencies(self, force: bool = False) -> None:
        """Install dependencies on Linux."""
        if not self._confirm_sudo_action("install portaudio and ffmpeg"):
            raise RuntimeError("User cancelled installation")


        if self._command_exists("apt-get"):
            packages = ["portaudio19-dev", "ffmpeg"]
            subprocess.run(["sudo", "apt-get", "update"], check=False)
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)

        elif self._command_exists("yum"):
            packages = ["portaudio-devel", "ffmpeg"]
            subprocess.run(["sudo", "yum", "install", "-y"] + packages, check=True)

        elif self._command_exists("pacman"):
            packages = ["portaudio", "ffmpeg"]
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + packages, check=True)
        else:
            raise RuntimeError("No supported package manager found (apt/yum/pacman)")

    def _install_windows_dependencies(self, force: bool = False) -> None:
        """Install dependencies on Windows."""
        if self._command_exists("choco"):
            packages = ["portaudio", "ffmpeg"]
            for package in packages:
                subprocess.run(["choco", "install", package, "-y"], check=True)
        elif self._command_exists("scoop"):
            subprocess.run(["scoop", "install", "portaudio", "ffmpeg"], check=True)
        else:
            raise RuntimeError(
                "Chocolatey or Scoop not found. "
                "Please install Chocolatey from https://chocolatey.org"
            )

    def _setup_python_environment(self, force: bool = False) -> None:
        """Verify Python version and install PyDub/python-magic if needed."""

        self.logger.info(f"Python {sys.version.split()[0]} detected")


        if importlib.util.find_spec("pydub") is not None:
            self.logger.info("PyDub already installed")
        else:
            self.logger.info("Installing PyDub...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pydub"], check=True)


        self._install_python_magic()

    def _install_python_magic(self) -> None:
        """Install python-magic with platform-specific handling."""

        if importlib.util.find_spec("magic") is not None:
            self.logger.info("python-magic already installed")
            return

        system = self.platform.system

        if system == "Windows":

            self.logger.info("Installing python-magic-bin for Windows...")
            subprocess.run([sys.executable, "-m", "pip", "install", "python-magic-bin"], check=True)
        else:

            self.logger.info("Installing python-magic...")
            subprocess.run([sys.executable, "-m", "pip", "install", "python-magic"], check=True)


        try:
            importlib.util.find_spec("magic")
            self.logger.info("python-magic installation verified")
        except ImportError as e:
            if system == "Windows":
                raise RuntimeError(
                    "python-magic installation failed. Try manually installing "
                    "python-magic-bin: pip install python-magic-bin"
                ) from e
            else:
                raise RuntimeError(
                    f"python-magic installation failed. Ensure libmagic is installed: {e}"
                ) from e

    def _download_models(self, force: bool = False, quant: str = "F16") -> None:
        """Download LFM2.5-Audio model and binaries."""
        from liqui_speak.core.config import get_model_files
        
        model_dir = self.setup_dir / "models"
        model_dir.mkdir(exist_ok=True)

        model_files_dict = get_model_files(quant)
        model_files = list(model_files_dict.values())

        all_models_exist = all((model_dir / filename).exists() for filename in model_files)

        if all_models_exist and not force:
            self.logger.info("Model files already downloaded")
        else:
            self.logger.info(f"Downloading LFM2.5-Audio-1.5B ({quant}) model files...")

            self.model_downloader.download_all_models(model_dir, quant=quant)


        from liqui_speak.platform.detector import PlatformDetector
        detector = PlatformDetector()
        platform = detector.get_supported_platform()

        if platform:
            binary_path = model_dir / "runners" / platform / "bin" / "llama-liquid-audio-cli"
            if binary_path.exists():
                self.logger.info(f"Binary already downloaded for {platform}")
            else:
                self.logger.info(f"Downloading {platform} binary...")
                binary_result = self.model_downloader.download_binary(model_dir, platform)
                if binary_result:
                    self.logger.info(f"Binary downloaded: {binary_result}")
        else:
            self.logger.warning(f"Platform {detector.system}-{detector.machine} not supported for binaries")

    def _verify_installation(self, force: bool = False) -> None:
        """Verify that everything is working correctly."""

        deps = {
            "ffmpeg": self._command_exists("ffmpeg"),
            "pydub": self._check_python_module("pydub"),
            "python-magic": self._check_python_module("magic"),
        }

        missing = [name for name, installed in deps.items() if not installed]
        if missing:
            raise RuntimeError(f"Missing dependencies: {', '.join(missing)}")

        self.logger.info("All dependencies verified")

    def _command_exists(self, command: str) -> bool:
        """Check if a system command exists."""
        try:

            if command == "ffmpeg":
                subprocess.run([command, "-version"],
                             capture_output=True, check=True)
            elif command == "portaudio":
                return self.platform._check_portaudio()
            else:
                subprocess.run([command, "--version"],
                             capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_python_module(self, module: str) -> bool:
        """Check if a Python module is installed."""
        try:
            __import__(module)
            return True
        except ImportError:
            return False

    def _install_shortcut(self, verbose: bool = True) -> None:
        """Install macOS Shortcut for voice transcription."""
        # The ~/.liqui_speak directory is already created in __init__, just use it
        # No separate directory needed - recordings go in the main app dir
        
        # Find the liqui-speak binary path
        # Try to find it in the current venv or system path
        import shutil
        binary_path = shutil.which("liqui-speak")
        
        if not binary_path:
            # Fall back to common locations
            venv_binary = Path(sys.prefix) / "bin" / "liqui-speak"
            if venv_binary.exists():
                binary_path = str(venv_binary)
            else:
                self.logger.warning("Could not find liqui-speak binary, skipping shortcut installation")
                return
        
        home_dir = str(Path.home())
        
        try:
            if verbose:
                self.logger.info("Opening Shortcuts app - please click 'Add Shortcut' to confirm")
            
            success = install_shortcut(binary_path, home_dir)
            
            if success:
                self.logger.info("Shortcut 'liqui-speak' ready to install")
                self.logger.info("📱 TIP: On first run, macOS will ask for permissions:")
                self.logger.info("   • Microphone access (for recording)")
                self.logger.info("   • File access (to save recordings)")
                self.logger.info("   • Shell script execution (for transcription)")
            else:
                self.logger.warning("Could not open shortcut file")
        except Exception as e:
            self.logger.warning(f"Shortcut installation skipped: {e}")

