-- ===============================================
-- 1) Table : crop_types (Types de cultures)
-- ===============================================
CREATE TABLE IF NOT EXISTS crop_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lifecycle_duration INT NOT NULL,
    unit VARCHAR(10) NOT NULL CHECK (unit IN ('days', 'months')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- 2) Table : users (Utilisateurs)
-- ===============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'farmer', 'other')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- 3) Table : pumps (Pompes d'irrigation)
-- ===============================================
CREATE TABLE IF NOT EXISTS pumps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    field_id INT NOT NULL, -- Pas de contrainte
    is_on BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    water_flow FLOAT DEFAULT 0.0,
    elapsed_time FLOAT DEFAULT 0.0,
    last_start_time TIMESTAMP NULL,
    last_activated TIMESTAMP NULL,
    total_usage_time FLOAT DEFAULT 0.0,
    power_consumption FLOAT DEFAULT 0.0,
    maintenance_status VARCHAR(50) NOT NULL DEFAULT 'ok',
    last_maintenance TIMESTAMP NULL
);

-- ===============================================
-- 4) Table : schedules (Plannings d'irrigation)
-- ===============================================
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    field_id INT NOT NULL, -- Pas de contrainte
    start_date DATE NOT NULL,
    start_time TIME WITHOUT TIME ZONE NOT NULL,
    duration INTERVAL NOT NULL,
    status VARCHAR(50) NOT NULL,
    flow_rate DOUBLE PRECISION NOT NULL,
    last_irrigation_time TIMESTAMP NULL
);

-- ===============================================
-- 5) Table : schedule_pumps (Relation planning-pompe)
-- ===============================================
CREATE TABLE IF NOT EXISTS schedule_pumps (
    pump_id INT NOT NULL, -- Pas de contrainte
    schedule_id INT NOT NULL, -- Pas de contrainte
    PRIMARY KEY (schedule_id, pump_id)
);

-- ===============================================
-- 6) Table : fields (Champs agricoles)
-- ===============================================
CREATE TABLE IF NOT EXISTS fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    size FLOAT NOT NULL,
    sensor_density FLOAT NOT NULL,
    crop_type_id INT NULL, -- Pas de contrainte
    planting_date DATE NULL
);

-- ===============================================
-- 7) Table : sensors (Capteurs)
-- ===============================================
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    installation_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('active', 'inactive', 'maintenance')),
    field_id INT NULL -- Pas de contrainte
);

-- ===============================================
-- 8) Table : sensorreadings (Données des capteurs)
-- ===============================================
CREATE TABLE IF NOT EXISTS sensorreadings (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL, -- Pas de contrainte
    field_id INTEGER NOT NULL, -- Pas de contrainte
    raw_data JSONB -- Stocke les données brutes du capteur
);

-- ===============================================
-- 9) Table : settings (Paramètres généraux)
-- ===============================================
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- 10) Table : dashboardsettings (Configuration du dashboard)
-- ===============================================
CREATE TABLE IF NOT EXISTS dashboardsettings (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    widgetsposition JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================
-- 11) Table : notifications (Notifications système)
-- ===============================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN NOT NULL DEFAULT FALSE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);



-- =====================================================
--  Mise à jour du trigger manage_pumps_on_schedule_status
--  pour utiliser 'notification_type' à la place de 'type'
-- =====================================================

-- Assurez-vous que la table notifications comporte :
-- notification_type VARCHAR(50) NOT NULL
-- read BOOLEAN NOT NULL DEFAULT FALSE
-- active BOOLEAN NOT NULL DEFAULT TRUE

-- ============================
-- 1) Supprimer l'ancien trigger
-- ============================
DROP TRIGGER IF EXISTS trigger_manage_pumps ON schedules;

-- ============================
-- 2) Nouvelle fonction gérant les pompes
-- ============================
CREATE OR REPLACE FUNCTION manage_pumps_on_schedule_status()
RETURNS TRIGGER AS $$
DECLARE
    pump_record RECORD;
BEGIN
    -- 🚀 1) Si la planification passe à "in_progress"
    IF NEW.status = 'in_progress' THEN

        -- Récupérer toutes les pompes liées à la NOUVELLE planification
        FOR pump_record IN
            SELECT p.id
              FROM pumps p
              JOIN schedule_pumps sp ON p.id = sp.pump_id
             WHERE sp.schedule_id = NEW.id
        LOOP
            -- A) Trouver si la pompe est déjà 'running' pour un autre planning en "in_progress"
            --    et, le cas échéant, arrêter cette ancienne planification en la passant à 'completed'.
            UPDATE schedules s
               SET status = 'completed'  -- Au lieu de 'cancelled'
              FROM schedule_pumps sp2
             WHERE s.id = sp2.schedule_id
               AND sp2.pump_id = pump_record.id
               AND s.id <> NEW.id               -- Exclure la planification actuelle
               AND s.status = 'in_progress';    -- L'autre planning en cours

            -- B) Arrêter physiquement la pompe si elle tourne déjà
            UPDATE pumps
               SET is_on            = FALSE,
                   status           = 'idle',
                   total_usage_time = total_usage_time
                                      + EXTRACT(EPOCH FROM (NOW() - last_start_time)) / 3600,
                   last_start_time  = NULL
             WHERE id = pump_record.id
               AND status = 'running';

            --   (On peut éventuellement insérer une notification pour l'arrêt forcé)
            INSERT INTO notifications (message, notification_type)
            VALUES (
                '🛑 Pompe ID ' || pump_record.id || ' arrêtée pour faire place à la nouvelle planification ' || NEW.id,
                'warning'
            );

            -- C) Démarrer la pompe pour la NOUVELLE planification
            UPDATE pumps
               SET is_on           = TRUE,
                   status          = 'running',
                   last_start_time = NOW(),
                   last_activated  = NOW()
             WHERE id = pump_record.id;

            INSERT INTO notifications (message, notification_type)
            VALUES (
                '🚰 Pompe ID ' || pump_record.id || ' démarrée pour le champ ' || NEW.field_id || ' (planning ' || NEW.id || ')',
                'info'
            );
        END LOOP;
    END IF;

    -- 🛑 2) Si la planification passe à "completed" ou "cancelled"
    IF NEW.status IN ('completed', 'cancelled') THEN
        FOR pump_record IN
            SELECT p.id
              FROM pumps p
              JOIN schedule_pumps sp ON p.id = sp.pump_id
             WHERE sp.schedule_id = NEW.id
               AND p.status = 'running'
        LOOP
            UPDATE pumps
               SET is_on            = FALSE,
                   status           = 'idle',
                   total_usage_time = total_usage_time
                                      + EXTRACT(EPOCH FROM (NOW() - last_start_time)) / 3600,
                   last_start_time  = NULL
             WHERE id = pump_record.id;

            INSERT INTO notifications (message, notification_type)
            VALUES (
                '🛑 Pompe ID ' || pump_record.id || ' arrêtée pour le champ ' || NEW.field_id || ' (planning ' || NEW.id || ')',
                'warning'
            );
        END LOOP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================
-- 3) (Re)Créer le trigger
-- ============================
CREATE TRIGGER trigger_manage_pumps
AFTER UPDATE ON schedules
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION manage_pumps_on_schedule_status();
