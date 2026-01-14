import argparse
import sys
import os
import threading



import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from structured_agent.utils.state import AgentState, InputSchema, ResponseSchema
from structured_agent.utils.services import *
from structured_agent.utils.nodes import *
from structured_agent.utils.constants_common import *
from structured_agent.utils.constants_oracle import *
from structured_agent.utils.mcp_oracle_service import mcp_oracle_service
from structured_agent.utils.azure_embedding_utils import CustomAzureOpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()
env = os.environ.get("ENVIRONMENT", "dev")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
config = configparser.ConfigParser()
# Check for config.ini in current working directory first
cwd_config_path = os.path.join(os.getcwd(), "config.ini")
bundled_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "utils/config.ini"
)
if os.path.exists(cwd_config_path):
    config_path = cwd_config_path
    logging.info(f"Using configuration from: {config_path}")
else:
    config_path = bundled_config_path
    logging.info(f"Using bundled configuration: {config_path}")
config.read(config_path)


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import contextmanager
from structured_agent.utils.nodes import build_graph
import langsmith as ls

@contextmanager
def graph(config):
    """
    Context-managed LangGraph for SQL Agent.
    This ensures distributed tracing when invoked from a parent LangGraph.
    """
    conf = config.get("configurable", {})
    parent_trace = conf.get("langsmith-trace")
    project_name = conf.get("langsmith-project")
    logger.info(f"graph: parent_trace: {parent_trace}")
    logger.info(f"graph: project_name: {project_name}")
    # Enable LangSmith distributed tracing linkage
    with ls.tracing_context(parent=parent_trace, project_name=project_name):
        yield build_graph(config=config)

def main():
    """Main entry point for the SQL Agent."""
    parser = argparse.ArgumentParser(description="SQL Agent CLI")
    parser.add_argument("question", type=str, help="The natural language question to convert to SQL.")
    parser.add_argument("yaml_file_name", type=str, help="The name of the YAML file containing the database schema.")
    
    args = parser.parse_args()

    # The graph is a context manager, so we can use it like this:
    with graph({}) as runnable:
        # The input to the graph is a dictionary with the question and yaml_file_name
        inputs = {"question": args.question, "yaml_file_name": args.yaml_file_name}
        
        # The invoke method runs the graph and returns the final state
        final_state = runnable.invoke(inputs)
        
        # The final result is in the "query_result" of the final state
        print("\n" + "="*80)
        print("RESULT")
        print("="*80)
        print(final_state.get("query_result", "No result found."))
        print("="*80 + "\n")

if __name__ == "__main__":
    main()

