"""Configuration management for Liqui-Speak."""

import json
import logging
import os
from pathlib import Path

# Available quantization levels
QUANT_LEVELS = ["F16", "Q8_0", "Q4_0"]
DEFAULT_QUANT = "F16"

CONFIG_FILE = "config.json"

def get_model_files(quant: str = DEFAULT_QUANT) -> dict[str, str]:
    """Get model filenames for the specified quantization level."""
    if quant not in QUANT_LEVELS:
        raise ValueError(f"Invalid quantization level: {quant}. Choose from: {QUANT_LEVELS}")
    return {
        "model": f"LFM2.5-Audio-1.5B-{quant}.gguf",
        "mmproj": f"mmproj-LFM2.5-Audio-1.5B-{quant}.gguf",
        "vocoder": f"vocoder-LFM2.5-Audio-1.5B-{quant}.gguf",
        "tokenizer": f"tokenizer-LFM2.5-Audio-1.5B-{quant}.gguf",
    }

# Default model files (F16)
MODEL_FILES = get_model_files(DEFAULT_QUANT)

TRANSCRIPTION_TIMEOUT = 60


LOG_LEVEL = os.getenv("LIQUI_SPEAK_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging() -> logging.Logger:
    """Set up logging configuration for Liqui-Speak."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger("liqui_speak")


def get_config_file_path() -> Path:
    """Get path to config.json file."""
    return Path.home() / ".liqui_speak" / CONFIG_FILE


def load_user_config() -> dict:
    """Load user configuration from config.json."""
    config_path = get_config_file_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_user_config(config: dict) -> None:
    """Save user configuration to config.json."""
    config_path = get_config_file_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_config() -> dict[str, str | int | float]:
    """
    Get configuration for transcription.

    Returns:
        Configuration dictionary with model paths and settings
    """
    setup_dir = Path.home() / ".liqui_speak"
    models_dir = setup_dir / "models"
    
    # Load user config to get quantization level
    user_config = load_user_config()
    quant = user_config.get("quant", DEFAULT_QUANT)
    model_files = get_model_files(quant)

    config = {
        "model_dir": str(models_dir),
        "model_path": str(models_dir / model_files["model"]),
        "mmproj_path": str(models_dir / model_files["mmproj"]),
        "vocoder_path": str(models_dir / model_files["vocoder"]),
        "tokenizer_path": str(models_dir / model_files["tokenizer"]),
        "binary_path": str(models_dir / "runners"),
        "sample_rate": 48000,
        "channels": 1,
        "chunk_duration": 2.0,
        "overlap": 0.5,
        "transcription_timeout": TRANSCRIPTION_TIMEOUT,
        "quant": quant,
    }


    for key in config:
        env_key = f"LIQUI_SPEAK_{key.upper()}"
        if env_key in os.environ:
            if key in ["sample_rate", "channels", "transcription_timeout"]:
                try:
                    config[key] = int(os.environ[env_key])
                except ValueError:
                    config[key] = float(os.environ[env_key])
            elif key in ["chunk_duration", "overlap"]:
                config[key] = float(os.environ[env_key])
            else:
                config[key] = os.environ[env_key]

    return config


def is_configured() -> bool:
    """Check if Liqui-Speak is properly configured."""
    config = get_config()


    required_files = [
        config["model_path"],
        config["mmproj_path"],
        config["vocoder_path"],
        config["tokenizer_path"],
    ]

    for file_path in required_files:
        if not Path(str(file_path)).exists():
            return False

    return True


def get_setup_dir() -> Path:
    """Get the setup directory path."""
    return Path.home() / ".liqui_speak"


def ensure_setup_dir() -> Path:
    """Ensure setup directory exists and return path."""
    setup_dir = get_setup_dir()
    setup_dir.mkdir(exist_ok=True)
    return setup_dir
