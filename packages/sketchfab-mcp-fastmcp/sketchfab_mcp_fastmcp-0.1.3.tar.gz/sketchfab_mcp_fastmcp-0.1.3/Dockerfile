# Base image with Python
FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

# Builder stage to install dependencies
FROM base AS builder
WORKDIR /app

# Copy UV from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files and README.md first (for layer caching)
COPY pyproject.toml uv.lock README.md* ./

# Install dependencies into virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy the rest of the application code
COPY . .

# Final stage for runtime
FROM base AS runtime
WORKDIR /app

# Copy the virtual environment and app from builder
COPY --from=builder /app /app

# Expose port (adjust as needed)
EXPOSE 8000

# Command to run the MCP server (adjust 'main' to your entry point)
CMD ["python", "-m", "main"]