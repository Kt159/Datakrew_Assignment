import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

drop_statements = [
    "DROP TABLE IF EXISTS fleet_daily_summary CASCADE;",
    "DROP TABLE IF EXISTS geofence_events CASCADE;",
    "DROP TABLE IF EXISTS driver_trip_map CASCADE;",
    "DROP TABLE IF EXISTS drivers CASCADE;",
    "DROP TABLE IF EXISTS maintenance_logs CASCADE;",
    "DROP TABLE IF EXISTS battery_cycles CASCADE;",
    "DROP TABLE IF EXISTS alerts CASCADE;",
    "DROP TABLE IF EXISTS trips CASCADE;",
    "DROP TABLE IF EXISTS charging_sessions CASCADE;",
    "DROP TABLE IF EXISTS processed_metrics CASCADE;",
    "DROP TABLE IF EXISTS raw_telemetry CASCADE;",
    "DROP TABLE IF EXISTS vehicles CASCADE;",
    "DROP TABLE IF EXISTS fleets CASCADE;",
    "DROP TYPE IF EXISTS soc_band_enum CASCADE;",
    "DROP TYPE IF EXISTS severity_enum CASCADE;"
]

for stmt in drop_statements:
    try:
        cur.execute(stmt)
        conn.commit()
        print(f"Executed: {stmt}")
    except Exception as e:
        print(f"Failed to execute {stmt}: {e}")
        conn.rollback()

cur.close()
conn.close()
