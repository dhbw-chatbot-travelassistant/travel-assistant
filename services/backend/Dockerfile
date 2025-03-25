# Verwende ein leichtgewichtiges Python-Image als Basis
FROM python:3.13

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die requirements-Datei und installiere die Abhängigkeiten
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Kopiere den Rest des Anwendungscodes in den Container
COPY backend/ ./backend/
COPY data/ ./data/

# Füge den Data-Ordner dem PYTHONPATH hinzu, damit Python die Module dort findet
ENV PYTHONPATH="/app/services/data:${PYTHONPATH}"

# Exponiere den Port, auf dem der Server läuft
EXPOSE 8000

# Starte den Uvicorn-Server, der deine FastAPI-App ausführt
CMD ["uvicorn", "backend:app", "--host", "127.0.0.1", "--port", "8000"]