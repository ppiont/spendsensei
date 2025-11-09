# Use Bun image
FROM oven/bun:1 AS builder

WORKDIR /app

# Copy package files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Accept build-time environment variables
ARG PUBLIC_API_BASE_URL
ENV PUBLIC_API_BASE_URL=${PUBLIC_API_BASE_URL}

# Build the app (SvelteKit will embed PUBLIC_API_BASE_URL)
RUN bun run build

# Production stage - use Node.js for adapter-node
FROM node:20-slim

WORKDIR /app

# Copy built app and dependencies
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

# Expose port (Railway will set PORT env var)
EXPOSE 3000

# Start the app
CMD ["node", "build/index.js"]
