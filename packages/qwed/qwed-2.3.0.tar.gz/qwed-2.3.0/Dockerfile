FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install QWED and dependencies
RUN pip install --no-cache-dir -e .

# GitHub Action entrypoint script
COPY action_entrypoint.sh /action_entrypoint.sh
RUN chmod +x /action_entrypoint.sh

ENTRYPOINT ["/action_entrypoint.sh"]
