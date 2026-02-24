# WordPan Voice Agent

Build a Voice-Powered Language Learning Game with LiveKit

# Overview

In this assignment, you will build a voice-powered word guessing game that helps users practice vocabulary in their target language. The game is played entirely through voice: a LiveKit voice agent speaks English words aloud and the player responds by saying the translation in their target language. The agent checks the answer, provides feedback, and keeps going.

This connects to your ongoing WordPan project. You must integrate the voice agent into your existing application.

Goal: Create a voice agent that quizzes you on word translations using LiveKit for real-time voice interaction. The agent should be integrated into a web interface where users can play the game.

## How the Game Works
- The game follows a simple loop:
- The agent greets the player and starts the game.
- The agent says an English word aloud ("How do you say 'cat' in Portuguese?").
- The player responds by speaking the translation ("gato").
- **If correct**: The agent confirms ("That's right! 'Cat' is 'gato'.") and moves to the next word.
- **If wrong**: The agent says it's incorrect and reveals the answer ("Not quite. 'Cat' in Portuguese is 'gato'. Let's try the next one.").
- The agent keeps going with the next word. The game continues until the player decides to stop.

### Example Conversation
- **Agent**: Welcome to WordPan! We're going to practice your Portuguese vocabulary today. Here we go! How do you say "dog" in Portuguese?
- **Player**: "Cachorro."
- **Agent**: That's correct! Great job. Next word: how do you say "house" in Portuguese?
- **Player**: "Morada."
- **Agent**: Not quite! "House" in Portuguese is "casa." Let's keep going. How do you say "water"?
- **Player**: "Água."
- **Agent**: Perfect! You're doing great. Next one...

## Requirements
### 1. Voice Agent (Backend)
Build a LiveKit voice agent that implements the word guessing game logic:
- Use the LiveKit Agents framework (Python).
- Configure a voice pipeline with STT (Speech-to-Text), LLM, and TTS (Text-to-Speech) providers of your choice.
- Have a word list with English words and their translations in a target language.
- Speak each English word and wait for the player's spoken response.
- Evaluate the player's answer (correct or incorrect) and respond accordingly.
- Keep the game going continuously — no fixed number of rounds.

### 2. Web Interface (Frontend)
Create a web page where users can play the voice word game:
- Use LiveKit's React components or JavaScript SDK to connect to the voice agent.
- Provide a "Start Game" button that connects the user to a LiveKit room and starts the agent session.
- Display an audio visualizer or agent state indicator so the player knows when the agent is speaking, listening, or thinking.

### 3. Integration
You must integrate the voice agent into your existing WordPan application. The agent should pull words from your Supabase word pairs database and become a natural part of your learning experience — a dedicated page where you can practice vocabulary through voice.
#### **Recommended**: Use the Voice Agent Template
One great way to approach this is to start from our voice-agent-template. As shown in the lecture, this template comes with a compliment battle agent as a demo — that's just an example to show the setup in action. The agent can be fully replaced with a default agent or your own custom one, so don't worry about the compliment battle logic. The value of the template is the architecture: a Next.js web frontend and a Python LiveKit agent worker, with Docker Compose configuration and Supabase access — all wired together and ready to go.
You can show this template to your coding agent (Cursor, Claude Code, etc.) and ask it to help you integrate the word game into the existing structure. The template gives you two services: a web service with a page where you talk to the agent, and a separate Python agent worker that runs the voice logic. Your job is to adapt the agent's instructions and game logic, add a game page to the frontend, and connect it to your word pairs in Supabase.
This is also a good exercise in working with a coding agent on a real integration task — figuring out the Docker setup, the service communication, and the environment variables is part of the learning.
This can be a bit challenging, especially if it's your first time working with real-time voice. If you run into issues or have questions, ask in Slack and we will help you work through it.

-----------
### Useful Links
LiveKit Agents Docs https://docs.livekit.io/agents/
Voice Agent Template (recommended starting point) https://github.com/GOMAN-AI/voice-agent-template
WordPan Spec https://github.com/GOMAN-AI/wordpan-spec
