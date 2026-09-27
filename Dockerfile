FROM python:3.11-slim

# System packages needed by:
#   azure-cognitiveservices-speech → libasound2t64, libssl, libgstreamer
#   faiss-cpu                      → libgomp1
#   pydub / ffmpeg                 → ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libasound2t64 \
    libgomp1 \
    libssl3 \
    libgstreamer1.0-0 \
    ffmpeg \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies with longer timeout for large packages
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

# Copy application code
COPY . .

# Create persistent data directory for SQLite
RUN mkdir -p /data

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
