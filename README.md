# Datakrew_Assignment
```markdown
Datakrew_Assignment/
├── backend/
│   ├── agent_logs.log (A log file to track AI agent's operations)
│   ├── **automated_test.py** (Automated test using pytest --> Tested using 'fleet_id = 1' from mock data)
│   ├── Dockerfile (Build docker image for FastAPI service) 
│   ├── langchain_pipeline.py (Core logic for AI-driven query pipeline, built using Langchain tool-calling) 
│   ├── main.py (Main entry for FastAPI service)
│   ├── prompt_templates.py (Predefined prompt templates to guide LLM)
│   ├── requirements.txt
│   └── **semantic_mappings.yaml** (Contain mappings between Natural Language and DB Schema elements)
│   
├── database/
│   ├── clear_database.py (Cleaning script --> Clears current DB data)
│   ├── **import_data.py** (Import script --> Create schema + load csv from data folder)
│   ├── row_level_security.py (Set up RLS policies --> Fleet_id row filtering)
│   ├── schema.py (Defines database schema)
│   └── data/ (Mock csv data provided)
│       ├── alerts.csv
│       ├── battery_cycles.csv
│       ├── charging_sessions.csv
│       ├── drivers.csv
│       ├── driver_trip_map.csv
│       ├── fleets.csv
│       ├── fleet_daily_summary.csv
│       ├── geofence_events.csv
│       ├── maintenance_logs.csv
│       ├── processed_metrics.csv
│       ├── raw_telemetry.csv
│       ├── trips.csv
│       └── vehicles.csv
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile (Build docker image for React frontend)
│   ├── .gitignore
│   └── src/
│       ├── App.css
│       ├── App.js (Main component of React application)
│       ├── ChatWindow.js (Renders chat interface)
│       ├── index.css 
│       ├── index.js
│       ├── Message.js (Renders chat messages)
│       ├── MessageInput.js (Renders chat input field)
│       ├── reportWebVitals.js
│       └── setupTests.js
│   
│
├── .env (Environment variables listed here)
├── .gitignore 
├── docker-compose.yml (Build multi-container docker application)
└── README.md
```

