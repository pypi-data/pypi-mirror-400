import operator
import yaml
import logging
import threading
import time
import configparser
import os
from typing import Any, Dict, List, Optional, TypedDict
from typing_extensions import Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Command

# Internal utility imports from your original project
from structured_agent.utils.services import *
from structured_agent.utils.constants_common import *

import snowflake.connector
import oracledb

from structured_agent.utils.services import load_constants
from structured_agent.utils.state import AgentState, InputSchema, ResponseSchema
from langgraph.types import RunnableConfig

from dotenv import load_dotenv


load_dotenv()
env = os.environ.get("ENVIRONMENT", "dev")

# Load config.ini
config = configparser.ConfigParser()
# Check for config.ini in current working directory first
cwd_config_path = os.path.join(os.getcwd(), "config.ini")
bundled_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
if os.path.exists(cwd_config_path):
    config_path = cwd_config_path
else:
    config_path = bundled_config_path
config.read(config_path)

from structured_agent.utils.tools import (
    _get_db_desc_str_new,
    parse_sql_from_string,
    parse_json,
    get_data_from_yaml_file,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
model = None


def refresh_llm_instance():
    """Refresh the LLM instance every 55 minutes."""
    global model
    while True:
        # Wait for 55 minutes (3300 seconds) before refreshing
        time.sleep(3300)
        logging.info("Refreshing LLM instance...")
        try:
            model = get_model()
            logging.info("LLM instance refreshed successfully")
        except Exception as e:
            logging.error(f"Error refreshing LLM instance: {e}")

def handle_greeting(state: AgentState):
    """
    Handles greeting questions and generates appropriate responses.
    """
    user_message = state["messages"][-1].content
    logging.info(f"Handling greeting for question: '{user_message}'")

    try:
        # Create greeting detection prompt
        prompt = PromptTemplate.from_template(GREETING_PROMPT_TEMPLATE)
        chain = prompt | model
        
        # Check if it's a greeting
        result = chain.invoke({"question": user_message})
        is_greeting = result.content.strip().lower()
        
        logging.info(f"Greeting detection result for '{user_message}': '{is_greeting}'")

        if "yes" in is_greeting:
            logging.info("Greeting detected. Generating a response.")
            
            # Generate a greeting response
            greeting_response_prompt = PromptTemplate.from_template(GREETING_RESPONSE_PROMPT_TEMPLATE)
            greeting_response_chain = greeting_response_prompt | model
            
            response_result = greeting_response_chain.invoke({"question": user_message})
            greeting_response = response_result.content.strip()
            
            logging.info(f"Generated greeting response: '{greeting_response}'")
            return {
                "query_result": greeting_response,
                "sql_query": "N/A - Greeting Response",
                "error": "GREETING_HANDLED"
            }
        else:
            logging.info("Not a greeting. Proceeding to SQL processing.")
            return {"error": ""}  # Empty error means continue normal flow

    except Exception as e:
        logging.error(f"Error in handle_greeting: {e}", exc_info=True)
        return {"error": "GREETING_ERROR"}


def route_after_greeting_check(state: AgentState):
    """Routes the flow after greeting detection."""
    error = state.get("error", "")
    
    if error == "GREETING_HANDLED":
        logging.info("Greeting was handled, routing directly to output_parser")
        return "output_parser"
    elif error == "":
        logging.info("No greeting detected, continuing with normal SQL flow")
        return "selector"
    else:
        logging.info("Greeting error detected, routing to output_parser")
        return "output_parser"


def selector(state: AgentState):
    try:
        logging.info("selector: extracting schema info.")
        
        # Read YAML content from file_name
        yaml_file_name = state.get("file_name", "")
        if not yaml_file_name:
            logging.error("No yaml_file_name provided in state")
            return Command(
                update={"error": "No yaml_file_name provided in state"}, goto=END
            )
        
        logging.info(f"Reading YAML file: {yaml_file_name}")
        
        # Try multiple locations to find the YAML file
        yaml_file_path = None
        search_paths = [
            yaml_file_name,  # Absolute path or relative to CWD
            os.path.join(os.getcwd(), yaml_file_name),  # Relative to current working directory
            os.path.join(os.path.dirname(__file__), yaml_file_name),  # Relative to utils directory
            os.path.join(os.path.dirname(os.path.dirname(__file__)), yaml_file_name),  # Relative to structured_agent directory
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                yaml_file_path = path
                logging.info(f"Found YAML file at: {yaml_file_path}")
                break
        
        if not yaml_file_path:
            error_msg = f"YAML file not found: {yaml_file_name}\nSearched in:\n" + "\n".join(f"  - {p}" for p in search_paths)
            logging.error(error_msg)
            return Command(
                update={"error": error_msg}, goto=END
            )
        
        # Read and parse YAML file
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            logging.info(f"Successfully read YAML file from {yaml_file_path}: {len(text)} characters")
        
        # Extract database details from state if provided, or from YAML
        db_details = state.get("db_details", {})
        
        # Parse YAML content
        yaml_content = yaml.safe_load(text)
        
        # Extract db_details from YAML if not in state
        if not db_details and isinstance(yaml_content, dict):
            db_name = yaml_content.get("db_name", "")
            schema_name = yaml_content.get("schema_name", "")
            app_name = yaml_content.get("app_name", "")
            db_type = yaml_content.get("db_type", "")
            db_details = {
                "db_name": db_name,
                "schema_name": schema_name,
                "app_name": app_name,
                "db_type": db_type,
            }
            logging.info(f"Extracted database details from YAML: {db_name}/{schema_name}")
        schema, verified_queries, custom_instructions, fk_str, content_yaml, metrics = (
            get_data_from_yaml_file(yaml_content)
        )
        prompt = PromptTemplate(
            input_variables=[
                "question",
                "context",
                "fk_str",
                "verified_queries",
                "evidence",
                "metrics",
            ],
            template=constants.selector_template,
        )
        human_q = state["messages"][-1].content
        ans = model.invoke(
            prompt.format(
                question=human_q,
                context=schema,
                fk_str=fk_str,
                verified_queries=verified_queries,
                evidence=custom_instructions,
                metrics=metrics,
            )
        ).content
        return {
            "raw_extracted_schema_dict": parse_json(ans),
            "messages": [AIMessage(content=ans)],
            "schema": schema,
            "verified_queries": verified_queries,
            "custom_instructions": custom_instructions,
            "fk_str": fk_str,
            "content_yaml": yaml_content,
            "metrics": metrics,
            "error": "",
            "iterations": state.get("iterations", 0),
            "db_details": db_details,
        }
    except Exception as e:
        logging.error("Error in selector: %s", e)
        raise


def query_builder(state: AgentState):
    logging.info("query_builder: building SQL.")
    question = state["messages"][0].content
    rsd = state["raw_extracted_schema_dict"]
    content_yaml = state["content_yaml"]
    metrics = state["metrics"]
    logging.info(f"Building SQL query for: {question[:100]}..." if len(question) > 100 else f"Building SQL query for: {question}")

    db_schema_str, verified, evidence, fk_str, content_yaml_new, metrics_new, _ = (
        _get_db_desc_str_new(content_yaml=content_yaml, extracted_schema=rsd)
    )
    prompt = PromptTemplate(
        input_variables=[
            "desc_str",
            "query",
            "db_fk",
            "verified_queries",
            "evidence",
            "metrics",
        ],
        template=constants.decomposer_template,
    )
    ans_msg = model.invoke(
        prompt.format(
            desc_str=db_schema_str,
            query=question,
            db_fk=fk_str,
            verified_queries=verified,
            evidence=evidence,
            metrics=metrics,
        )
    )

    sql_query = parse_sql_from_string(ans_msg.content)
    logging.info(f"Generated SQL query: {sql_query[:200]}..." if len(sql_query) > 200 else f"Generated SQL query: {sql_query}")
    return {
        "sql_query": parse_sql_from_string(ans_msg.content),
        "messages": [AIMessage(content=ans_msg.content)],
    }


def query_executor(state: AgentState):
    """Executes the SQL query and generates a natural language response."""
    query = state["sql_query"]
    db_details = state["db_details"]
    db_type = db_details.get("db_type")

    logging.info("Executing SQL query against database...")
    if not query:
        raise ValueError("No SQL query generated. Please check the previous steps.")

    conn = None
    try:
        if db_type == "oracle":
            # Fetch Oracle credentials from config.ini
            oracle_user = config['oracle_dev']['user']
            oracle_password = config['oracle_dev']['password']
            oracle_dsn = config['oracle_dev']['dsn']
            
            logging.info(f"Connecting to Oracle database: {oracle_dsn}")
            conn = oracledb.connect(user=oracle_user, password=oracle_password, dsn=oracle_dsn)

        elif db_type == "snowflake":
            # Fetch Snowflake credentials from config.ini
            # Assumes a [snowflake_etl_dev] section
            logging.info("Connecting to Snowflake database...")
            conn = snowflake.connector.connect(
                user=config['snowflake_etl_dev']['user'],
                password=config['snowflake_etl_dev']['password'],
                account=config['snowflake_etl_dev']['account'],
                warehouse=config['snowflake_etl_dev']['warehouse'],
                database=config['snowflake_etl_dev']['database'],
                schema=config['snowflake_etl_dev']['schema'],
                role=config['snowflake_etl_dev']['role'],
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        logging.info("Database connection established successfully")
        cursor = conn.cursor()
        cursor.execute(query)
        result_data = cursor.fetchall()
        
        logging.info(f"Query executed successfully, retrieved {len(result_data)} rows")
        
        if isinstance(result_data, list) and len(result_data) > 100:
            total_rows = len(result_data)
            logging.info(f"Query returned {total_rows} rows, truncating to first 20 rows")
            truncated_data = result_data[:20]
            return {
                "sql_query": str(query),
                "query_result": str(truncated_data),
                "error": "",
                "exception_class": "",
                "is_truncated": True,
                "total_rows": total_rows,
                "shown_rows": 20
            }
        
        return {
            "sql_query": str(query),
            "query_result": str(result_data),
            "error": "",
            "exception_class": "",
            "is_truncated": False
        }

    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return {
            "sql_query": str(query),
            "query_result": None,
            "error": str(e),
            "exception_class": type(e).__name__,
        }
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed")


def route_to_decide(state: AgentState):
    err = state.get("error", "")
    iters = state.get("iterations", 0)
    if "No SQL found" in err:
        logging.error("No SQL query was generated, terminating.")
        return END

    if err == "":
        return "success"
    if iters >= 1 or "fatal_error" in err.lower():
        return END
    return "error"


def query_refiner(state: AgentState):
    logging.info("query_refiner: refining SQL due to error.")
    prompt = PromptTemplate(
        input_variables=[
            "desc_str",
            "sql",
            "fk_str",
            "verified_queries",
            "error",
            "exception_class",
            "query",
        ],
        template=constants.refiner_template,
    )
    desc_str, verified, evidence, fk_str, _, _, _ = _get_db_desc_str_new(
        content_yaml=state["content_yaml"],
        extracted_schema=state["raw_extracted_schema_dict"],
    )
    human_q = state["messages"][-1].content
    ans_msg = model.invoke(
        prompt.format(
            desc_str=desc_str,
            sql=state["sql_query"],
            fk_str=fk_str,
            verified_queries=verified,
            error=state.get("error", ""),
            exception_class=state.get("exception_class", ""),
            query=human_q,
        )
    )
    return {
        "sql_query": parse_sql_from_string(ans_msg.content),
        "iterations": state.get("iterations", 0) + 1,
        "messages": [AIMessage(content=ans_msg.content)],
    }

def crud_validator(state: AgentState):
    """Validates if the generated SQL contains CRUD operations and blocks them."""
    sql_query = state.get("sql_query", "").strip().upper()
    
    if not sql_query:
        logging.warning("No SQL query found to validate")
        return {"error": "No SQL query generated to validate"}
    
    # Define CRUD keywords that should be blocked
    crud_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'MERGE', 'REPLACE', 'UPSERT'
    ]
    
    # Check if SQL contains any CRUD operations
    for keyword in crud_keywords:
        if keyword in sql_query:
            logging.warning(f"CRUD operation detected: {keyword} in SQL query")
            return {
                "query_result": "Sorry you don't have enough permissions to execute this",
                "error": "CRUD_PERMISSION_DENIED",
                "sql_query": sql_query
            }
    
    # If no CRUD operations found, allow the query to proceed
    logging.info("SQL query validation passed - no CRUD operations detected")
    return {"error": ""}  # Empty error means validation passed


def output_parser(state: AgentState):
    """Parses the query result and generates a user-friendly response."""
    # Check if this is a CRUD permission denial case
    error = state.get("error", "")
    if error == "CRUD_PERMISSION_DENIED":
        # For CRUD permission denial, return the query_result directly
        query_result = state.get("query_result", "Sorry you don't have enough permissions to execute this")
        sql_query = state.get("sql_query", "Permission denied")
        
        return {
            "query_result": query_result,
            "sql_query": sql_query
        }

    # Normal processing for non-CRUD cases
    query_result = (
        state.get("query_result") if state.get("query_result") else "No data available"
    )
    user_query = state["messages"][0].content
    sql_query = (
        state.get("sql_query") if state.get("sql_query") else "No SQL query generated"
    )
    
    prompt = PromptTemplate(
        input_variables=["user_query", "query_result", "sql_query"],
        template=constants.output_parser_template,
    )

    final_result_prompt = prompt.format(
        user_query=user_query, query_result=query_result, sql_query=sql_query
    )
    message = model.invoke(final_result_prompt)
    message = message.content
    logging.info("Generated natural language response")
    
    # Check if results were truncated and add professional note
    if state.get("is_truncated", False):
        total_rows = state.get("total_rows", 0)
        shown_rows = state.get("shown_rows", 20)
        truncation_note = f"\n\n📊 Note: The query returned a large dataset with {total_rows} records. For optimal readability, only the first {shown_rows} records are displayed above."
        message = message + truncation_note
    
    return {"query_result": message}


def route_to_outputParser(state: AgentState):
    """
    Routes to the output parser based on the error state.
    """
    if state["sql_query"] == "error: No SQL found in the input string":
        return "OutputParser"
    else:
        return "QueryExecutor"
    
def route_after_crud_validation(state: AgentState):
    """Routes the flow after CRUD validation."""
    error = state.get("error", "")
    
    if error == "CRUD_PERMISSION_DENIED":
        logging.info("Routing to output_parser due to CRUD permission denial")
        return "output_parser"
    elif error == "":
        logging.info("CRUD validation passed, routing to query_executor")
        return "query_executor"
    else:
        logging.info("Other error detected, routing to output_parser")
        return "output_parser"



def build_graph(config: RunnableConfig):
    """Wrapper that builds the actual StateGraph."""
    # Call actual graph builder
    return build_main_graph(env=env)


# Build the graph
def build_main_graph(env):
    logging.info(f"Building SQL Agent graph for environment: {env}")
    global constants, model
    model = get_model()  # Assuming get_model() returns the LLM instance

    # Start the refresh in a background thread
    refresh_thread = threading.Thread(target=refresh_llm_instance, daemon=True)
    refresh_thread.start()

    constants = load_constants(config['database_type']['db_type'])

    builder = StateGraph(
        state_schema=AgentState,
        context_schema=None,
        input_schema=InputSchema,
        output_schema=ResponseSchema,
    )

    def ingress(inputs: InputSchema) -> AgentState:
        logging.info("Processing query: %s", inputs.get('question', '')[:100])
        return {
            "messages": [HumanMessage(content=inputs["question"])],
            "file_name": inputs.get("yaml_file_name", ""),
            "yaml_content": "",
            "db_details": "",
            "iterations": 0,
            "schema": "",
            "raw_extracted_schema_dict": None,
            "content_yaml": "",
            "metrics": "",
            "verified_queries": "",
            "custom_instructions": "",
            "fk_str": "",
            "sql_query": None,
            "query_result": None,
            "error": "",
            "exception_class": "",
        }

    # Add nodes to the graph
    builder.add_node("ingress", ingress)
    builder.add_node("handle_greeting", handle_greeting)
    builder.add_node("selector", selector)
    builder.add_node("query_builder", query_builder)
    builder.add_node("crud_validator", crud_validator)  # New node

    builder.add_node("query_executor", query_executor)
    builder.add_node("query_refiner", query_refiner)
    builder.add_node("output_parser", output_parser)

    try:
        # Add edges between nodes
        builder.add_edge(START, "ingress")
        builder.add_edge("ingress", "handle_greeting")

        # Route from greeting handler
        builder.add_conditional_edges(
            "handle_greeting",
            route_after_greeting_check,
            {"output_parser": "output_parser", "selector": "selector"},
        )
        builder.add_edge("selector", "query_builder")
        #builder.add_edge("query_builder", "query_executor")
        builder.add_conditional_edges(
            "query_builder",
            route_to_outputParser,
            {"OutputParser": "output_parser", "QueryExecutor": "query_executor"},
        )

         # Route from CRUD validator based on validation result
        builder.add_conditional_edges(
            "crud_validator",
            route_after_crud_validation,
            {"query_executor": "query_executor", "output_parser": "output_parser"},
        )


        builder.add_conditional_edges(
            "query_executor",
            route_to_decide,
            {"success": "output_parser", "error": "query_refiner", "fatal_error": END},
        )
        builder.add_edge("query_refiner", "query_executor")
        builder.add_edge("output_parser", END)

        builder.set_entry_point("ingress")

        compiled_graph = builder.compile()
    except Exception as e:
        logging.error("Error while building the graph: %s", e)
        raise

    return compiled_graph



