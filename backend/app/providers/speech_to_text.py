from abc import ABC, abstractmethod
from typing import Optional


class SpeechToTextProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file
            language: Optional language code (e.g., 'en', 'ur', 'hi')

        Returns:
            dict: {
                'text': str,
                'language': str,
                'confidence': Optional[float],
                'duration': Optional[float]
            }
        """
        pass
