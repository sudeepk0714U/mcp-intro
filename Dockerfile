FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Verify key dependencies
RUN python -c "import langchain; print('langchain OK')"
RUN python -c "import paramiko; print('paramiko OK')"
RUN python -c "import langgraph; print('langgraph OK')"

# Copy project files
COPY . .

# Create required directories
RUN mkdir -p /app/projects /app/keys

# Set permissions for keys directory
RUN chmod 700 /app/keys

EXPOSE 8000

CMD ["python", "scout/client.py"]