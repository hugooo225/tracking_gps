import psycopg2
from psycopg2 import sql

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

try:
    # Connexion à la base de données PostgreSQL
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    print("Connexion réussie à PostgreSQL")

    # Créer une table
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS coordinates (
        IP INET PRIMARY KEY,     
        latitude FLOAT NOT NULL,  
        longitude FLOAT NOT NULL   
    );
    '''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table 'personnes' créée avec succès")

    # Insérer des données dans la table
    insert_query = '''
    INSERT INTO coordinates (nom, age)
    VALUES (%s, %s);
    '''
    records = [
        ('Alice', 30),
        ('Bob', 25),
        ('Charlie', 35)
    ]
    cursor.executemany(insert_query, records)
    connection.commit()
    print("Données insérées avec succès dans la table 'personnes'")

    # Lire les données de la table
    cursor.execute("SELECT * FROM personnes;")
    rows = cursor.fetchall()
    print("Données récupérées :")
    for row in rows:
        print(f"ID: {row[0]}, Nom: {row[1]}, Age: {row[2]}")

except (Exception, psycopg2.Error) as error:
    print("Erreur lors de l'opération PostgreSQL :", error)

finally:
    # Fermer la connexion et le curseur
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Connexion PostgreSQL fermée")
