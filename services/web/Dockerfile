# Base stage with dependencies
FROM node:22-alpine AS base
RUN apk add --no-cache libc6-compat curl

# Install pnpm
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Development stage
FROM base AS development

WORKDIR /app

# Copy source code
COPY . .

ENV NODE_ENV=development

EXPOSE 3000

# Run dev server with hot reload
CMD ["pnpm", "dev"]

# Production builder stage
FROM base AS builder

WORKDIR /app

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build the application
RUN pnpm build

# Production runner stage
FROM node:22-alpine AS production
RUN apk add --no-cache libc6-compat curl

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Set correct permissions
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
