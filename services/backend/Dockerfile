FROM python:3.13

WORKDIR /app

# Kopiere die benötigten Ordner in den "service"-Ordner
COPY services/backend/ backend/

RUN pip install --no-cache-dir -r backend/requirements.txt

# Füge den Data-Ordner dem PYTHONPATH hinzu, damit Python die Module dort findet
ENV PYTHONPATH="/app/data:${PYTHONPATH}"

EXPOSE 8000
