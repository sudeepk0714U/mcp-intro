FROM python:3.13-slim

WORKDIR /app

# Install system dependencies and Node.js 20
RUN apt-get update && apt-get install -y \
    git \
    curl \
    openssh-client \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv (includes uvx)
RUN pip install --no-cache-dir uv

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Verify dependencies
RUN python -c "import langchain; print('langchain OK')"
RUN python -c "import paramiko; print('paramiko OK')"
RUN python -c "import langgraph; print('langgraph OK')"

# Copy application source
COPY . .

# Create required directories
RUN mkdir -p /app/projects /app/keys && \
    chmod 700 /app/keys

EXPOSE 8000

CMD ["python", "scout/client.py"]
