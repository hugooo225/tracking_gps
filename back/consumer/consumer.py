from confluent_kafka import Consumer
import json
import psycopg2
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()

#@app.websocket("/ws/coordonnees/{IP}")


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