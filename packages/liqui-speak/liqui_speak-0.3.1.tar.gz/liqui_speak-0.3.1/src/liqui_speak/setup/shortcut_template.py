"""macOS Shortcut template for Liqui-Speak voice transcription."""

import plistlib
import subprocess
import tempfile
import uuid
from pathlib import Path


def get_shortcut_plist(binary_path: str, home_dir: str) -> dict:
    """
    Generate the shortcut plist dictionary with dynamic paths.
    
    Args:
        binary_path: Full path to liqui-speak binary
        home_dir: User's home directory path
    
    Returns:
        Dictionary representing the shortcut plist
    """
    # Generate unique UUIDs for action references
    record_uuid = str(uuid.uuid4()).upper()
    save_uuid = str(uuid.uuid4()).upper()
    transcribe_uuid = str(uuid.uuid4()).upper()
    read_uuid = str(uuid.uuid4()).upper()
    clipboard_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()
    
    speakkit_dir = f"{home_dir}/.liqui_speak"
    recording_path = f"{speakkit_dir}/recording.m4a"
    
    return {
        "WFQuickActionSurfaces": [],
        "WFWorkflowActions": [
            # Action 1: Record Audio
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.recordaudio",
                "WFWorkflowActionParameters": {
                    "UUID": record_uuid,
                    "WFRecordingCompression": "Normal",
                    "WFRecordingStart": "Immediately",
                }
            },
            # Action 2: Save File to ~/.liqui_speak/recording.m4a
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
                "WFWorkflowActionParameters": {
                    "UUID": save_uuid,
                    "WFAskWhereToSave": False,
                    "WFFileDestinationPath": "recording.m4a",
                    "WFFolder": {
                        "displayName": ".liqui_speak",
                        "fileLocation": {
                            "WFFileLocationType": "Home",
                            "relativeSubpath": ".liqui_speak",
                        },
                        "filename": ".liqui_speak",
                    },
                    "WFInput": {
                        "Value": {
                            "OutputName": "Recorded Audio",
                            "OutputUUID": record_uuid,
                            "Type": "ActionOutput",
                        },
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "WFSaveFileOverwrite": True,
                }
            },
            # Action 3: Run liqui-speak transcribe
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.runshellscript",
                "WFWorkflowActionParameters": {
                    "UUID": transcribe_uuid,
                    "Script": f"{binary_path} transcribe {recording_path}",
                    "Shell": "/bin/zsh",
                }
            },
            # Action 4: Copy to Clipboard
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.setclipboard",
                "WFWorkflowActionParameters": {
                    "UUID": clipboard_uuid,
                    "WFInput": {
                        "Value": {
                            "OutputName": "Shell Script Result",
                            "OutputUUID": transcribe_uuid,
                            "Type": "ActionOutput",
                        },
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                }
            },
            # Action 5: Output result
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.output",
                "WFWorkflowActionParameters": {
                    "UUID": output_uuid,
                    "WFOutput": {
                        "Value": {
                            "attachmentsByRange": {
                                "{0, 1}": {
                                    "OutputName": "Shell Script Result",
                                    "OutputUUID": transcribe_uuid,
                                    "Type": "ActionOutput",
                                }
                            },
                            "string": "\ufffc",
                        },
                        "WFSerializationType": "WFTextTokenString",
                    },
                }
            },
        ],
        "WFWorkflowClientVersion": "4046.0.2.2",
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 59780,  # Microphone icon
            "WFWorkflowIconStartColor": 463140863,  # Purple color
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": [
            "WFStringContentItem",
        ],
        "WFWorkflowMinimumClientVersion": 1106,
        "WFWorkflowMinimumClientVersionString": "1106",
        "WFWorkflowOutputContentItemClasses": [
            "WFContentItem",
        ],
        "WFWorkflowTypes": [
            "WFWorkflowTypeShowInSearch",
        ],
    }


def create_shortcut_file(binary_path: str, home_dir: str) -> Path:
    """
    Create a .shortcut file that can be imported into macOS Shortcuts app.
    
    Args:
        binary_path: Full path to liqui-speak binary
        home_dir: User's home directory path
    
    Returns:
        Path to the created .shortcut file
    """
    plist_data = get_shortcut_plist(binary_path, home_dir)
    
    # Create temp file with .shortcut extension
    shortcut_path = Path(tempfile.gettempdir()) / "liqui-speak.shortcut"
    
    with open(shortcut_path, "wb") as f:
        plistlib.dump(plist_data, f, fmt=plistlib.FMT_BINARY)
    
    return shortcut_path


def install_shortcut(binary_path: str, home_dir: str) -> bool:
    """
    Generate, sign, and open the shortcut file to trigger import dialog.
    
    Args:
        binary_path: Full path to liqui-speak binary
        home_dir: User's home directory path
    
    Returns:
        True if shortcut file was opened successfully
    """
    try:
        unsigned_path = create_shortcut_file(binary_path, home_dir)
        signed_path = Path(tempfile.gettempdir()) / "liqui-speak-signed.shortcut"
        
        # Sign the shortcut using macOS shortcuts CLI
        sign_result = subprocess.run(
            [
                "shortcuts", "sign",
                "--mode", "anyone",
                "--input", str(unsigned_path),
                "--output", str(signed_path)
            ],
            capture_output=True,
            check=True
        )
        
        # Use 'open' to trigger Shortcuts app import
        subprocess.run(
            ["open", str(signed_path)],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False

