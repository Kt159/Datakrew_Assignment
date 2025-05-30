# Enum created based on excel sheet in data provided
create_enum_soc_band = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'soc_band_enum') THEN
        CREATE TYPE soc_band_enum AS ENUM ('0-20', '20-40', '40-60', '60-80', '80-100');
    END IF;
END
$$;
"""

create_enum_severity = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severity_enum') THEN
        CREATE TYPE severity_enum AS ENUM ('High', 'Medium', 'Low');
    END IF;
END
$$;
"""


# Create tables following Database Scheme 9
create_fleets = """
CREATE TABLE IF NOT EXISTS fleets (
    fleet_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    time_zone TEXT NOT NULL
);
"""
create_vehicles = """
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vin TEXT UNIQUE NOT NULL,
    fleet_id INTEGER REFERENCES fleets(fleet_id),
    model TEXT NOT NULL,
    make TEXT NOT NULL,
    variant TEXT NOT NULL,
    registration_no TEXT NOT NULL,
    purchase_date DATE NOT NULL
);
"""

create_raw_telemetry = """
CREATE TABLE IF NOT EXISTS raw_telemetry (
    ts TIMESTAMP NOT NULL,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    soc_pct DECIMAL NOT NULL,
    pack_voltage_v DECIMAL NOT NULL,
    pack_current_a DECIMAL NOT NULL,
    batt_temp_c DECIMAL NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed_kph DECIMAL NOT NULL,
    odo_km DECIMAL NOT NULL,
    PRIMARY KEY (ts, vehicle_id)
);
"""


create_processed_metrics = """
CREATE TABLE IF NOT EXISTS processed_metrics (
    ts TIMESTAMP NOT NULL,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    avg_speed_kph_15m DOUBLE PRECISION NOT NULL,
    distance_km_15m DECIMAL NOT NULL,
    energy_kwh_15m DECIMAL NOT NULL,
    battery_health_pct DECIMAL NOT NULL,
    soc_band soc_band_enum NOT NULL,
    PRIMARY KEY (ts, vehicle_id)
);
"""

create_charging_sessions = """
CREATE TABLE IF NOT EXISTS charging_sessions (
    session_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP NOT NULL,
    start_soc DECIMAL NOT NULL,
    end_soc DECIMAL NOT NULL,
    energy_kwh DECIMAL NOT NULL,
    location TEXT NOT NULL
);
"""

create_trips = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP NOT NULL,
    distance_km DECIMAL NOT NULL,
    energy_kwh DECIMAL NOT NULL,
    idle_minutes DECIMAL NOT NULL,
    avg_temp_c DECIMAL NOT NULL
);
"""

create_alerts = """
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    alert_type TEXT NOT NULL,
    severity severity_enum NOT NULL,
    alert_ts TIMESTAMP NOT NULL,
    value DECIMAL NOT NULL,
    threshold DECIMAL NOT NULL,
    resolved_bool BOOLEAN NOT NULL,
    resolved_ts TIMESTAMP
);
"""
create_battery_cycles = """
CREATE TABLE IF NOT EXISTS battery_cycles (
    cycle_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    ts TIMESTAMP NOT NULL,
    dod_pct DECIMAL NOT NULL,
    soh_pct DECIMAL NOT NULL
);
"""
create_maintenance_logs = """
CREATE TABLE IF NOT EXISTS maintenance_logs (
    maint_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    maint_type TEXT NOT NULL,
    start_ts TIMESTAMP NOT NULL,
    end_ts TIMESTAMP NOT NULL,
    cost_sgd DECIMAL NOT NULL,
    notes TEXT
);
"""
create_drivers = """
CREATE TABLE IF NOT EXISTS drivers (
    driver_id SERIAL PRIMARY KEY,
    fleet_id INTEGER NOT NULL REFERENCES fleets(fleet_id),
    name TEXT NOT NULL,
    license_no TEXT NOT NULL,
    hire_date DATE NOT NULL
);
"""
create_driver_trip_map = """
CREATE TABLE IF NOT EXISTS driver_trip_map (
    trip_id INTEGER NOT NULL REFERENCES trips(trip_id),
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id),
    primary_bool BOOLEAN NOT NULL DEFAULT TRUE
);
"""
create_geofence_events = """
CREATE TABLE IF NOT EXISTS geofence_events (
    event_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(vehicle_id),
    geofence_name TEXT NOT NULL,
    enter_ts TIMESTAMP NOT NULL,
    exit_ts TIMESTAMP NOT NULL
);
"""
create_fleet_daily_summary = """
CREATE TABLE IF NOT EXISTS fleet_daily_summary (
    fleet_id INTEGER NOT NULL REFERENCES fleets(fleet_id),
    date DATE NOT NULL,
    total_distance_km DECIMAL NOT NULL,
    total_energy_kwh DECIMAL NOT NULL,
    active_vehicles INTEGER NOT NULL,
    avg_soc_pct DECIMAL NOT NULL
);
"""

all_create_statements = [
    create_enum_soc_band,
    create_enum_severity,
    create_fleets,
    create_vehicles,
    create_raw_telemetry,
    create_processed_metrics,
    create_charging_sessions,
    create_trips,
    create_alerts,
    create_battery_cycles,
    create_maintenance_logs,
    create_drivers,
    create_driver_trip_map,
    create_geofence_events,
    create_fleet_daily_summary
]