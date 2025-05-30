import os
from dotenv import load_dotenv

load_dotenv()

APP_ROLE_NAME = os.getenv("APP_ROLE_NAME", "fleet_users_default")
APP_ROLE_PASSWORD = os.getenv("APP_ROLE_PASSWORD")

create_app_role = f"""
DO $$
BEGIN
    -- Check if the role exists
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE_NAME}') THEN
        CREATE ROLE {APP_ROLE_NAME} WITH LOGIN PASSWORD '{APP_ROLE_PASSWORD}';
    ELSE
        -- If it exists, update its password
        ALTER ROLE {APP_ROLE_NAME} WITH PASSWORD '{APP_ROLE_PASSWORD}';
    END IF;
END
$$;

-- Grant basic connection and schema usage
GRANT CONNECT ON DATABASE "{os.getenv("DB_NAME")}" TO {APP_ROLE_NAME};
GRANT USAGE ON SCHEMA public TO {APP_ROLE_NAME};

-- Set default privileges for *future* tables created in the public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO {APP_ROLE_NAME};
"""

remove_old_RLS_policies = [
    "ALTER TABLE fleets DISABLE ROW LEVEL SECURITY;", 
    "ALTER TABLE vehicles DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE drivers DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE fleet_daily_summary DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE raw_telemetry DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE processed_metrics DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE charging_sessions DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE trips DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE alerts DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE battery_cycles DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE maintenance_logs DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE geofence_events DISABLE ROW LEVEL SECURITY;",
    "ALTER TABLE driver_trip_map DISABLE ROW LEVEL SECURITY;",
]

create_new_RLS_policies = [
    "ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE fleet_daily_summary ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE raw_telemetry ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE processed_metrics ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE charging_sessions ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE trips ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE battery_cycles ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE maintenance_logs ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE geofence_events ENABLE ROW LEVEL SECURITY;",
    "ALTER TABLE driver_trip_map ENABLE ROW LEVEL SECURITY;",
]


direct_fleet_id_RLS_policies = f"""
-- Table: vehicles
CREATE POLICY vehicles_rls_policy ON vehicles
FOR ALL
TO {APP_ROLE_NAME}
USING (fleet_id = current_setting('app.current_fleet_id', true)::INTEGER); 

-- Table: drivers
CREATE POLICY drivers_rls_policy ON drivers
FOR ALL
TO {APP_ROLE_NAME}
USING (fleet_id = current_setting('app.current_fleet_id', true)::INTEGER);

-- Table: fleet_daily_summary
CREATE POLICY fleet_daily_summary_rls_policy ON fleet_daily_summary
FOR ALL
TO {APP_ROLE_NAME}
USING (fleet_id = current_setting('app.current_fleet_id', true)::INTEGER);
"""

indirect_fleet_id_RLS_views = f"""
-- Table: raw_telemetry
CREATE OR REPLACE VIEW raw_telemetry_v AS
SELECT
    rt.*,
    v.fleet_id
FROM
    raw_telemetry rt
JOIN
    vehicles v ON rt.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON raw_telemetry_v TO {APP_ROLE_NAME};

-- Table: processed_metrics
CREATE OR REPLACE VIEW processed_metrics_v AS
SELECT
    pm.*,
    v.fleet_id
FROM
    processed_metrics pm
JOIN
    vehicles v ON pm.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON processed_metrics_v TO {APP_ROLE_NAME};

-- Table: charging_sessions
CREATE OR REPLACE VIEW charging_sessions_v AS
SELECT
    cs.*,
    v.fleet_id
FROM
    charging_sessions cs
JOIN
    vehicles v ON cs.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON charging_sessions_v TO {APP_ROLE_NAME};

-- Table: trips
CREATE OR REPLACE VIEW trips_v AS
SELECT
    t.*,
    v.fleet_id
FROM
    trips t
JOIN
    vehicles v ON t.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON trips_v TO {APP_ROLE_NAME};


-- Table: alerts
CREATE OR REPLACE VIEW alerts_v AS
SELECT
    a.*,
    v.fleet_id
FROM
    alerts a
JOIN
    vehicles v ON a.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON alerts_v TO {APP_ROLE_NAME};

-- Table: battery_cycles
CREATE OR REPLACE VIEW battery_cycles_v AS
SELECT
    bc.*,
    v.fleet_id
FROM
    battery_cycles bc
JOIN
    vehicles v ON bc.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON battery_cycles_v TO {APP_ROLE_NAME};

-- Table: maintenance_logs
CREATE OR REPLACE VIEW maintenance_logs_v AS
SELECT
    ml.*,
    v.fleet_id
FROM
    maintenance_logs ml
JOIN
    vehicles v ON ml.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON maintenance_logs_v TO {APP_ROLE_NAME};

-- Table: geofence_events
CREATE OR REPLACE VIEW geofence_events_v AS
SELECT
    ge.*,
    v.fleet_id
FROM
    geofence_events ge
JOIN
    vehicles v ON ge.vehicle_id = v.vehicle_id;
-- RLS is handled by the underlying 'vehicles' table.
GRANT SELECT ON geofence_events_v TO {APP_ROLE_NAME};

-- Table: driver_trip_map
CREATE OR REPLACE VIEW driver_trip_map_v AS
SELECT
    dtm.*,
    d.fleet_id
FROM
    driver_trip_map dtm
JOIN
    drivers d ON dtm.driver_id = d.driver_id;
-- RLS is handled by the underlying 'drivers' table.
GRANT SELECT ON driver_trip_map_v TO {APP_ROLE_NAME};
"""

set_privileges = f"""
-- For base tables:
GRANT SELECT ON fleets TO {APP_ROLE_NAME};
GRANT SELECT ON vehicles TO {APP_ROLE_NAME};
GRANT SELECT ON raw_telemetry TO {APP_ROLE_NAME};
GRANT SELECT ON processed_metrics TO {APP_ROLE_NAME};
GRANT SELECT ON charging_sessions TO {APP_ROLE_NAME};
GRANT SELECT ON trips TO {APP_ROLE_NAME};
GRANT SELECT ON alerts TO {APP_ROLE_NAME};
GRANT SELECT ON battery_cycles TO {APP_ROLE_NAME};
GRANT SELECT ON maintenance_logs TO {APP_ROLE_NAME};
GRANT SELECT ON drivers TO {APP_ROLE_NAME};
GRANT SELECT ON driver_trip_map TO {APP_ROLE_NAME};
GRANT SELECT ON geofence_events TO {APP_ROLE_NAME};
GRANT SELECT ON fleet_daily_summary TO {APP_ROLE_NAME};

-- For helper views with RLS:
GRANT SELECT ON raw_telemetry_v TO {APP_ROLE_NAME};
GRANT SELECT ON processed_metrics_v TO {APP_ROLE_NAME};
GRANT SELECT ON charging_sessions_v TO {APP_ROLE_NAME};
GRANT SELECT ON trips_v TO {APP_ROLE_NAME};
GRANT SELECT ON alerts_v TO {APP_ROLE_NAME};
GRANT SELECT ON battery_cycles_v TO {APP_ROLE_NAME};
GRANT SELECT ON maintenance_logs_v TO {APP_ROLE_NAME};
GRANT SELECT ON driver_trip_map_v TO {APP_ROLE_NAME};
GRANT SELECT ON geofence_events_v TO {APP_ROLE_NAME};
"""

RLS_statements = [
    create_app_role,
    *remove_old_RLS_policies,
    *create_new_RLS_policies,
    direct_fleet_id_RLS_policies, 
    indirect_fleet_id_RLS_views, 
    set_privileges
]