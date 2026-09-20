from typing import Optional
from app.providers.speech_to_text import SpeechToTextProvider
from app.providers.translation import TranslationProvider
from app.providers.text_to_speech import TextToSpeechProvider


class MockSpeechToTextProvider(SpeechToTextProvider):
    """Mock Speech-to-Text provider for development/testing."""

    async def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> dict:
        """Return mock transcription instantly."""
        return {
            "text": "This is a mock transcription for development and testing purposes.",
            "language": language or "en",
            "confidence": 0.95,
            "duration": 5.0
        }


class MockTranslationProvider(TranslationProvider):
    """Mock Translation provider for development/testing."""

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> dict:
        """Return mock translation instantly."""
        return {
            "translated_text": f"[MOCK TRANSLATION: {text} from {source_language} to {target_language}]",
            "source_language": source_language,
            "target_language": target_language
        }


class MockTextToSpeechProvider(TextToSpeechProvider):
    """Mock Text-to-Speech provider for development/testing."""

    async def synthesize(
        self,
        text: str,
        language: str,
        voice: Optional[str] = None
    ) -> dict:
        """Return mock audio file path instantly."""
        return {
            "audio_file_path": f"mock_audio_{language}_{hash(text)}.mp3",
            "language": language,
            "voice": voice or "default"
        }
