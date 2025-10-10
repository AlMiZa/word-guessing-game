# AI Complimentary Rap Battle Voice Agent

A real-time voice AI agent application that participates in complimentary rap battles. Unlike traditional rap battles, this agent specializes in delivering kind, uplifting compliments and praise through creative wordplay, metaphors, and rhythmic flow. Battle your opponent with kindness - the goal is to out-compliment them!

## Overview

This project demonstrates a LiveKit-powered voice agent that engages in positive rap battles with two modes:

- **Attack Mode**: The agent delivers uplifting compliments immediately with genuine enthusiasm and positivity
- **Protect Mode**: The agent listens to your compliments first, then responds with even more heartfelt appreciation

The agent uses natural voice interaction, maintaining a warm, encouraging style while keeping verses concise and under 20 seconds for quick-fire rounds of kindness.

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

## Prerequisites

- Docker and Docker Compose
- LiveKit account and credentials ([Get started](https://livekit.io))

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

Edit `.env` and add your LiveKit credentials:

```env
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### 3. Run the Application

**Development Mode:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

The web interface will be available at `http://localhost:3000`

## How to Battle

Once the application is running:

1. **Join a Room**: Connect to the voice session through the web interface
2. **Choose Your Mode**:
   - **Attack**: Click the attack button to have the agent deliver compliments to you
   - **Protect**: Click the protect button, then share your compliments - the agent will listen and respond
3. **Add Custom Instructions**: Optionally provide specific themes or instructions for the agent's compliments

## Deployment

This project uses GitHub Actions for automated deployment to a production server. The deployment process is designed for workshop participants at TechSpot week.

### Workshop Information

This agent was originally created for the AI Agents TechSpot workshop happening in Warsaw on October 15th. If you're a workshop participant and need a server for deployment, you can ask the organizers for a promo code to get a free server from our hosting partner **is*hosting**.

- Workshop Details: [https://onthespotdev.com/techspot/ai-agents-techpot-uhub](https://onthespotdev.com/techspot/ai-agents-techpot-uhub)
- Hosting Partner: [https://ishosting.com/](https://ishosting.com/)


### Required GitHub Secrets

Before deploying, you need to configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

#### Server Credentials
- **`SERVER_IP`**: Your server's IP address
- **`SERVER_PASSWORD`**: Your server's root password


#### GitHub Container Registry
- **`CR_PAT`**: GitHub Personal Access Token (classic) with `read:packages` and `write:packages` permissions
  - Create one here: [GitHub Personal Access Tokens](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic)
  - Note: Author prefers using a classic token for easier setup

#### LiveKit Credentials
- **`LIVEKIT_URL`**: Your LiveKit server URL (e.g., `wss://your-project.livekit.cloud`)
- **`LIVEKIT_API_KEY`**: Your LiveKit API key
- **`LIVEKIT_API_SECRET`**: Your LiveKit API secret

**Important**: Use separate LiveKit projects (with different API keys) for development and production environments. This prevents interference between environments and makes debugging easier.

### Deployment Steps

#### 1. Set Up Your Server (One-time)

Run the "Setup Server" workflow manually to configure your server with Docker, Docker Compose, and other dependencies:

1. Go to **Actions** tab in your GitHub repository
2. Select **Setup Server** workflow
3. Click **Run workflow**
4. Wait for the setup to complete (typically 5-10 minutes)

This workflow will:
- Install Docker and Docker Compose
- Configure swap space
- Initialize Docker Swarm
- Log in to GitHub Container Registry
- Create project directories

#### 2. Deploy to Production

Deployment happens automatically on every push to the `main` branch:

```bash
git push origin main
```

The deployment workflow will:
1. Build Docker images for all services (agent, web, nginx)
2. Push images to GitHub Container Registry
3. Deploy the stack to your production server
4. Configure SSL certificates via Nginx

#### 3. Monitor Deployment

Check the deployment status in the **Actions** tab of your GitHub repository. The deployment typically takes 5-10 minutes.

### Deployment Architecture

The production deployment uses:
- **Docker Swarm** for orchestration
- **GitHub Container Registry** for image storage
- **Nginx** as reverse proxy with self-signed SSL support
- Separate environment configurations for each service

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
