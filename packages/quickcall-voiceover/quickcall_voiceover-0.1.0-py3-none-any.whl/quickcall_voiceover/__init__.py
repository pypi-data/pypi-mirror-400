"""QuickCall VoiceOver - Utility tool for creating voice-over audio assets."""

__version__ = "0.1.0"

from quickcall_voiceover.generator import generate_from_text, generate_voiceover

__all__ = ["generate_voiceover", "generate_from_text", "__version__"]
