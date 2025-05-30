import re
import yaml
import os
import logging
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import init_chat_model
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from prompt_templates import fallback_schema, SQL_generation_prompt_template, SQL_error_prompt_template, LLM_answer_prompt_template
from sqlalchemy import text
from typing import List
load_dotenv()


if not os.path.exists('agent_logs.log'):
    with open('agent_logs.log', 'w') as f:
        pass  

logging.basicConfig(
    filename='agent_logs.log',   
    filemode='a',                  
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class LoggingCallbackHandler(BaseCallbackHandler):
    def on_agent_action(self, action, **kwargs):
        logging.info(f"[Agent Action] Tool: {action.tool} | Input: {action.tool_input}")

    def on_tool_end(self, output, **kwargs):
        logging.info(f"[Tool Output] {output}")

    def on_agent_finish(self, finish, **kwargs):
        logging.info(f"[Agent Finish] {finish.log}")

    def on_text(self, text, **kwargs):
        logging.info(f"[LLM Output] {text.strip()}")


class QueryAssistant:
    def __init__(self, model="mistral-large-latest", provider="mistralai", env_api_key ='MISTRAL_API_KEY', temperature=0.0, semantic_mapping_path="./semantic_mappings.yaml"):
        self.llm = init_chat_model(
            model=model,
            model_provider=provider,
            api_key=os.getenv(env_api_key),
            temperature=temperature,
        )
        self.semantic_mapping_path = semantic_mapping_path
        self.active_fleet_id = None
        self.db = self.connect_to_db()

    def connect_to_db(self):
        dbname = os.getenv("DB_NAME")
        user = os.getenv("APP_ROLE_NAME")
        password = os.getenv("APP_ROLE_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")

        if not all([dbname, user, password, host, port]):
            raise ValueError("Database credentials missing.")

        return SQLDatabase.from_uri(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

    def extract_semantic_info(self, question: str) -> str:
        with open(self.semantic_mapping_path, "r") as f:
            raw_terms = yaml.safe_load(f)['terms']
        hints = []
        for entry in raw_terms:
            pattern = re.compile(entry["pattern"])
            match = pattern.search(question)
            if match:
                hints.append(f'"{match.group(0)}" in the question relate to {entry["column"]} column in {entry["table"]} table.')
        extracted_info = "\n".join(hints)
        logging.info(f"Extracted semantic information: {extracted_info}")
        return extracted_info if hints else "No semantic information extracted."

    def inject_sql_query_limit(self, sql: str) -> str:
        if not re.search(r"\blimit\b", sql, re.IGNORECASE):
            sql += " LIMIT 5000"
        return sql

    def generate_sql_query(self, question: str, prompt_template: str = SQL_generation_prompt_template) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        sql = chain.invoke({
            "hints": self.extract_semantic_info(question),
            "fallback_schema": fallback_schema,
            "question": question
        })
        cleaned_sql = re.sub(r"^```sql|```$", "", sql.strip(), flags=re.IGNORECASE).strip()
        if cleaned_sql.endswith(';'):
            cleaned_sql = cleaned_sql[:-1].strip()
        
        limited_sql = self.inject_sql_query_limit(cleaned_sql)
        if not limited_sql.endswith(';'):
            limited_sql += ';'
        logging.info(f"Generated SQL query: {limited_sql}")
        return limited_sql

    def run_sql_query(self, sql: str, question: str) -> str:
        fleet_id = self.active_fleet_id 
        if fleet_id is None:
            raise ValueError("fleet_id not set for the current request. RLS cannot be applied.")
        try:
            with self.db._engine.connect() as connection:
                connection.execute(text(f"SET app.current_fleet_id = {int(fleet_id)};"))
                connection.commit()
                result_proxy = connection.execute(text(sql))
                result = result_proxy.fetchall()
                if not result:
                    result = "No results found."

            logging.info(f"SQL Result: {result}")
            return result
            
        except Exception as e:
            error_message = str(e)
            logging.error(f"SQL error: {e}\nQuery: {sql}")
            error_response = self.sql_error_response(question, sql, error_message)
            logging.info(f"SQL Error Response: {error_response}")
            return error_response
    
    def sql_error_response(self, question: str, sql: str, error_message: str, prompt_template: str = SQL_error_prompt_template) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({
            "sql": sql,
            "error_message": error_message,
            "question": question
        })
        logging.info(f"SQL Error Response: {response}")
        return response
            
    def llm_response(self, question: str, sql: str, result: str, prompt_template: str = LLM_answer_prompt_template) -> str:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({
            "question": question,
            "query": sql,
            "result": result
        })
        logging.info(f"LLM Response: {response}")
        return response

class AgentExecutor(QueryAssistant):
    def __init__(self):
        super().__init__()
        self.agent = self.create_simple_agent()

    def run_pipeline(self, question: str) -> str:
        sql = self.generate_sql_query(question)
        result = self.run_sql_query(sql, question)
        return self.llm_response(question, sql, result)

    def log_tool_usage(self, func):
        def wrapper(*args, **kwargs):
            question = args[0] if args else kwargs.get('question', '')
            logging.info(f"[Tool] Called with input: {question}")
            result = func(*args, **kwargs)
            logging.info(f"[Tool] Output: {result}")
            return result
        return wrapper

    def create_simple_agent(self):
        tools = [
            Tool.from_function(
                name="sql_pipeline_tool",
                description=(
                    "Use this tool ONLY when the user's query explicitly requires fetching information "
                    "from the database, such as data about fleets, assets, trips, maintenance records, "
                    "or specific measurements. "
                    "Do NOT use this tool for greetings, general knowledge questions, "
                    "conversational chitchat, or any query that does not clearly relate to retrieving "
                    "structured data from the database. If the query is outside the scope of database "
                    "information, respond directly in natural language."),
                func=self.log_tool_usage(self.run_pipeline)
            )
        ]
        callback_manager = CallbackManager([LoggingCallbackHandler()])
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            callback_manager=callback_manager,
        )

    def run_query_with_agent(self, question: str, fleet_id: int) -> str:
        self.active_fleet_id = fleet_id
        try:
            print(f"Running query with agent for fleet_id {fleet_id}: {question}")
            response = self.agent.invoke(question)
            return response
        except Exception as e:
            logging.error(f"Agent execution error: {e}")
            return f"An error occurred while processing your request: {str(e)}"
        finally:
            self.active_fleet_id = None # Reset fleet_id after the query


### Example usage

# agent = AgentExecutor()
# response = agent.run_query_with_agent("What is the SOC of vehicle GBM6296G right now?", fleet_id=1)

