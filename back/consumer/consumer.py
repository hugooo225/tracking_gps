from confluent_kafka import Consumer
import json
import psycopg2
import time
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect



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

    # Stocker la WebSocket dans les connexions actives
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


db_config = {
    'host': 'localhost',       
    'port': '5432',            
    'dbname': 'gps_tracking_db',    
    'user': 'admin',            
    'password': '1234'       
}

cursor = None
connection = None


# execution 
if __name__ == "__main__" :

    conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "consumer-group-1",
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(conf)

    topic = 'coordinates'
    consumer.subscribe([topic])

    print(f"Consommateur abonné au topic : {topic}")

    try:
        # Connexion à la base de données PostgreSQL
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        print("Connexion réussie à PostgreSQL")


        insert_query = '''
        INSERT INTO coordonnees (IP, latitude, longitude)
        VALUES (%s, %s, %s);
        '''

        try:
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
                if active_connections.get(IP) :
                    active_connections.get(IP).send_text(json.dumps(data))

                record = (IP,latitude,longitude)
                cursor.execute(insert_query,record)
                connection.commit()
                print(f"Message enregistre : ( {IP} , {data['latitude']} , {data['longitude']} ) (Partition: {msg.partition()}, Offset: {msg.offset()})")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Arrêt du consommateur.")
        finally:
            consumer.close()
    except (Exception, psycopg2.Error) as error:
        print("Erreur lors de l'opération PostgreSQL :", error)
    finally:
        
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connexion PostgreSQL fermée")