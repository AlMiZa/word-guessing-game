# Voice Agent Template

A real-time voice AI agent template demonstrating two LiveKit-powered voice applications:

1. **Compliment Battle** - Positive competitions where you out-compliment your opponent
2. **Word Game** - Vocabulary practice through voice translation

## Features

### Compliment Battle Mode

A voice agent that engages in positive compliment battles with two modes:

- **Attack Mode**: The agent delivers uplifting compliments immediately with genuine enthusiasm
- **Protect Mode**: The agent listens to your compliments first, then responds with heartfelt appreciation

The agent uses natural voice interaction, maintaining a warm, encouraging style while keeping verses concise.

### Word Game Mode

A vocabulary practice game where the agent speaks English words and you respond with translations in your target language:

- **Multiple Languages**: Portuguese, Spanish, French, Italian, German
- **Real-time Feedback**: Instant confirmation of correct/incorrect answers
- **Score Tracking**: Track your progress as you practice
- **Voice Interaction**: Completely hands-free gameplay

Access the word game at `/word-game` when the application is running.

## Architecture

The application consists of three main services:

- **Web Service** (`services/web/`): Next.js frontend with LiveKit integration for real-time voice communication
- **Agent Service** (`services/agent/`): Python-based voice AI agent using LiveKit Agents framework
- **Nginx**: Reverse proxy for routing requests only used in production for SSL certificates

### Tech Stack

**Frontend:**
- Next.js with TypeScript
- React Components for UI
- LiveKit Client SDK

**Agent:**
- Python 3.13+
- LiveKit Agents SDK
- Supabase (for word game database)

## Prerequisites

- Docker and Docker Compose
- LiveKit account and credentials ([Get started](https://livekit.io))
- Supabase account (optional, for word game - fallback words available)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd voice-agent-template
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# LiveKit (required for both modes)
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-project.livekit.cloud

# Supabase (optional for word game)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here
```

### 3. Set Up Supabase (Optional)

If using Supabase for the word game:

1. Create a project at [supabase.com](https://supabase.com)
2. Run the schema from `services/agent/supabase/schema.sql` in the SQL Editor
3. Copy your credentials to `.env`

See `services/agent/supabase/README.md` for detailed instructions.

### 4. Run the Application

**Development Mode:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

The web interface will be available at `http://localhost:3000`

## How to Use

### Compliment Battle

1. Navigate to `http://localhost:3000` (home page)
2. **Join a Room**: Connect to the voice session
3. **Choose Your Mode**:
   - **Attack**: Click to have the agent deliver compliments to you
   - **Protect**: Click, then share your compliments - the agent will listen and respond
4. **Add Custom Instructions**: Optionally provide specific themes for the agent's compliments

### Word Game

1. Navigate to `http://localhost:3000/word-game`
2. Click "START PRACTICING" to connect
3. Select your target language
4. Click "START GAME"
5. Listen to the English word and speak the translation
6. Get instant feedback and continue practicing!

See `WORD-GAME-TESTING.md` for comprehensive testing instructions.

## Deployment

This project uses GitHub Actions for automated deployment to a production server.

### Required GitHub Secrets

Before deploying, configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Server Credentials
- **`SERVER_IP`**: Your server's IP address
- **`SERVER_PASSWORD`**: Your server's root password

#### GitHub Container Registry
- **`CR_PAT`**: GitHub Personal Access Token with `read:packages` and `write:packages` permissions

#### LiveKit Credentials
- **`LIVEKIT_URL`**: Your LiveKit server URL
- **`LIVEKIT_API_KEY`**: Your LiveKit API key
- **`LIVEKIT_API_SECRET`**: Your LiveKit API secret

#### Supabase Credentials (for Word Game)
- **`SUPABASE_URL`**: Your Supabase project URL
- **`SUPABASE_KEY`**: Your Supabase service role key

**Important**: Use separate LiveKit projects for development and production.

### Deployment Steps

#### 1. Set Up Your Server (One-time)

Run the "Setup Server" workflow manually from the Actions tab.

#### 2. Deploy to Production

```bash
git push origin main
```

Deployment happens automatically on push to `main`.

## Documentation

- `CLAUDE.md` - Detailed architecture and development guide
- `WORD-GAME-TESTING.md` - Word game testing checklist
- `services/agent/supabase/README.md` - Supabase setup guide

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
