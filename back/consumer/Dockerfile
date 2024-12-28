# Dockerfile

# Utiliser une image Python officielle comme base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . /app

# Installer les dépendances système requises
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python directement
RUN pip install --no-cache-dir fastapi uvicorn asyncpg psycopg2-binary confluent-kafka
RUN pip install "uvicorn[standard]" websockets  # Ajout du support WebSocket

# Exposer le port utilisé par FastAPI
EXPOSE 8000

# Commande pour lancer le script avec uvicorn
CMD ["sh", "-c", "sleep 10 && uvicorn consumer:app --host 0.0.0.0 --port 8000 --reload"]