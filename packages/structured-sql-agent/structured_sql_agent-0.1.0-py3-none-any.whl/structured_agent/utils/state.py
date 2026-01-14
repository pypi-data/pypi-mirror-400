from typing import Optional, TypedDict
from typing_extensions import Annotated
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    file_name: str
    messages: Annotated[list[AIMessage], add_messages]
    iterations: int
    raw_extracted_schema_dict: Optional[dict]
    schema: str
    verified_queries: str
    custom_instructions: str
    fk_str: str
    content_yaml: str
    metrics: str
    yaml_content: str
    db_details: dict
    sql_query: Optional[str]
    query_result: Optional[str]
    error: Optional[str]
    exception_class: Optional[str]
    is_truncated: Optional[bool]
    total_rows: Optional[int]
    shown_rows: Optional[int]


class InputSchema(TypedDict):
    question: str
    yaml_file_name: str
    db_details: dict


class ResponseSchema(TypedDict, total=False):
    query_result: str
    error: Optional[str]
    sql_query: Optional[str]
