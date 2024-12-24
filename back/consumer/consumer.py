from confluent_kafka import Consumer
import json
import psycopg2
import time
import asyncio
import asyncpg
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

DATABASE_URL = "postgresql://admin:1234@localhost:5432/gps_tracking_db"
active_connections = {}

async def get_last_coordonnees():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        query = """
            SELECT id, IP, latitude, longitude, date_heure
            FROM coordonnees
            ORDER BY date_heure DESC
            LIMIT 1;
        """
        result = await conn.fetchrow(query)
        await conn.close()
        return result
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return None

@app.websocket("/ws/coordonnees")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accepter la connexion WebSocket

    # Ajouter la connexion WebSocket aux connexions actives
    connection_id = id(websocket)  # Identifiant unique pour la connexion
    active_connections[connection_id] = websocket
    print(f"Nouvelle connexion WebSocket : {connection_id}")

    try:
        # Envoyer immédiatement la dernière coordonnée connue
        coordonnee = await get_last_coordonnees()
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
            await websocket.receive_text()  # Garder la connexion active
    except WebSocketDisconnect:
        print(f"Client {connection_id} déconnecté.")
        active_connections.pop(connection_id, None)


def consumer_kafka():
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'gps_tracking_db',
        'user': 'admin',
        'password': '1234'
    }

    cursor = None
    connection = None

    conf = {
        "bootstrap.servers": "kafka:9092",
        "group.id": "consumer-group-1",
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(conf)

    topic = 'coordinates'
    consumer.subscribe([topic])

    print(f"Consommateur abonné au topic : {topic}")

    try:
        # Connexion à PostgreSQL
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

            # Diffusion des données à toutes les connexions WebSocket
            for connection_id, websocket in list(active_connections.items()):
                try:
                    data_json = json.dumps({
                        "IP": IP,
                        "latitude": latitude,
                        "longitude": longitude
                    })
                    asyncio.run(websocket.send_text(data_json))
                except Exception as e:
                    print(f"Erreur lors de l'envoi au client {connection_id} : {e}")
                    active_connections.pop(connection_id, None)

            # Insertion dans la base de données
            record = (IP, latitude, longitude)
            cursor.execute(insert_query, record)
            connection.commit()
            print(f"Message enregistré : ( {IP} , {latitude} , {longitude} ) (Partition: {msg.partition()}, Offset: {msg.offset()})")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du consommateur.")
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de l'opération PostgreSQL :", error)
    finally:
        consumer.close()
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connexion PostgreSQL fermée")

@app.on_event("startup")
async def startup():
    threading.Thread(target=consumer_kafka, daemon=True).start()

