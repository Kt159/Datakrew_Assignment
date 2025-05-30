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
## Tech Stack Used
![Diagram](./images/datakrew_techstack.png)

## Login Page Logic/Routing
![Diagram](./images/datakrew_login.png)
1. User Input: The user types their **fleetname** into the login page on the frontend.
2. API Call: The frontend sends this fleetname to your FastAPI backend's `/get-token` API endpoint.
3. Fleet Validation: FastAPI then queries the PostgreSQL database to validate if the fleetname exists.
4. JWT Production: If the fleetname is valid, FastAPI creates a JSON Web Token (JWT). This token contains the unique `fleet_id` associated with that user's fleet.
5. Session & RLS Enforcement: The frontend uses this JWT for all subsequent requests. FastAPI validates the token to maintain the user's session and, critically, uses the `fleet_id` within the token to enforce Row-Level Security (RLS), ensuring the user can only access data belonging to their specific fleet.

## Core LangChain AI-driven query logic
![Diagram](./images/datakrew.drawio.png)
1. **User Query**: The process begins with a user submitting a natural language query.
2. **Agent** (Langchain): The user's query is received by the Agent (Langchain). The agent acts as the orchestrator, deciding the best course of action based on the query.
3. **SQL Pipeline Tool** (Decision Point): The Langchain Agent, if it determines the query requires database interaction, invokes the SQL Pipeline Tool.
4. **Extract Semantic Information**: As part of the SQL Pipeline Tool's preparation, relevant semantic information is extracted from `semantic_mapping.yaml`. This helps the LLM in understanding database schema terms.
5. **Generate SQL Query** (MistralAI): Based on the user's query and potentially the semantic mappings, an LLM (specifically MistralAI) is used to Generate a SQL Query.
6. **Run SQL Query** (PostgreSQL): The generated SQL query is then executed against the PostgreSQL database to Run the SQL Query and retrieve data.
7. **LLM Response** (MistralAI): Finally, the results from the SQL query are fed back to an LLM (MistralAI), which then formulates a natural language LLM Response to the user.
