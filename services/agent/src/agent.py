import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    JobRequest,
    MetricsCollectedEvent,
    RoomIO,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.llm import ChatContext, ChatMessage, StopResponse
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from textwrap import dedent

logger = logging.getLogger("agent")

load_dotenv(".env.local")

PROMPT=dedent("""
    You are a skilled rap battle competitor with sharp wit and quick comebacks. The user is interacting with you via voice in a rap battle format.
    Your style is energetic, confident, and creative. You use wordplay, metaphors, and rhythmic flow in your responses.
    Keep your verses concise, impactful, and under 20 seconds when speaking - think quick fire rounds, not long performances.
    Your responses should be spoken naturally without using emojis, asterisks, or other symbols.
    Stay clever and competitive but always keep it fun and respectful - no personal attacks or offensive content.
    When given custom instructions, incorporate them into your rap battle style and strategy.
    If you're attacking, deliver your verse immediately with confidence.
    If you're protecting, listen to your opponent first, then counter with your own bars.
""")


class Assistant(Agent):
    def __init__(self, custom_instructions: str = "") -> None:
        # Use custom instructions if provided, otherwise use default prompt
        instructions = custom_instructions if custom_instructions else PROMPT
        super().__init__(instructions=instructions)

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        # callback before generating a reply after user turn committed
        if not new_message.text_content:
            # for example, raise StopResponse to stop the agent from generating a reply
            logger.info("ignore empty user turn")
            raise StopResponse()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline with manual turn detection (push-to-talk)
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt="assemblyai/universal-streaming:en",
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm="openai/gpt-4.1-mini",
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        # Manual turn detection for push-to-talk mode
        # DO NOT include VAD - it will cause automatic turn completion
        turn_detection="manual",
        # Set extremely high min_endpointing_delay to prevent automatic turn completion on pauses
        # This ensures the agent ONLY responds when we explicitly call commit_user_turn()
        min_endpointing_delay=999999.0,  # Effectively disable automatic EOU detection
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

    # Start the session
    await session.start(agent=Assistant())

    # Disable input audio at the start (push-to-talk mode)
    session.input.set_audio_enabled(False)

    # Register RPC methods for listen/reply control
    @ctx.room.local_participant.register_rpc_method("start_listening")
    async def start_listening(data: rtc.RpcInvocationData):
        logger.info(f"start_listening called by {data.caller_identity}")
        # Clear any previous turn and start fresh
        session.interrupt()
        session.clear_user_turn()
        # listen to the caller if multi-user
        room_io.set_participant(data.caller_identity)
        session.input.set_audio_enabled(True)

    @ctx.room.local_participant.register_rpc_method("attack")
    async def attack(data: rtc.RpcInvocationData):
        logger.info(f"attack called by {data.caller_identity} with instructions: {data.payload}")
        # Clear any previous turn and interrupt
        session.interrupt()
        session.clear_user_turn()

        # Get custom instructions if provided
        instructions = data.payload or ""

        # Generate a reply with the custom instructions
        # This simulates user input and triggers the agent to respond
        user_message = f"Begin your attack! {instructions}" if instructions else "Begin your attack now!"

        # Use generate_reply to trigger the agent's response
        session.generate_reply(user_input=user_message)

    @ctx.room.local_participant.register_rpc_method("protect")
    async def protect(data: rtc.RpcInvocationData):
        logger.info(f"protect called by {data.caller_identity} with instructions: {data.payload}")
        # Clear any previous turn and interrupt
        session.interrupt()
        session.clear_user_turn()

        # Get custom instructions if provided
        instructions = data.payload or ""

        # Inject instructions as a silent message to guide the agent's defense strategy
        if instructions:
            # Generate a silent instruction that sets up the defense strategy
            session.generate_reply(user_input=f"Prepare to defend yourself. Your strategy: {instructions}. Now listen to your opponent.")

        # Start listening for the attacker
        room_io.set_participant(data.caller_identity)
        session.input.set_audio_enabled(True)

    @ctx.room.local_participant.register_rpc_method("stop_listening")
    async def stop_listening(data: rtc.RpcInvocationData):
        logger.info(f"stop_listening called by {data.caller_identity}")
        # DON'T disable audio here - we need the STT stream to remain open
        # so that commit_user_turn() can flush the buffer later
        # Just stop capturing new audio by doing nothing - the high min_endpointing_delay
        # prevents automatic turn completion
        pass

    @ctx.room.local_participant.register_rpc_method("reply")
    async def reply(data: rtc.RpcInvocationData):
        logger.info(f"reply called by {data.caller_identity}")
        # Disable audio (in case it's still enabled) and commit the turn
        session.input.set_audio_enabled(False)
        # Commit the user turn and generate a response
        session.commit_user_turn(
            # the timeout for the final transcript to be received after committing the user turn
            # increase this value if the STT is slow to respond
            transcript_timeout=10.0,
            # the duration of the silence to be appended to the STT to make it generate the final transcript
            stt_flush_duration=2.0,
        )

    # Join the room and connect to the user
    await ctx.connect()


async def handle_request(request: JobRequest) -> None:
    await request.accept(
        identity="ptt-agent",
        # this attribute communicates to frontend that we support PTT
        attributes={"push-to-talk": "1"},
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, request_fnc=handle_request, prewarm_fnc=prewarm))
