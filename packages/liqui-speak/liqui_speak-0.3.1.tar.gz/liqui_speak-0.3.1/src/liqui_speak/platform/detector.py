"""Platform detection and compatibility utilities."""

import platform
import subprocess
from pathlib import Path


class PlatformDetector:
    """Detects platform and architecture for binary compatibility."""

    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.python_version = platform.python_version()

    def get_platform_info(self) -> dict:
        """Get detailed platform information."""
        return {
            "system": self.system,
            "machine": self.machine,
            "python_version": self.python_version,
            "platform": platform.platform(),
            "processor": platform.processor(),
        }

    def get_supported_platform(self) -> str | None:
        """
        Get the platform identifier for llama.cpp binary downloads.

        Returns:
            Platform string like 'macos-arm64' or None if unsupported
        """
        system = self.system.lower()
        machine = self.machine.lower()


        if machine in ["x86_64", "amd64"]:
            arch = "x64"
        elif machine in ["arm64", "aarch64"]:
            arch = "arm64"
        else:
            return None


        if system == "darwin":
            return f"macos-{arch}"
        elif system == "linux":
            return f"ubuntu-{arch}"
        elif system == "windows":
            return f"windows-{arch}"
        else:
            return None

    def check_dependencies(self) -> dict:
        """Check if required system dependencies are available."""
        deps = {
            "portaudio": self._check_portaudio(),
            "ffmpeg": self._check_command("ffmpeg"),
        }
        return deps

    def _check_portaudio(self) -> bool:
        """Check if portaudio library is available."""

        import platform
        system = platform.system()

        if system == "Darwin":

            paths = [
                "/opt/homebrew/lib/libportaudio.dylib",
                "/usr/local/lib/libportaudio.dylib",
                "/usr/lib/libportaudio.dylib",
            ]
        elif system == "Linux":
            paths = [
                "/usr/lib/x86_64-linux-gnu/libportaudio.so",
                "/usr/lib/libportaudio.so",
                "/usr/local/lib/libportaudio.so",
            ]
        elif system == "Windows":
            paths = [
                "portaudio.dll",
                "libportaudio.dll",
            ]
        else:
            return False


        for path in paths:
            if Path(path).exists():
                return True


        try:
            import importlib.util
            return importlib.util.find_spec("pyaudio") is not None
        except ImportError:
            return False

    def _check_command(self, command: str) -> bool:
        """Check if a system command exists."""
        try:
            subprocess.run([command, "--version"],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def verify_python_version(self) -> bool:
        """Verify Python version is >= 3.12."""
        import sys
        return sys.version_info >= (3, 12)

    def get_homebrew_path(self) -> Path | None:
        """Get Homebrew installation path on macOS."""
        if self.system != "Darwin":
            return None


        paths = [
            Path("/opt/homebrew"),
            Path("/usr/local"),
        ]

        for path in paths:
            if path.exists() and (path / "bin" / "brew").exists():
                return path

        return None
