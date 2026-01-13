FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for piper
RUN apt-get update && apt-get install -y --no-install-recommends \
    libespeak-ng1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY quickcall_voiceover ./quickcall_voiceover/

# Install the package
RUN uv pip install --system .

# Create directories for models and output
RUN mkdir -p /app/models /app/output

# Set default directories
ENV MODELS_DIR=/app/models
ENV OUTPUT_DIR=/app/output

ENTRYPOINT ["quickcall-voiceover"]
CMD ["--help"]
