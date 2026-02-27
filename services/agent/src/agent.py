import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AgentSession,
    JobContext,
    JobProcess,
    JobRequest,
    MetricsCollectedEvent,
    RoomIO,
    WorkerOptions,
    cli,
    metrics,
    inference,
)
from livekit.plugins import silero

from word_game_agent import WordGameAgent, create_word_game_agent

logger = logging.getLogger("agent")

load_dotenv(".env.local")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline with VAD for word game
    # Using Deepgram Nova-2 for multilingual speech recognition
    session = AgentSession(
        # Speech-to-text (STT) - Deepgram Nova-2 supports multilingual input
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt="deepgram/nova-2",
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm="openai/gpt-4.1-mini",
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=inference.TTS(
            model="cartesia/sonic-2",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            language="en"
        ),
        # Use VAD for automatic turn detection in word game mode
        turn_detection="auto",
    )

    # Set up RoomIO for managing participant audio
    room_io = RoomIO(session, room=ctx.room)
    await room_io.start()

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Create the word game agent instance with room reference
    # Pass room so agent can send score updates via data channel
    word_game_agent = create_word_game_agent(target_language="Portuguese", room=ctx.room)

    # Enable input audio BEFORE starting session
    # This ensures the agent can hear the user from the beginning
    session.input.set_audio_enabled(True)

    # Start the session
    await session.start(agent=word_game_agent)

    @ctx.room.local_participant.register_rpc_method("start_game")
    async def start_game(data: rtc.RpcInvocationData):
        logger.info(f"start_game called by {data.caller_identity} with language: {data.payload}")

        # Get the target language from payload
        target_language = data.payload or "Portuguese"

        # Start the game and get the greeting message
        greeting = word_game_agent.start_game(target_language)

        # Say the greeting to start the game
        session.generate_reply(user_input=f"START_GAME:{target_language}")

        logger.info(f"Word game started for {target_language}")

    @ctx.room.local_participant.register_rpc_method("stop_game")
    async def stop_game(data: rtc.RpcInvocationData):
        logger.info(f"stop_game called by {data.caller_identity}")

        # Reset the game state
        word_game_agent.game_state.reset()

        # Say goodbye
        session.generate_reply(user_input="Thanks for practicing! Goodbye!")

        logger.info("Word game stopped")

    @ctx.room.local_participant.register_rpc_method("skip_question")
    async def skip_question(data: rtc.RpcInvocationData):
        logger.info(f"skip_question called by {data.caller_identity}")

        # Move to the next word without incrementing score (user must answer correctly)
        if word_game_agent.game_state.current_word:
            word_game_agent.game_state.total_words += 1
            logger.info(f"Skipped to next question. Score: {word_game_agent.game_state.score}/{word_game_agent.game_state.total_words}")

        # Move to the next word and generate the response
        next_word = word_game_agent._get_next_word()
        response = (
            f"Let's move to the next word. "
            f"Your score is {word_game_agent.game_state.score} out of {word_game_agent.game_state.total_words}. "
            f"How do you say '{next_word.english_word}' in {word_game_agent.target_language}?"
        )

        # Say the next question
        session.generate_reply(user_input=f"SKIP_QUESTION:{response}")

        logger.info("Skipped to next question")

    # Join the room and connect to the user
    await ctx.connect()


async def handle_request(request: JobRequest) -> None:
    await request.accept(
        identity="word-game-agent",
        attributes={"mode": "word-game"},
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, request_fnc=handle_request, prewarm_fnc=prewarm))
