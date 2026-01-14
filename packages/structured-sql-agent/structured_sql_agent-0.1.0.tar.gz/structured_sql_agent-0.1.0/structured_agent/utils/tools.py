import json
import configparser
from langchain_openai import AzureChatOpenAI
import requests
import base64
from langchain_community.utilities import SQLDatabase
import os
import snowflake.connector
import re
import random
import time
import sqlite3
from structured_agent.utils.constants_common import subq_pattern
from typing import Dict
from typing import List
from copy import deepcopy
import pprint
import yaml
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = configparser.ConfigParser()
# Check for config.ini in current working directory first
cwd_config_path = os.path.join(os.getcwd(), "config.ini")
bundled_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
if os.path.exists(cwd_config_path):
    config_path = cwd_config_path
else:
    config_path = bundled_config_path
config.read(config_path)





def _build_bird_table_schema_list_str(table_name, new_columns_desc, new_columns_val):
    schema_desc_str = ""
    schema_desc_str += f"# Table: {table_name}\n"
    extracted_column_infos = []
    for (col_name, full_col_name, col_extra_desc), (_, col_values_str) in zip(
        new_columns_desc, new_columns_val
    ):
        col_extra_desc = (
            "And " + str(col_extra_desc)
            if col_extra_desc != "" and str(col_extra_desc) != "nan"
            else ""
        )
        col_extra_desc = col_extra_desc[:100]

        col_line_text = ""
        col_line_text += f"  ("
        col_line_text += f"{col_name},"

        if full_col_name != "":
            full_col_name = full_col_name.strip()
            col_line_text += f" {full_col_name}."
        if col_values_str != "":
            col_line_text += f" Value examples: {col_values_str}."
        if col_extra_desc != "":
            col_line_text += f" {col_extra_desc}"
        col_line_text += "),"
        extracted_column_infos.append(col_line_text)
    schema_desc_str += (
        "[\n" + "\n".join(extracted_column_infos).strip(",") + "\n]" + "\n"
    )
    return schema_desc_str








# GPT result parsing


# def parse_json(res: str) -> dict:
#     lines = res.split('\n')
#     start_idx, end_idx = -1, -1
#     for idx in range(0, len(lines)):
#         if '```json' in lines[idx]:
#             start_idx = idx
#             break
#     if start_idx == -1: return {}
#     for idx in range(start_idx + 1, len(lines)):
#         if '```' in lines[idx]:
#             end_idx = idx
#             break
#     if end_idx == -1: return {}
#     jstr = " ".join(lines[start_idx + 1: end_idx])
#     return json.loads(jstr)


# parse json output
def parse_json(res: str) -> dict:
    # lines = res.split('\n')
    # start_idx, end_idx = -1, -1
    # for idx in range(0, len(lines)):
    #     if '```json' in lines[idx]:
    #         start_idx = idx
    #         break
    # if start_idx == -1: return {}
    # for idx in range(start_idx + 1, len(lines)):
    #     if '```' in lines[idx]:
    #         end_idx = idx
    #         break
    # if end_idx == -1: return {}
    # jstr = " ".join(lines[start_idx + 1: end_idx])
    # return json.loads(jstr)
    # todo: for debug
    return {}


# check if valid format
def check_selector_response(json_data: Dict) -> bool:
    FLAGS = ["keep_all", "drop_all"]
    for k, v in json_data.items():
        if isinstance(v, str):
            if v not in FLAGS:
                print(f"error: invalid table flag: {v}\n")
                print(f"json_data: {json_data}\n\n")
                return False
        elif isinstance(v, list):
            pass
        else:
            print(f"error: invalid flag type: {v}\n")
            print(f"json_data: {json_data}\n\n")
            return False
    return True





def parse_json(text: str) -> dict:
    # 查找字符串中的 JSON 块
    start = text.find("```json")
    end = text.find("```", start + 7)

    # 如果找到了 JSON 块
    if start != -1 and end != -1:
        json_string = text[start + 7 : end]

        try:
            # 解析 JSON 字符串
            json_data = json.loads(json_string)
            valid = check_selector_response(json_data)
            if valid:
                return json_data
            else:
                return {}
        except:
            print(f"error: parse json error!\n")
            print(f"json_string: {json_string}\n\n")
            pass

    return {}


def parse_sql(res: str) -> str:
    """Only need SQL(startswith `SELECT`) of LLM result"""
    if "SELECT" not in res and "select" not in res:
        res = "SELECT " + res
    # match = re.search(parse_pattern, res, re.IGNORECASE | re.DOTALL)
    # if match:
    #     sql = match.group().strip()
    #     sql = sql.replace('```', '') # TODO
    #     sql = sql.replace('\n', ' ') # TODO
    #     return True, sql
    # else:
    #     return False, ""
    res = res.replace("\n", " ")
    return res.strip()


def parse_sql_from_string(input_string):
    sql_pattern = r"```sql(.*?)```"
    all_sqls = []
    # 将所有匹配到的都打印出来
    for match in re.finditer(sql_pattern, input_string, re.DOTALL):
        all_sqls.append(match.group(1).strip())

    if all_sqls:
        return all_sqls[-1]
    else:
        return "error: No SQL found in the input string"


# if do not need decompose, just one code block is OK!
def parse_single_sql(res: str) -> str:
    """Return SQL in markdown block"""
    lines = res.split("\n")
    iter, start_idx, end_idx = -1, -1, -1
    for idx in range(iter + 1, len(lines)):
        if "```" in lines[idx]:
            start_idx = idx
            break
    if start_idx == -1:
        return ""
    for idx in range(start_idx + 1, len(lines)):
        if "```" in lines[idx]:
            end_idx = idx
            break
    if end_idx == -1:
        return f"error: \n{res}"

    return " ".join(lines[start_idx + 1 : end_idx])














