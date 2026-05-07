FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# System deps for chromadb / pydub / etc.
RUN apt-get update && apt-get install -y --no-install-recommends     gcc g++ libffi-dev libssl-dev ffmpeg     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure dirs exist
RUN mkdir -p /app/memory/data /app/logs

CMD ["python", "brain/agent.py"]
