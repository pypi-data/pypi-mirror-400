"""Command-line interface for Liqui-Speak."""

import argparse
import sys
from importlib.metadata import version

from liqui_speak.cli.commands import handle_config, handle_transcribe
from liqui_speak.core.config import setup_logging


def main():
    """Main CLI entry point."""

    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="Liqui-Speak: Automated audio transcription with LFM2.5-Audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  liqui-speak config
  liqui-speak transcribe audio.m4a
  liqui-speak transcribe audio.wav --verbose

        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('liqui-speak')}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")


    config_parser = subparsers.add_parser(
        "config",
        help="Install dependencies and download models"
    )
    config_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed setup progress"
    )
    config_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstallation of dependencies"
    )
    config_parser.add_argument(
        "--quant",
        choices=["F16", "Q8_0", "Q4_0"],
        default="F16",
        help="Model quantization level: F16 (default, best quality), Q8_0 (smaller), Q4_0 (smallest)"
    )


    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe audio file"
    )
    transcribe_parser.add_argument(
        "audio_file",
        help="Path to audio file (M4A, AAC, WAV, MP3, etc.)"
    )

    transcribe_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed transcription progress"
    )


    if len(sys.argv) == 1:
        parser.print_help()
        return 0


    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        known_commands = {'config', 'transcribe', '-h', '--help', '--version'}

        if first_arg not in known_commands and not first_arg.startswith('-'):

            sys.argv.insert(1, 'transcribe')

    args = parser.parse_args()

    try:
        if args.command == "config":
            return handle_config(args)
        elif args.command == "transcribe":
            return handle_transcribe(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

__all__ = ["main"]