def get_data_from_yaml_file(yaml_content):
    """
    Process YAML content and return a formatted string suitable for LLM input.
    :param yaml_content: Parsed YAML content as a dictionary.
    :return: Formatted string.
    """
    tables_data = yaml_content.get("tables", [])
    if not tables_data:
        raise ValueError("No tables found in the YAML content.")
    llm_format = ""
    for table_data in tables_data:
        # table_data = yaml_content["tables"][0]  # Assume you only want the first table
        # Initialize llm_format here
        llm_format += f"Table: {table_data['name']}\n[\n"
        entries = []

        # Process dimensions
        for dim in table_data.get("dimensions", []):
            parts = []  # Initialize parts as an empty list
            if "expr" in dim:
                parts.append(f"{dim['expr']}")
            if "name" in dim:
                parts.append(f"name: {dim['name']}")
            if "description" in dim:
                parts.append(dim["description"])
            if "synonyms" in dim:
                parts.append(f"Synonyms: {dim['synonyms']}")
            if "sample_values" in dim:
                parts.append(f"Value examples: {dim['sample_values']}")
            entry = (
                "("
                + ", ".join(str(part) if part is not None else "" for part in parts)
                + ")"
            )
            entries.append(entry)

        # Process time dimensions
        for dim in table_data.get("time_dimensions", []):
            parts = []  # Initialize parts as an empty list
            if "expr" in dim:
                parts.append(f"{dim['expr']}")
            if "name" in dim:
                parts.append(f"name: {dim['name']}")
            if "description" in dim:
                parts.append(dim["description"])
            if "synonyms" in dim:
                parts.append(f"{dim['synonyms']}")
            if "sample_values" in dim:
                parts.append(f"Value examples: {dim['sample_values']}")
            entry = (
                "("
                + ", ".join(str(part) if part is not None else "" for part in parts)
                + ")"
            )
            entries.append(entry)

        # Process facts
        for dim in table_data.get("facts", []):
            parts = []  # Initialize parts as an empty list
            if "expr" in dim:
                parts.append(f"{dim['expr']}")
            if "name" in dim:
                parts.append(f"name: {dim['name']}")
            if "description" in dim:
                parts.append(dim["description"])
            if "data_type" in dim:
                parts.append(f"Data type: {dim['data_type']}")
            if "synonyms" in dim:
                parts.append(f"Synonyms: {dim['synonyms']}")
            if "sample_values" in dim:
                parts.append(f"Value examples: {dim['sample_values']}")
            entry = (
                "("
                + ", ".join(str(part) if part is not None else "" for part in parts)
                + ")"
            )
            entries.append(entry)
        llm_format += ",\n".join(entries) + "\n]\n\n"

    # print("LLM Format:\n", llm_format)

    # Create the second TXT file: Queries and Custom Instructions
    queries = yaml_content.get("verified_queries", [])
    custom_instructions = yaml_content.get("custom_instructions", "")

    verified_queries = "Queries:\n"
    for query in queries:
        verified_queries += f"- Name: {query['name']}\n"
        verified_queries += f"  Question: {query['question']}\n"
        verified_queries += f"  SQL: {query['sql']}\n\n"

    fk_str = yaml_content.get("relationships", [])
    metrics = extract_metrics(yaml_content)
    formatted_metrics = format_metrics_for_prompt(metrics)

    return (
        llm_format,
        verified_queries,
        custom_instructions,
        fk_str,
        yaml_content,
        formatted_metrics,
    )


def extract_metrics(yaml_data):
    """Extract and reformat metrics from the YAML data."""
    # Navigate to the metrics section
    metrics = yaml_data.get("tables", [])[0].get("metrics", [])

    # Reformat metrics into a readable format
    formatted_metrics = []
    for metric in metrics:
        name = metric.get("name", "Unknown Metric")
        description = metric.get("description", "No description available.")
        formula = metric.get("expr", "No formula provided.")
        synonyms = metric.get("synonyms", [])

        # Build the formatted metric data
        formatted_metrics.append(
            {
                "Metric Name": name,
                "Description": description,
                "Formula": formula,
                "Synonyms": synonyms if synonyms else None,
            }
        )

    return formatted_metrics





def format_metrics_for_prompt(metrics):
    """Format metrics into a prompt-friendly text (Markdown format)."""
    formatted = "### Metrics\n"
    for metric in metrics:
        formatted += f"- **{metric['Metric Name']}**\n"
        formatted += f"  - Description: {metric['Description']}\n"
        formatted += f"  - Formula: `{metric['Formula']}`\n"
        if metric["Synonyms"]:
            formatted += f"  - Synonyms: {', '.join(metric['Synonyms'])}\n"
        formatted += "\n"
    return formatted


def _get_db_desc_str_new(content_yaml, extracted_schema):
    print(content_yaml)
    # Parse the YAML content
    data = content_yaml
    # Function to count columns in a table
    # Count columns and tables
    tables = data.get("tables", [])
    column_counts = [count_columns(table) for table in tables]
    total_tables = len(tables)
    total_columns = sum(column_counts)
    average_columns = total_columns / total_tables if total_tables else 0

    # Output
    print(f"Number of tables: {total_tables}")
    print(f"Average columns per table: {average_columns:.2f}")

    # if (total_tables <2 or average_columns <= 30):
    print(
        "The number of tables is less than 2 or the average number of columns is less than 30."
    )
    schema, verified_queries, custom_instructions, fk_str, content_yaml, metrics = (
        get_data_from_yaml_file(content_yaml)
    )
    return (
        schema,
        verified_queries,
        custom_instructions,
        fk_str,
        content_yaml,
        metrics,
        "",
    )


def count_columns(table):
    count = 0
    count += len(table.get("dimensions", []))
    return count
