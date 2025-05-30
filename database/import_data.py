import psycopg2
from dotenv import load_dotenv
import os
from schema import all_create_statements
from row_level_security import RLS_statements

load_dotenv()

script_directory = os.path.dirname(os.path.abspath(__file__))
data_folder_path = os.path.join(script_directory, 'data')
def get_csv_path(filename):
    return os.path.join(data_folder_path, filename)

# DB config from .env (Admin level access)
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

try:
    # Create schema if it doesn't exist
    for create_statement in all_create_statements:
        try:
            cur.execute(create_statement)
            conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")
            conn.rollback()
    print("Schema created successfully.")

    # Apply Row Level Security policies
    for rls_statement in RLS_statements:
        try:
            cur.execute(rls_statement)
            conn.commit()
        except Exception as e:
            print(f"Error applying RLS policy: {e}")
            conn.rollback()
    print("Row Level Security policies applied successfully.")
    
    # Bulk load function
    def load_csv(table_name, csv_path):
        try:
            with open(csv_path, 'r') as f:
                cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
            conn.commit()
            print(f"Loaded {csv_path} into {table_name}")
        except Exception as e:
            print(f"Failed to load {csv_path} into {table_name}: {e}")
            conn.rollback()

    table_names = [
        "fleets",
        "vehicles",
        "raw_telemetry",
        "processed_metrics",
        "charging_sessions",
        "trips",
        "alerts",
        "battery_cycles",
        "maintenance_logs",
        "drivers",
        "driver_trip_map",
        "geofence_events",
        "fleet_daily_summary"
    ]

    for table in table_names:
        csv_file = f"{table}.csv"
        csv_path = get_csv_path(csv_file)
        if os.path.exists(csv_path):
            try:
                load_csv(table, csv_path)
                print(f"Successfully loaded {csv_file} into {table}.")
            except Exception as e:
                print(f"Error loading {table}: {e}")
        else:
            print(f"CSV file for table '{table}' not found at path: {csv_path}")

except Exception as e:
    print(f"An unhandled error occurred during database setup: {e}")
    conn.rollback() # Ensure rollback for any unhandled errors

finally:
    cur.close()
    conn.close()
    print("Database setup script finished.")