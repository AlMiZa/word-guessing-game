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
        lang_lower = target_language.lower()

        if lang_lower in ["portuguese", "pt"]:
            return [
                WordPair(id="pt1", english_word="hello", translated_word="olá", target_language="Portuguese"),
                WordPair(id="pt2", english_word="goodbye", translated_word="adeus", target_language="Portuguese"),
                WordPair(id="pt3", english_word="thank you", translated_word="obrigado", target_language="Portuguese"),
                WordPair(id="pt4", english_word="please", translated_word="por favor", target_language="Portuguese"),
                WordPair(id="pt5", english_word="yes", translated_word="sim", target_language="Portuguese"),
                WordPair(id="pt6", english_word="no", translated_word="não", target_language="Portuguese"),
                WordPair(id="pt7", english_word="dog", translated_word="cachorro", target_language="Portuguese"),
                WordPair(id="pt8", english_word="cat", translated_word="gato", target_language="Portuguese"),
                WordPair(id="pt9", english_word="house", translated_word="casa", target_language="Portuguese"),
                WordPair(id="pt10", english_word="water", translated_word="água", target_language="Portuguese"),
                WordPair(id="pt11", english_word="food", translated_word="comida", target_language="Portuguese"),
                WordPair(id="pt12", english_word="book", translated_word="livro", target_language="Portuguese"),
                WordPair(id="pt13", english_word="sun", translated_word="sol", target_language="Portuguese"),
                WordPair(id="pt14", english_word="moon", translated_word="lua", target_language="Portuguese"),
                WordPair(id="pt15", english_word="friend", translated_word="amigo", target_language="Portuguese"),
                WordPair(id="pt16", english_word="love", translated_word="amor", target_language="Portuguese"),
                WordPair(id="pt17", english_word="happy", translated_word="feliz", target_language="Portuguese"),
                WordPair(id="pt18", english_word="sad", translated_word="triste", target_language="Portuguese"),
                WordPair(id="pt19", english_word="big", translated_word="grande", target_language="Portuguese"),
                WordPair(id="pt20", english_word="small", translated_word="pequeno", target_language="Portuguese"),
            ]
        elif lang_lower in ["spanish", "es"]:
            return [
                WordPair(id="es1", english_word="hello", translated_word="hola", target_language="Spanish"),
                WordPair(id="es2", english_word="goodbye", translated_word="adiós", target_language="Spanish"),
                WordPair(id="es3", english_word="thank you", translated_word="gracias", target_language="Spanish"),
                WordPair(id="es4", english_word="please", translated_word="por favor", target_language="Spanish"),
                WordPair(id="es5", english_word="yes", translated_word="sí", target_language="Spanish"),
                WordPair(id="es6", english_word="no", translated_word="no", target_language="Spanish"),
                WordPair(id="es7", english_word="dog", translated_word="perro", target_language="Spanish"),
                WordPair(id="es8", english_word="cat", translated_word="gato", target_language="Spanish"),
                WordPair(id="es9", english_word="house", translated_word="casa", target_language="Spanish"),
                WordPair(id="es10", english_word="water", translated_word="agua", target_language="Spanish"),
                WordPair(id="es11", english_word="food", translated_word="comida", target_language="Spanish"),
                WordPair(id="es12", english_word="book", translated_word="libro", target_language="Spanish"),
                WordPair(id="es13", english_word="sun", translated_word="sol", target_language="Spanish"),
                WordPair(id="es14", english_word="moon", translated_word="luna", target_language="Spanish"),
                WordPair(id="es15", english_word="friend", translated_word="amigo", target_language="Spanish"),
                WordPair(id="es16", english_word="love", translated_word="amor", target_language="Spanish"),
                WordPair(id="es17", english_word="happy", translated_word="feliz", target_language="Spanish"),
                WordPair(id="es18", english_word="sad", translated_word="triste", target_language="Spanish"),
                WordPair(id="es19", english_word="big", translated_word="grande", target_language="Spanish"),
                WordPair(id="es20", english_word="small", translated_word="pequeño", target_language="Spanish"),
            ]
        elif lang_lower in ["french", "fr"]:
            return [
                WordPair(id="fr1", english_word="hello", translated_word="bonjour", target_language="French"),
                WordPair(id="fr2", english_word="goodbye", translated_word="au revoir", target_language="French"),
                WordPair(id="fr3", english_word="thank you", translated_word="merci", target_language="French"),
                WordPair(id="fr4", english_word="please", translated_word="s'il vous plaît", target_language="French"),
                WordPair(id="fr5", english_word="yes", translated_word="oui", target_language="French"),
                WordPair(id="fr6", english_word="no", translated_word="non", target_language="French"),
                WordPair(id="fr7", english_word="dog", translated_word="chien", target_language="French"),
                WordPair(id="fr8", english_word="cat", translated_word="chat", target_language="French"),
                WordPair(id="fr9", english_word="house", translated_word="maison", target_language="French"),
                WordPair(id="fr10", english_word="water", translated_word="eau", target_language="French"),
                WordPair(id="fr11", english_word="food", translated_word="nourriture", target_language="French"),
                WordPair(id="fr12", english_word="book", translated_word="livre", target_language="French"),
                WordPair(id="fr13", english_word="sun", translated_word="soleil", target_language="French"),
                WordPair(id="fr14", english_word="moon", translated_word="lune", target_language="French"),
                WordPair(id="fr15", english_word="friend", translated_word="ami", target_language="French"),
                WordPair(id="fr16", english_word="love", translated_word="amour", target_language="French"),
                WordPair(id="fr17", english_word="happy", translated_word="heureux", target_language="French"),
                WordPair(id="fr18", english_word="sad", translated_word="triste", target_language="French"),
                WordPair(id="fr19", english_word="big", translated_word="grand", target_language="French"),
                WordPair(id="fr20", english_word="small", translated_word="petit", target_language="French"),
            ]
        elif lang_lower in ["italian", "it"]:
            return [
                WordPair(id="it1", english_word="hello", translated_word="ciao", target_language="Italian"),
                WordPair(id="it2", english_word="goodbye", translated_word="arrivederci", target_language="Italian"),
                WordPair(id="it3", english_word="thank you", translated_word="grazie", target_language="Italian"),
                WordPair(id="it4", english_word="please", translated_word="per favore", target_language="Italian"),
                WordPair(id="it5", english_word="yes", translated_word="sì", target_language="Italian"),
                WordPair(id="it6", english_word="no", translated_word="no", target_language="Italian"),
                WordPair(id="it7", english_word="dog", translated_word="cane", target_language="Italian"),
                WordPair(id="it8", english_word="cat", translated_word="gatto", target_language="Italian"),
                WordPair(id="it9", english_word="house", translated_word="casa", target_language="Italian"),
                WordPair(id="it10", english_word="water", translated_word="acqua", target_language="Italian"),
                WordPair(id="it11", english_word="food", translated_word="cibo", target_language="Italian"),
                WordPair(id="it12", english_word="book", translated_word="libro", target_language="Italian"),
                WordPair(id="it13", english_word="sun", translated_word="sole", target_language="Italian"),
                WordPair(id="it14", english_word="moon", translated_word="luna", target_language="Italian"),
                WordPair(id="it15", english_word="friend", translated_word="amico", target_language="Italian"),
                WordPair(id="it16", english_word="love", translated_word="amore", target_language="Italian"),
                WordPair(id="it17", english_word="happy", translated_word="felice", target_language="Italian"),
                WordPair(id="it18", english_word="sad", translated_word="triste", target_language="Italian"),
                WordPair(id="it19", english_word="big", translated_word="grande", target_language="Italian"),
                WordPair(id="it20", english_word="small", translated_word="piccolo", target_language="Italian"),
            ]
        elif lang_lower in ["german", "de"]:
            return [
                WordPair(id="de1", english_word="hello", translated_word="hallo", target_language="German"),
                WordPair(id="de2", english_word="goodbye", translated_word="auf wiedersehen", target_language="German"),
                WordPair(id="de3", english_word="thank you", translated_word="danke", target_language="German"),
                WordPair(id="de4", english_word="please", translated_word="bitte", target_language="German"),
                WordPair(id="de5", english_word="yes", translated_word="ja", target_language="German"),
                WordPair(id="de6", english_word="no", translated_word="nein", target_language="German"),
                WordPair(id="de7", english_word="dog", translated_word="hund", target_language="German"),
                WordPair(id="de8", english_word="cat", translated_word="katze", target_language="German"),
                WordPair(id="de9", english_word="house", translated_word="haus", target_language="German"),
                WordPair(id="de10", english_word="water", translated_word="wasser", target_language="German"),
                WordPair(id="de11", english_word="food", translated_word="essen", target_language="German"),
                WordPair(id="de12", english_word="book", translated_word="buch", target_language="German"),
                WordPair(id="de13", english_word="sun", translated_word="sonne", target_language="German"),
                WordPair(id="de14", english_word="moon", translated_word="mond", target_language="German"),
                WordPair(id="de15", english_word="friend", translated_word="freund", target_language="German"),
                WordPair(id="de16", english_word="love", translated_word="liebe", target_language="German"),
                WordPair(id="de17", english_word="happy", translated_word="glücklich", target_language="German"),
                WordPair(id="de18", english_word="sad", translated_word="traurig", target_language="German"),
                WordPair(id="de19", english_word="big", translated_word="groß", target_language="German"),
                WordPair(id="de20", english_word="small", translated_word="klein", target_language="German"),
            ]
        elif lang_lower in ["belarusian", "be", "belarus"]:
            return [
                WordPair(id="be1", english_word="hello", translated_word="прывітанне", target_language="Belarusian"),
                WordPair(id="be2", english_word="goodbye", translated_word="да пабачэння", target_language="Belarusian"),
                WordPair(id="be3", english_word="thank you", translated_word="дзякуй", target_language="Belarusian"),
                WordPair(id="be4", english_word="please", translated_word="калі ласка", target_language="Belarusian"),
                WordPair(id="be5", english_word="yes", translated_word="так", target_language="Belarusian"),
                WordPair(id="be6", english_word="no", translated_word="не", target_language="Belarusian"),
                WordPair(id="be7", english_word="dog", translated_word="сабака", target_language="Belarusian"),
                WordPair(id="be8", english_word="cat", translated_word="кот", target_language="Belarusian"),
                WordPair(id="be9", english_word="house", translated_word="дом", target_language="Belarusian"),
                WordPair(id="be10", english_word="water", translated_word="вода", target_language="Belarusian"),
                WordPair(id="be11", english_word="food", translated_word="ежа", target_language="Belarusian"),
                WordPair(id="be12", english_word="book", translated_word="кніга", target_language="Belarusian"),
                WordPair(id="be13", english_word="sun", translated_word="сонца", target_language="Belarusian"),
                WordPair(id="be14", english_word="moon", translated_word="месяц", target_language="Belarusian"),
                WordPair(id="be15", english_word="friend", translated_word="сябар", target_language="Belarusian"),
                WordPair(id="be16", english_word="love", translated_word="любов", target_language="Belarusian"),
                WordPair(id="be17", english_word="happy", translated_word="шчаслівы", target_language="Belarusian"),
                WordPair(id="be18", english_word="sad", translated_word="сумны", target_language="Belarusian"),
                WordPair(id="be19", english_word="big", translated_word="вялікі", target_language="Belarusian"),
                WordPair(id="be20", english_word="small", translated_word="малы", target_language="Belarusian"),
            ]
        else:
            logger.warning(f"No fallback words available for {target_language}")
            return []
