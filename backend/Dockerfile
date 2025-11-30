FROM python:3.13-slim

WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv first (rarely changes)
RUN pip install --no-cache-dir uv

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Create venv and install dependencies (cached unless deps change)
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --system -e .

# Copy application code (changes frequently, so last)
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
