-- CityAir database schema
-- City → Monitoring Location → Sensor → Reading

PRAGMA foreign_keys = ON;


-- ============================================================
-- Cities
-- ============================================================

CREATE TABLE IF NOT EXISTS cities (
    city_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name     TEXT NOT NULL,
    state         TEXT,
    country       TEXT NOT NULL DEFAULT 'India',
    latitude      REAL NOT NULL,
    longitude     REAL NOT NULL,

    -- Coordinates returned by the geocoder.
    geocoder      TEXT DEFAULT 'nominatim',

    created_at    TEXT DEFAULT (datetime('now')),

    UNIQUE(city_name, state)
);


-- ============================================================
-- OpenAQ monitoring locations
-- ============================================================

CREATE TABLE IF NOT EXISTS locations (
    location_id          INTEGER PRIMARY KEY AUTOINCREMENT,

    city_id              INTEGER NOT NULL,

    -- Original OpenAQ location ID
    openaq_location_id   INTEGER NOT NULL UNIQUE,

    location_name        TEXT,

    latitude             REAL,
    longitude            REAL,

    is_mobile            INTEGER DEFAULT 0,
    is_monitor           INTEGER DEFAULT 0,

    owner_name           TEXT,
    provider_name        TEXT,

    first_measurement    TEXT,
    last_measurement     TEXT,

    FOREIGN KEY (city_id)
        REFERENCES cities(city_id)
        ON DELETE CASCADE
);


-- ============================================================
-- Sensors
-- ============================================================

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id             INTEGER PRIMARY KEY AUTOINCREMENT,

    location_id           INTEGER NOT NULL,

    -- Original OpenAQ sensor ID
    openaq_sensor_id      INTEGER NOT NULL UNIQUE,

    sensor_name           TEXT,

    parameter             TEXT NOT NULL,

    unit                   TEXT,

    first_measurement      TEXT,
    last_measurement       TEXT,

    coverage_percent       REAL,

    FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
        ON DELETE CASCADE
);


-- ============================================================
-- Hourly readings
-- ============================================================

CREATE TABLE IF NOT EXISTS readings (
    reading_id       INTEGER PRIMARY KEY AUTOINCREMENT,

    sensor_id        INTEGER NOT NULL,

    city_id          INTEGER NOT NULL,

    parameter        TEXT NOT NULL,

    value            REAL NOT NULL,

    unit              TEXT,

    measured_at       TEXT NOT NULL,

    source            TEXT DEFAULT 'openaq',

    ingested_at      TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (sensor_id)
        REFERENCES sensors(sensor_id)
        ON DELETE CASCADE,

    FOREIGN KEY (city_id)
        REFERENCES cities(city_id)
        ON DELETE CASCADE,

    UNIQUE(sensor_id, measured_at)
);


-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_locations_city
    ON locations(city_id);


CREATE INDEX IF NOT EXISTS idx_sensors_location
    ON sensors(location_id);


CREATE INDEX IF NOT EXISTS idx_sensors_parameter
    ON sensors(parameter);


CREATE INDEX IF NOT EXISTS idx_readings_city_time
    ON readings(city_id, measured_at);


CREATE INDEX IF NOT EXISTS idx_readings_parameter
    ON readings(parameter);


CREATE INDEX IF NOT EXISTS idx_readings_sensor_time
    ON readings(sensor_id, measured_at);