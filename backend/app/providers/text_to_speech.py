from abc import ABC, abstractmethod
from typing import Optional


class TextToSpeechProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language: str,
        voice: Optional[str] = None
    ) -> dict:
        """
        Synthesize text to speech audio.

        Args:
            text: Text to synthesize
            language: Language code (e.g., 'en', 'ur', 'hi')
            voice: Optional voice identifier

        Returns:
            dict: {
                'audio_file_path': str,
                'language': str,
                'voice': Optional[str]
            }
        """
        pass
