fallback_schema = """
    Tables available:
    - fleets (fleet_id, name, country, time_zone)
    - vehicles (vehicle_id, vin, fleet_id, model, make, registration_no)
    - raw_telemetry (ts, vehicle_id, soc_pct, batt_temp_c, speed_kph, odo_km)
    - processed_metrics (ts, vehicle_id, avg_speed_kph_15m, distance_km_15m, soc_band)
    - charging_sessions (session_id, vehicle_id, start_ts, end_ts, energy_kwh)
    - trips (trip_id, vehicle_id, start_ts, end_ts, distance_km, avg_temp_c)
    - alerts (alert_id, vehicle_id, alert_type, severity, alert_ts)
    - battery_cycles (cycle_id, vehicle_id, ts, dod_pct, soh_pct)
    - maintenance_logs (maint_id, vehicle_id, maint_type, start_ts, cost_sgd)
    - drivers (driver_id, fleet_id, name, license_no)
    - driver_trip_map (trip_id, driver_id, primary_bool)
    - geofence_events (event_id, vehicle_id, geofence_name, enter_ts, exit_ts)
    - fleet_daily_summary (fleet_id, date, total_distance_km, avg_soc_pct)
    """


SQL_generation_prompt_template = """
    You are an expert SQL generator. Given a natural language question, output only the SQL query needed to answer it. 

    When querying data, always use the following table/view names for row-level security:

    Directly accessible tables (use original names):
    - 'fleets' (contains fleet_id directly)
    - 'vehicles' (contains fleet_id directly)
    - 'drivers' (contains fleet_id directly)
    - 'fleet_daily_summary' (contains fleet_id directly)

    Helper Views (use '_v' suffix for these, as they join to expose fleet_id):
    - 'raw_telemetry_v' (instead of 'raw_telemetry')
    - 'processed_metrics_v' (instead of 'processed_metrics')
    - 'charging_sessions_v' (instead of 'charging_sessions')
    - 'trips_v' (instead of 'trips')
    - 'alerts_v' (instead of 'alerts')
    - 'battery_cycles_v' (instead of 'battery_cycles')
    - 'maintenance_logs_v' (instead of 'maintenance_logs')
    - 'driver_trip_map_v' (instead of 'driver_trip_map')
    - 'geofence_events_v' (instead of 'geofence_events')

    **IMPORTANT RLS RULE:** 
    All queries must adhere to Row-Level Security. 
    The term 'fleet-wide' in a question ALWAYS refers to the data pertinent to the `current_setting('app.current_fleet_id')::integer` which is set for the user's active fleet. 
    You MUST ensure that any aggregate or summary query, especially those over tables containing multi-fleet data like 'fleet_daily_summary', implicitly or explicitly respects this filtering. 
    Do NOT generate queries that could expose data outside the current user's fleet.

    Use the following hints to guide your column/table selection:
    **Crucially, if a hint specifies a name for a value (like 'SRM T3' for the 'model' column), use that exact value in your WHERE clause.**
    {hints}

    If the hints are insufficient, refer to the full database schema:
    {fallback_schema}

    Generate a SQL query to answer:
    {question}

    Important:
    - Do not include any units like "%", "km", or "kWh" in string values or comparisons.
    - soc_band values (enum): '0-20', '20-40', '40-60', '60-80', '80-100'
    - severity (enum): 'Low', 'Medium', 'High'
    - Only use column values as they appear in the database.
    - Only output SQL — no explanations, markdown, or commentary.
    """


LLM_answer_prompt_template = """
    You are a data assistant. Use the following SQL query and its result 
    to answer the user's question accurately and concisely.

    If the SQL result does not contain enough information to answer the question, 
    clearly state that and suggest what additional data might be needed.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: 
    """
