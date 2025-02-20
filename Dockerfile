FROM python:3.11.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    python3-dev \
    espeak \
    espeak-ng \
    ffmpeg \
    libespeak1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"] 