from abc import ABC, abstractmethod
from typing import Optional


class TranslationProvider(ABC):
    """Abstract base class for Translation providers."""

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> dict:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'en', 'ur', 'hi')
            target_language: Target language code (e.g., 'en', 'ur', 'hi')

        Returns:
            dict: {
                'translated_text': str,
                'source_language': str,
                'target_language': str
            }
        """
        pass
