FROM python:3.10-slim

# definition of work directory
WORKDIR /app

# copy files in the container
COPY . /app

# install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install --no-cache-dir fastapi uvicorn asyncpg psycopg2-binary confluent-kafka
RUN pip install "uvicorn[standard]" websockets  # Ajout du support WebSocket

# expose the port 8000
EXPOSE 8000

# run the script with uvicorn
CMD ["sh", "-c", "sleep 10 && uvicorn consumer:app --host 0.0.0.0 --port 8000 --reload"]