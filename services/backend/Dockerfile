FROM python:3.13

WORKDIR /app

# Kopiere die benötigten Ordner in den "service"-Ordner
COPY . backend/

RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000
