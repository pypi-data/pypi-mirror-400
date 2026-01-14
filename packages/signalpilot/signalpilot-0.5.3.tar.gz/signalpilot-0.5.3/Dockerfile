# SignalPilot CLI - Development & Testing Docker Image
FROM python:3.12-slim

# Set UV to use copy mode instead of hardlinks (better for Docker)
ENV UV_LINK_MODE=copy

# Install system dependencies including uv via pip
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Create working directory
WORKDIR /workspace

# Copy the CLI source code
COPY . /app/sp-cli

# Install sp-cli in development mode
WORKDIR /app/sp-cli
RUN uv venv .venv && uv pip install -e ".[dev]"

# Add sp to PATH for easy access
ENV PATH="/app/sp-cli/.venv/bin:${PATH}"

# Create a test project directory
WORKDIR /root/SignalPilotHome

# Expose Jupyter Lab port
EXPOSE 9999

# Default command: open a bash shell
CMD ["/bin/bash"]
