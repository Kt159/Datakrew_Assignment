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
    You are an expert SQL generator. Given a natural language question, 
    output only the SQL query needed to answer it. 

    Use the following hints to guide your column/table selection:
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

SQL_error_prompt_template = """
    The following SQL query failed:
    {sql}

    Error message:
    {error_message}

    The user asked:
    {question}

    Inform the user clearly that their query requested data that does not exist.
    Suggest alternative queries or ask for clarification.
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
