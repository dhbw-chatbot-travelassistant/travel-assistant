# Verwende ein leichtgewichtiges Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die requirements-Datei und installiere die Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Anwendungscodes in den Container
COPY . .

# Exponiere den Port, auf dem der Server läuft
EXPOSE 8000

# Starte den Uvicorn-Server, der deine FastAPI-App ausführt
CMD ["uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"]