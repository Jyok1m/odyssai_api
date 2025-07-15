FROM --platform=$BUILDPLATFORM python:3.12.10-slim

WORKDIR /app

# Éviter les erreurs de build avec certains packages
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système utiles pour LangChain et Mongo
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN ["pip", "install", "-q", "--no-cache-dir", "-r", "requirements.txt"]

COPY . .

EXPOSE 5050

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5050", "main:app"]