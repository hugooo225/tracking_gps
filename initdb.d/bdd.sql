-- the database is created if it doesn't already exist
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'gps_tracking_db') THEN
        CREATE DATABASE gps_tracking_db;
    END IF;
END $$;

-- use the gps_tracking_db database
\c gps_tracking_db;

-- creation of the tables
CREATE TABLE IF NOT EXISTS coordonnees (
    id SERIAL PRIMARY KEY,
    IP CHAR(50) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
