"""
Word Game Agent - Voice-powered vocabulary practice game.

A LiveKit agent that quizzes users on word translations in their target language.
The agent speaks English words and the player responds by saying the translation.
"""

import logging
import random
import json
from typing import Optional
from dataclasses import dataclass, field

from livekit.agents import Agent, JobContext
from livekit.agents.llm import ChatContext, ChatMessage
from textwrap import dedent

from supabase_client import SupabaseWordService, WordPair

# Data channel payload for sending score updates to frontend
SCORE_DATA_CHANNEL = "word_game_score"

logger = logging.getLogger("agent")


WORD_GAME_PROMPT = dedent("""
    You are a friendly and encouraging language learning assistant for WordPan.
    Your role is to help users practice vocabulary in their target language through a word guessing game.

    GAME RULES:
    - You will say an English word and ask the user to translate it to their target language
    - Listen carefully to their answer
    - If correct: Celebrate with enthusiasm ("That's right!", "Perfect!", "Excellent!") and move to the next word
    - If incorrect: Be encouraging, reveal the correct answer, and continue ("Not quite! The word is X. Let's try another!")
    - Keep responses brief and conversational (under 10 seconds)

    SPEECH STYLE:
    - Be warm, patient, and supportive
    - Speak clearly at a moderate pace
    - Use simple language appropriate for language learners
    - Celebrate successes with genuine enthusiasm
    - Be encouraging even when they make mistakes

    CURRENT GAME STATE will be provided in each turn:
    - Target language
    - Current English word
    - Correct translation
    - User's current score

    EXAMPLE INTERACTIONS:
    User: "olá"
    Agent: "That's correct! 'Hello' in Portuguese is 'olá'. Great job! Let's continue. How do you say 'dog' in Portuguese?"

    User: "perro"
    Agent: "Not quite! 'Dog' in Portuguese is 'cachorro'. Don't worry, you'll get it! Let's try the next one. How do you say 'cat' in Portuguese?"

    Remember: Keep it fun, encouraging, and keep the game moving!
""")


@dataclass
class GameState:
    """Tracks the state of the word guessing game."""
    is_active: bool = False
    target_language: str = "Portuguese"
    score: int = 0
    total_words: int = 0
    current_word: Optional[WordPair] = None
    word_history: list[WordPair] = field(default_factory=list)

    def reset(self, target_language: str = "Portuguese") -> None:
        """Reset the game state for a new game."""
        self.is_active = True
        self.target_language = target_language
        self.score = 0
        self.total_words = 0
        self.current_word = None
        self.word_history = []

    def get_accuracy(self) -> float:
        """Calculate the accuracy percentage."""
        if self.total_words == 0:
            return 0.0
        return (self.score / self.total_words) * 100


