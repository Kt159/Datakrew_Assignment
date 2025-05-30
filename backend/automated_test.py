#Unit Testing for generating and executing SQL queries
import pytest
from decimal import Decimal
from langchain_pipeline import AgentExecutor

agent = AgentExecutor()
agent.connect_to_db()
fleet_id = 1  # Mock fleet ID for testing
agent.set_active_fleet_id(fleet_id)

@pytest.mark.parametrize("question, expected_result", [
    ("What is the SOC of vehicle GBM6296G right now?", [(Decimal('57'),)]), 
    ("How many SRM T3 EVs are in my fleet?", [(2,)]),
    ("Did any SRM T3 exceed 33 °C battery temperature in the last 24 h?", [(False,)]),
    ("What is the fleet‑wide average SOC comfort zone?", [(Decimal('55'),), (Decimal('60'),)]), # there are 2 avg_soc_pct values for fleet_id = 1
    ("Which vehicles spent > 20 % time in the 90‑100 % SOC band this week?", 'No results found.'), # 90-100 band does not exist in database
    ("How many vehicles are currently driving with SOC < 30 %?", [(0,)]), # No vehicles with SOC < 30% in the mock data for fleet_id = 1
    ("What is the total km and driving hours by my fleet over the past 7 days, and which are the most-used & least-used vehicles?", [(None, None, None, None)]) # No data for the past 7 days in the mock data for fleet_id = 1
])

def test_sql_query_generation_and_execution(question, expected_result):
    sql = agent.generate_sql_query(question)
    actual_result = agent.run_sql_query(sql, question)

    assert actual_result == expected_result, f"\nQ: {question}\nExpected: {expected_result}, but got: {actual_result}"
