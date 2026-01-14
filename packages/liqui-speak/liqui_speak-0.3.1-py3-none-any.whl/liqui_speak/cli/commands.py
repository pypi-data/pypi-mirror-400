"""CLI command handlers for Liqui-Speak."""

import logging
from pathlib import Path

from liqui_speak.core.transcription import transcribe_audio
from liqui_speak.setup.manager import SetupManager


def handle_config(args) -> int:
    """Handle config command."""
    logger = logging.getLogger("liqui_speak")
    logger.info("Starting Liqui-Speak configuration...")

    setup_manager = SetupManager()

    if args.force:
        logger.info("Force mode enabled - reinstalling everything")
    
    logger.info(f"Using {args.quant} quantization")

    success = setup_manager.run_full_setup(verbose=args.verbose, force=args.force, quant=args.quant)

    if success:
        logger.info("Configuration complete!")
        logger.info("You can now transcribe audio files:")
        logger.info("   liqui-speak transcribe audio.m4a")
        logger.info("   liqui-speak audio.m4a")
        return 0
    else:
        logger.error("Configuration failed. Check the logs above.")
        return 1


def handle_transcribe(args) -> int:
    """Handle transcribe command."""
    logger = logging.getLogger("liqui_speak")


    if '\x00' in args.audio_file:
        logger.error("Invalid file path")
        return 1

    audio_file = Path(args.audio_file).resolve()

    if not audio_file.is_file():
        logger.error(f"Audio file not found: {audio_file}")
        return 1

    if args.verbose:
        logger.info(f"Transcribing: {audio_file.name}")

    try:
        result = transcribe_audio(
            str(audio_file),
            verbose=args.verbose
        )

        if result is not None:
            print(result.strip(), end='')
            return 0
        else:
            if args.verbose:
                logger.error("Transcription failed")
            return 1

    except Exception as e:
        if args.verbose:
            logger.error(f"Transcription error: {e}")
        return 1