class WordGameAgent(Agent):
    """
    Voice agent for the WordPan word guessing game.

    The agent quizzes users on vocabulary by speaking English words
    and listening for the correct translation in the target language.
    """

    def __init__(
        self,
        target_language: str = "Portuguese",
        word_service: Optional[SupabaseWordService] = None,
        room=None
    ) -> None:
        """
        Initialize the WordGameAgent.

        Args:
            target_language: The target language for translations (default: "Portuguese")
            word_service: Optional SupabaseWordService for fetching words
            room: Optional LiveKit room reference for sending data messages
        """
        super().__init__(instructions=WORD_GAME_PROMPT)
        self.target_language = target_language
        self.word_service = word_service or SupabaseWordService()
        self.game_state = GameState()
        self.word_pairs: list[WordPair] = []
        self.room = room  # Store room reference for sending data messages

        # Load word pairs on initialization
        self._load_word_pairs()

    def _load_word_pairs(self) -> None:
        """Load word pairs from the word service."""
        self.word_pairs = self.word_service.get_word_pairs(
            self.target_language,
            limit=100
        )
        logger.info(f"Loaded {len(self.word_pairs)} word pairs for {self.target_language}")

    def _send_score_update(self) -> None:
        """Send the current score to the frontend via data channel."""
        if self.room:
            try:
                import asyncio
                from livekit import rtc

                # Send score as JSON data
                score_data = {
                    "type": "score_update",
                    "score": self.game_state.score,
                    "total": self.game_state.total_words,
                }
                payload = json.dumps(score_data).encode('utf-8')

                # Send to all participants
                async def publish():
                    for participant in self.room.remote_participants.values():
                        await self.room.local_participant.publish_data(
                            payload,
                            identity=participant.identity
                        )

                # Run async
                asyncio.create_task(publish())
                logger.info(f"Sent score update: {score_data}")
            except Exception as e:
                logger.warning(f"Failed to send score update: {e}")

    def start_game(self, target_language: Optional[str] = None) -> str:
        """
        Start a new word guessing game.

        Args:
            target_language: Optional language override

        Returns:
            Greeting message to speak to the user
        """
        if target_language:
            self.target_language = target_language
            # Reload words if language changed
            self._load_word_pairs()

        self.game_state.reset(self.target_language)

        # Shuffle words for variety
        random.shuffle(self.word_pairs)

        logger.info(f"Starting word game for {self.target_language}")

        return (
            f"Welcome to WordPan! We're going to practice your {self.target_language} vocabulary today. "
            f"I'll say an English word, and you tell me how to say it in {self.target_language}. "
            f"Are you ready? Let's get started! "
            f"How do you say '{self._get_next_word().english_word}' in {self.target_language}?"
        )

    def _get_next_word(self) -> WordPair:
        """Get the next word from the shuffled list, cycling back if needed."""
        if not self.word_pairs:
            logger.warning("No word pairs available, using fallback")
            return WordPair(
                id="fallback",
                english_word="hello",
                translated_word="olá",
                target_language=self.target_language
            )

        if self.game_state.current_word is None:
            # First word
            self.game_state.current_word = self.word_pairs[0]
        else:
            # Find current word index and move to next
            current_idx = self.word_pairs.index(self.game_state.current_word)
            next_idx = (current_idx + 1) % len(self.word_pairs)
            self.game_state.current_word = self.word_pairs[next_idx]

        return self.game_state.current_word

    def evaluate_answer(self, user_answer: str) -> tuple[bool, str]:
        """
        Evaluate the user's answer against the correct translation.

        This method:
        1. Validates the game is active
        2. Normalizes both answers (lowercase, trim)
        3. Performs fuzzy matching via _is_answer_correct()
        4. Generates appropriate feedback based on correctness
        5. Advances to the next word
        6. Updates score tracking

        Args:
            user_answer: The user's spoken answer (raw text from STT)

        Returns:
            Tuple of (is_correct, response_message)
            - is_correct: Whether the answer was deemed correct
            - response_message: Full agent response to speak
        """
        if not self.game_state.is_active:
            return False, "The game hasn't started yet. Say 'start game' to begin!"

        current_word = self.game_state.current_word
        if not current_word:
            return False, "Let me think of a word for you..."

        # Normalize answers for comparison (lowercase, trim)
        # This ensures case-insensitive matching and removes extra whitespace
        user_normalized = user_answer.lower().strip()
        correct_normalized = current_word.translated_word.lower().strip()

        # Check for correct answer with fuzzy matching (allows articles, minor variations)
        is_correct = self._is_answer_correct(user_normalized, correct_normalized)

        if is_correct:
            self.game_state.score += 1
            self.game_state.total_words += 1
            accuracy = self.game_state.get_accuracy()
            next_word = self._get_next_word()

            # Send score update to frontend
            self._send_score_update()

            response = (
                f"That's correct! '{current_word.english_word}' in {self.target_language} "
                f"is '{current_word.translated_word}'. "
            )

            # Add encouragement based on streak
            if self.game_state.score >= 5 and self.game_state.score == self.game_state.total_words:
                response += f"You're on fire! {self.game_state.score} in a row! "
            elif self.game_state.score >= 3:
                response += "Great job! "

            response += (
                f"Your score is {self.game_state.score} out of {self.game_state.total_words}. "
                f"Let's continue! How do you say '{next_word.english_word}' in {self.target_language}?"
            )

            logger.info(f"Correct answer: '{user_answer}' = '{correct_normalized}'")
            return True, response
        else:
            # Incorrect answer
            self.game_state.total_words += 1
            next_word = self._get_next_word()

            # Send score update to frontend
            self._send_score_update()

            response = (
                f"Not quite! '{current_word.english_word}' in {self.target_language} "
                f"is '{current_word.translated_word}'. "
                f"Don't worry, you'll get it next time! "
                f"Your score is {self.game_state.score} out of {self.game_state.total_words}. "
                f"Let's try another one. How do you say '{next_word.english_word}' in {self.target_language}?"
            )

            logger.info(f"Incorrect answer: '{user_answer}' != '{correct_normalized}'")
            return False, response

    def _is_answer_correct(self, user_answer: str, correct_answer: str) -> bool:
        """
        Check if the user's answer is correct, allowing for minor variations.

        This implements fuzzy matching to handle common speech patterns:
        - Articles before words (e.g., "el gato" vs "gato")
        - Prepositions (e.g., "the cat" vs "cat")
        - Multiple word answers (e.g., "thank you" -> "obrigado")
        - Partial matches with Soundex-like similarity
        - Accented characters normalization

        Args:
            user_answer: Normalized user answer (lowercase, trimmed)
            correct_answer: Normalized correct answer (lowercase, trimmed)

        Returns:
            True if the answer is correct within tolerance
        """
        # Exact match - most common case
        if user_answer == correct_answer:
            return True

        # Remove common filler words and phrases that STT might add
        user_answer = self._remove_filler_words(user_answer)

        # Check again after removing filler words
        if user_answer == correct_answer:
            return True

        # For single-word answers, check if user said the word at the end
        # This handles cases where user might say "the cat" instead of "cat"
        # or include filler words before the actual answer
        if len(correct_answer.split()) == 1 and user_answer.endswith(correct_answer):
            return True

        # For multi-word answers, check if the correct answer appears in user's speech
        if len(correct_answer.split()) > 1:
            # Check if user said all the words of the correct answer in order
            correct_words = correct_answer.split()
            user_words = user_answer.split()

            # Check if correct words appear consecutively in user answer
            for i in range(len(user_words) - len(correct_words) + 1):
                if user_words[i:i+len(correct_words)] == correct_words:
                    return True

        # Check if user said a common article before the word
        # Supports Romance languages and Germanic languages
        articles = [
            "el ", "la ", "le ", "les ", "il ", "lo ", "o ", "a ", "os ", "as ",
            "un ", "une ", "der ", "die ", "das ", "ein ", "eine ", "і ", "ў "
        ]
        for article in articles:
            if user_answer == article + correct_answer:
                return True
            if user_answer == correct_answer.replace(" ", " " + article):
                return True

        # Check for partial match - if user got at least 70% of the characters right
        # This helps with pronunciation variations and STT errors
        if self._is_similar_enough(user_answer, correct_answer):
            return True

        return False

    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words that STT might include."""
        filler_words = [
            "the ", "a ", "an ", "is ", "it ", "it's ", "its ",
            "um ", "uh ", "eh ", "oh ", "like ", "so ",
            "isto é ", "é ", "o ", "a ", "os ", "as ",  # Portuguese
            "el ", "la ", "los ", "las ", "un ", "una ",  # Spanish
            "le ", "la ", "les ", "un ", "une ", "des ",  # French
            "il ", "lo ", "la ", "le ", "gli ", "un ", "uno ", "una ",  # Italian
            "der ", "die ", "das ", "ein ", "eine ",  # German
        ]

        result = text.lower()
        for filler in filler_words:
            # Only remove if at the start to avoid over-removing
            if result.startswith(filler):
                result = result[len(filler):]
                break

        return result.strip()

    def _is_similar_enough(self, answer1: str, answer2: str, threshold: float = 0.7) -> bool:
        """
        Check if two strings are similar enough using Levenshtein distance ratio.

        Args:
            answer1: First string to compare
            answer2: Second string to compare
            threshold: Minimum similarity ratio (0-1) to consider a match

        Returns:
            True if strings are similar enough
        """
        if not answer1 or not answer2:
            return False

        # For very short words, require exact match or very high similarity
        if len(answer1) <= 3 or len(answer2) <= 3:
            return answer1 == answer2

        # Calculate Levenshtein distance
        import unicodedata

        # Normalize unicode characters (handles accents)
        def normalize(s):
            return ''.join(
                c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn'
            )

        answer1_norm = normalize(answer1.lower())
        answer2_norm = normalize(answer2.lower())

        # Simple Levenshtein distance calculation
        m, n = len(answer1_norm), len(answer2_norm)

        # Quick check for very different lengths
        if abs(m - n) > max(m, n) * 0.5:
            return False

        # Use dynamic programming for distance calculation
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if answer1_norm[i-1] == answer2_norm[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

        max_len = max(m, n)
        similarity = 1 - (dp[m][n] / max_len)

        return similarity >= threshold

    async def on_user_turn_completed(
        self,
        turn_ctx: ChatContext,
        new_message: ChatMessage
    ) -> None:
        """
        Process the user's answer after they finish speaking.

        **CRITICAL CALLBACK**: This is where we intercept the LLM pipeline to:
        1. Evaluate the user's answer against the correct translation
        2. Generate our own feedback message (bypassing the LLM)
        3. Replace the message content that the TTS will speak

        This allows us to have complete control over the game flow without
        relying on the LLM to evaluate answers, ensuring consistent scoring
        and feedback.

        **Flow**: User speaks → VAD detects silence → This callback fires →
                  We evaluate and set response → TTS speaks our response

        Args:
            turn_ctx: The chat context with conversation history
            new_message: The user's message (transcribed speech)

        Raises:
            StopResponse: If user turn is empty, prevents agent from responding
        """
        logger.info(f"on_user_turn_completed called: game_active={self.game_state.is_active}, text_content={new_message.text_content}")

        if not self.game_state.is_active:
            # Game not started, let the LLM handle it (for general conversation)
            logger.info("Game not active, letting LLM handle the response")
            return

        if not new_message.text_content:
            # Empty turn (user said nothing or was silent), ignore
            logger.info("Empty user turn, ignoring")
            from livekit.agents.llm import StopResponse
            raise StopResponse()

        # Get the user's answer and evaluate it using our game logic
        user_answer = new_message.text_content
        is_correct, response = self.evaluate_answer(user_answer)

        # Update the message content with our evaluation response
        # This ensures the agent speaks our evaluated response
        new_message.content = response

        logger.info(f"Evaluated answer: {user_answer} -> {is_correct}")


def create_word_game_agent(target_language: str = "Portuguese", room=None) -> WordGameAgent:
    """
    Factory function to create a WordGameAgent.

    Args:
        target_language: The target language for the game
        room: Optional LiveKit room reference for sending data messages

    Returns:
        A configured WordGameAgent instance
    """
    word_service = SupabaseWordService()
    return WordGameAgent(
        target_language=target_language,
        word_service=word_service,
        room=room
    )
