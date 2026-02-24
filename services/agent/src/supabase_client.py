"""
Supabase client for fetching word pairs from the database.

This module provides a simple interface to query the word_pairs table
for vocabulary practice in the word guessing game.
"""

import logging
import os
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError(
        "supabase package is not installed. "
        "Add 'supabase' to pyproject.toml dependencies and run: pip install supabase"
    )

load_dotenv(".env.local")

logger = logging.getLogger("agent")


@dataclass
class WordPair:
    """Represents a word pair with English and translated word."""
    id: str
    english_word: str
    translated_word: str
    target_language: str


class SupabaseWordService:
    """Service for fetching word pairs from Supabase."""

    def __init__(self):
        """Initialize the Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            logger.warning(
                "SUPABASE_URL or SUPABASE_KEY not set. "
                "Word game will use fallback word list."
            )
            self.client = None
        else:
            self.client: Client = create_client(
                self.supabase_url, self.supabase_key
            )
            logger.info("Supabase client initialized")

    def is_available(self) -> bool:
        """Check if Supabase client is available."""
        return self.client is not None

    def get_word_pairs(self, target_language: str, limit: int = 50) -> List[WordPair]:
        """
        Fetch word pairs for a specific target language.

        Args:
            target_language: The language to fetch word pairs for (e.g., "Portuguese")
            limit: Maximum number of word pairs to return

        Returns:
            List of WordPair objects
        """
        if not self.is_available():
            logger.warning("Supabase not available, using fallback words")
            return self._get_fallback_words(target_language)

        try:
            response = self.client.table("word_pairs").select(
                "*"
            ).eq("target_language", target_language).limit(limit).execute()

            word_pairs = [
                WordPair(
                    id=word["id"],
                    english_word=word["english_word"],
                    translated_word=word["translated_word"],
                    target_language=word["target_language"]
                )
                for word in response.data
            ]

            logger.info(f"Fetched {len(word_pairs)} word pairs for {target_language}")
            return word_pairs

        except Exception as e:
            logger.error(f"Error fetching word pairs from Supabase: {e}")
            return self._get_fallback_words(target_language)

    def _get_fallback_words(self, target_language: str) -> List[WordPair]:
        """
        Provide fallback word pairs when Supabase is unavailable.

        This ensures the word game can still function for testing purposes.
        """
        if target_language.lower() in ["portuguese", "pt"]:
            return [
                WordPair(id="1", english_word="dog", translated_word="cachorro", target_language="Portuguese"),
                WordPair(id="2", english_word="cat", translated_word="gato", target_language="Portuguese"),
                WordPair(id="3", english_word="house", translated_word="casa", target_language="Portuguese"),
                WordPair(id="4", english_word="water", translated_word="água", target_language="Portuguese"),
                WordPair(id="5", english_word="hello", translated_word="olá", target_language="Portuguese"),
                WordPair(id="6", english_word="goodbye", translated_word="adeus", target_language="Portuguese"),
                WordPair(id="7", english_word="thank you", translated_word="obrigado", target_language="Portuguese"),
                WordPair(id="8", english_word="please", translated_word="por favor", target_language="Portuguese"),
                WordPair(id="9", english_word="yes", translated_word="sim", target_language="Portuguese"),
                WordPair(id="10", english_word="no", translated_word="não", target_language="Portuguese"),
            ]
        elif target_language.lower() in ["spanish", "es"]:
            return [
                WordPair(id="1", english_word="dog", translated_word="perro", target_language="Spanish"),
                WordPair(id="2", english_word="cat", translated_word="gato", target_language="Spanish"),
                WordPair(id="3", english_word="house", translated_word="casa", target_language="Spanish"),
                WordPair(id="4", english_word="water", translated_word="agua", target_language="Spanish"),
                WordPair(id="5", english_word="hello", translated_word="hola", target_language="Spanish"),
            ]
        elif target_language.lower() in ["belarusian", "be", "belarus"]:
            return [
                WordPair(id="1", english_word="dog", translated_word="сабака", target_language="Belarusian"),
                WordPair(id="2", english_word="cat", translated_word="кот", target_language="Belarusian"),
                WordPair(id="3", english_word="house", translated_word="дом", target_language="Belarusian"),
                WordPair(id="4", english_word="water", translated_word="вода", target_language="Belarusian"),
                WordPair(id="5", english_word="hello", translated_word="прывітанне", target_language="Belarusian"),
                WordPair(id="6", english_word="goodbye", translated_word="да пабачэння", target_language="Belarusian"),
                WordPair(id="7", english_word="thank you", translated_word="дзякуй", target_language="Belarusian"),
                WordPair(id="8", english_word="please", translated_word="калі ласка", target_language="Belarusian"),
                WordPair(id="9", english_word="yes", translated_word="так", target_language="Belarusian"),
                WordPair(id="10", english_word="no", translated_word="не", target_language="Belarusian"),
                WordPair(id="11", english_word="friend", translated_word="сябар", target_language="Belarusian"),
                WordPair(id="12", english_word="love", translated_word="любов", target_language="Belarusian"),
                WordPair(id="13", english_word="book", translated_word="кніга", target_language="Belarusian"),
                WordPair(id="14", english_word="sun", translated_word="сонца", target_language="Belarusian"),
                WordPair(id="15", english_word="moon", translated_word="месяц", target_language="Belarusian"),
            ]
        else:
            logger.warning(f"No fallback words available for {target_language}")
            return []
