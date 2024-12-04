from confluent_kafka import Consumer
import json
import psycopg2
import time
# Configuration de la connexion
db_config = {
    'host': 'localhost',        # Adresse de l'hôte (localhost pour un conteneur Docker mappé)
    'port': '5432',             # Port par défaut de PostgreSQL
    'dbname': 'tracking',    # Nom de la base de données
    'user': 'admin',            # Nom de l'utilisateur
    'password': 'secret'        # Mot de passe de l'utilisateur
}

cursor = None
connection = None


# execution 
if __name__ == "__main__" :

    conf = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "consumer-group-1",
        "auto.offset.reset": "earliest", # Lire depuis le début du topic
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

        # Créer une table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS coordinates (
            Id SERIAL PRIMARY KEY,
            IP INET NOT NULL,     
            latitude FLOAT NOT NULL,  
            longitude FLOAT NOT NULL   
        );
        '''

        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'coordinates' créée avec succès")

        # Insérer des données dans la table
        insert_query = '''
        INSERT INTO coordinates (IP, latitude, longitude)
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
                if ( msg.partition() == 0 ) :
                    IP = '192.0.0.1'
                elif ( msg.partition() == 1 ) :
                    IP = '192.0.0.2'
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
        # Fermer la connexion et le curseur
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connexion PostgreSQL fermée")