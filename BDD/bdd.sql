-- Vérifiez si la base de données existe déjà, et ne la recréez que si elle n'existe pas
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'gps_tracking_db') THEN
        CREATE DATABASE gps_tracking_db;
    END IF;
END $$;

-- Utiliser la base de données gps_tracking_db
\c gps_tracking_db;

-- Créez vos tables et insérez des données ici
CREATE TABLE IF NOT EXISTS coordonnees (
    id SERIAL PRIMARY KEY,
    IP CHAR(50) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajoutez d'autres requêtes d'insertion ici si nécessaire

