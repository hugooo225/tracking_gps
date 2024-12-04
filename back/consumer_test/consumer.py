import asyncio
from confluent_kafka import Consumer
import json
import psycopg2
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


app = FastAPI()

DATABASE_URL = "postgresql://admin:1234@localhost:5432/gps_tracking_db"
active_connections = {}

async def get_last_coordonnees_for_ip(IP: str):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        query = """
            SELECT id, IP, latitude, longitude, date_heure
            FROM coordonnees
            WHERE IP = $1
            ORDER BY date_heure DESC
            LIMIT 1;
        """
        result = await conn.fetchrow(query, IP)
        await conn.close()
        return result
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return None

@app.websocket("/ws/coordonnees/{IP}")
async def websocket_endpoint(websocket: WebSocket, IP: str):
    await websocket.accept()  # Accepter la connexion WebSocket
    active_connections[IP] = websocket

    try:
        # Envoyer immédiatement la dernière coordonnée
        coordonnee = await get_last_coordonnees_for_ip(IP)
        if coordonnee:
            coordonnee_json = {
                "id": coordonnee["id"],
                "IP": coordonnee["ip"].strip(),
                "latitude": float(coordonnee["latitude"]),
                "longitude": float(coordonnee["longitude"]),
                "date_heure": coordonnee["date_heure"].isoformat() if coordonnee["date_heure"] else None
            }
            await websocket.send_text(json.dumps(coordonnee_json))

        # Maintenir la connexion WebSocket ouverte
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"Client with IP {IP} disconnected.")
        active_connections.pop(IP, None)

async def kafka_consumer_task():
    conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "consumer-group-1",
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(conf)
    topic = 'coordinates'
    consumer.subscribe([topic])
    print(f"Consommateur abonné au topic : {topic}")

    db_config = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'gps_tracking_db',
        'user': 'admin',
        'password': '1234'
    }

    try:
        # Connexion à la base de données PostgreSQL
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        print("Connexion réussie à PostgreSQL")

        insert_query = '''
        INSERT INTO coordonnees (IP, latitude, longitude)
        VALUES (%s, %s, %s);
        '''

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur : {msg.error()}")
                continue
            data = json.loads(msg.value().decode('utf-8'))
            latitude = data['latitude']
            longitude = data['longitude']
            IP = msg.key().decode('utf-8')

            # Si un client WebSocket est connecté, envoyer les données
            if IP in active_connections:
                await active_connections[IP].send_text(json.dumps(data))

            # Insérer dans la base de données
            record = (IP, latitude, longitude)
            cursor.execute(insert_query, record)
            connection.commit()
            print(f"Message enregistré : ( {IP} , {latitude} , {longitude} )")

    except KeyboardInterrupt:
        print("Arrêt du consommateur Kafka.")
    finally:
        consumer.close()
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connexion PostgreSQL fermée")

# # Lancer FastAPI et le consommateur Kafka simultanément
# if __name__ == "__main__":
#     import uvicorn

#     async def main():
#         # Lancer les deux tâches
#         await asyncio.gather(
#             kafka_consumer_task(),  # Tâche Kafka
#             uvicorn.run(app, host="0.0.0.0", port=8000)  # Serveur FastAPI
#         )

#     asyncio.run(main())

async def startfastapi():
    """Démarre le serveur FastAPI dans un thread distinct."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loglevel="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Lance FastAPI et le consommateur Kafka en parallèle."""
    await asyncio.gather(
        kafka_consumer_task(),
        startfastapi()
    )

if __name__ == "__main":
    asyncio.run(main())