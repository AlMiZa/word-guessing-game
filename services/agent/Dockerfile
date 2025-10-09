ARG PYTHON_VERSION=3.13.8
FROM python:${PYTHON_VERSION}-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create src directory to avoid uv failing
RUN mkdir -p src/

# Install dependencies
RUN uv sync --locked

# Development stage
FROM base AS development

WORKDIR /app

# Install watchfiles for hot reload
RUN uv pip install watchfiles

# Copy source code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Use entrypoint to download models at runtime, then start with hot reload
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "watchfiles", "--filter", "python", "uv run src/agent.py start", "src"]

# Production stage
FROM base AS production

# Create non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    user

WORKDIR /app

# Copy source code
COPY . .

# Make entrypoint executable and change ownership to non-privileged user
RUN chmod +x /app/entrypoint.sh && \
    chown -R user:user /app

USER user

# Use entrypoint to download models at runtime, then start the agent
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "src/agent.py", "start"]
