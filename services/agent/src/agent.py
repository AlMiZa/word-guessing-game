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
    inference,
)
from livekit.agents.llm import ChatContext, ChatMessage, StopResponse
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from textwrap import dedent

logger = logging.getLogger("agent")

load_dotenv(".env.local")

PROMPT=dedent("""
    You are a uniquely kind and uplifting rap battle competitor who specializes in COMPLIMENTARY rap battles. The user is interacting with you via voice in a positive rap battle format.
    Your style is warm, encouraging, and genuinely appreciative. You use wordplay, metaphors, and rhythmic flow to deliver sincere compliments and praise.
    Keep your verses concise, heartfelt, and under 20 seconds when speaking - think quick fire rounds of kindness, not long performances.
    Your responses should be spoken naturally without using emojis, asterisks, or other symbols.
    Focus on highlighting your opponent's strengths, talents, and positive qualities with creative wordplay and genuine warmth.
    Celebrate their presence, acknowledge their skills, and make them feel valued through your rhymes.
    When given custom instructions, incorporate them into your complimentary rap battle style.
    If you're attacking, deliver uplifting compliments immediately with genuine enthusiasm and positivity.
    If you're protecting, listen to your opponent's kind words first, then respond with even more heartfelt compliments and appreciation.
    Remember: This is a battle of kindness - the goal is to out-compliment your opponent with creative, genuine praise!
""")


class Assistant(Agent):
    def __init__(self, custom_instructions: str = "", protect_instructions: str = "") -> None:
        # Use custom instructions if provided, otherwise use default prompt
        instructions = custom_instructions if custom_instructions else PROMPT
        super().__init__(instructions=instructions)
        self.protect_instructions = protect_instructions

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        # callback before generating a reply after user turn committed
        # If we have protect instructions, prepend them to the user's message
        if self.protect_instructions:
            logger.info(f"Applying protect instructions: {self.protect_instructions}")
            # Modify the user message to include defensive strategy
            original_text = new_message.text_content or ""
            enhanced_text = f"[Defensive Strategy: {self.protect_instructions}] User said: {original_text}"
            # Update the message content
            new_message.content = enhanced_text
            logger.info(f"Enhanced user message with protect instructions")
            # Clear the protect instructions after use
            self.protect_instructions = ""

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
        # tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        tts=inference.TTS(
            model="cartesia/sonic-2",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            language="en"
        ),
        # Manual turn detection for push-to-talk mode
        # DO NOT include VAD - it will cause automatic turn completion
        turn_detection="manual",
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

    # Create the assistant instance so we can modify it later
    assistant = Assistant()

    # Start the session
    await session.start(agent=assistant)

    # Disable input audio at the start (push-to-talk mode)
    session.input.set_audio_enabled(False)

    # Store VAD instance for protect mode
    vad = None

    @ctx.room.local_participant.register_rpc_method("attack")
    async def attack(data: rtc.RpcInvocationData):
        logger.info(f"attack called by {data.caller_identity} with instructions: {data.payload}")

        # Get custom instructions if provided
        instructions = data.payload or ""

        # Generate a reply with the custom instructions
        # This simulates user input and triggers the agent to respond
        user_message = f"Share your compliments! {instructions}" if instructions else "Share your kind words and compliments now!"

        # Use generate_reply to trigger the agent's response
        session.generate_reply(user_input=user_message)

    @ctx.room.local_participant.register_rpc_method("protect")
    async def protect(data: rtc.RpcInvocationData):
        nonlocal vad
        logger.info(f"protect called by {data.caller_identity} with instructions: {data.payload}")

        # Get custom instructions if provided
        instructions = data.payload or ""

        # Store the protect instructions in the assistant to be used when the turn is completed
        if instructions:
            assistant.protect_instructions = instructions
            logger.info(f"Stored protect instructions: {instructions}")

        # Switch to automatic turn detection with VAD for protect mode
        # This allows the agent to automatically respond after 5 seconds of silence
        if vad is None:
            vad = ctx.proc.userdata["vad"]

        # Update the session to use VAD with 5-second silence threshold
        session.input.turn_detector = vad
        # Set min_endpointing_delay to 3 seconds (3000ms)
        session.input.min_endpointing_delay = 3.0

        # Start listening for the attacker
        room_io.set_participant(data.caller_identity)
        session.input.set_audio_enabled(True)

        logger.info("Protect mode: VAD enabled with 3-second silence threshold")

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
