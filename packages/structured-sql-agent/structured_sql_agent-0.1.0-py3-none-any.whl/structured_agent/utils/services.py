import ast
import importlib
import sys
import os
import threading
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
import requests
import base64
import configparser
from langchain_community.utilities import SQLDatabase
import snowflake.connector
import json
from structured_agent.utils import conjur_utils
import time
from typing import List, Dict, Tuple, Any
from structured_agent.utils.azure_embedding_utils import CustomAzureOpenAIEmbedding


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


config = configparser.ConfigParser()
# Check for config.ini in current working directory first
cwd_config_path = os.path.join(os.getcwd(), "config.ini")
bundled_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
if os.path.exists(cwd_config_path):
    config_path = cwd_config_path
    import logging
    logging.info(f"Loading config from CWD: {config_path}")
else:
    config_path = bundled_config_path
    import logging
    logging.info(f"Loading bundled config: {config_path}")
config.read(config_path)
lock = threading.Lock()


def load_constants(db_type: str):
    """
    Dynamically imports the constants module based on the database type.
    """
    try:
        # Import common constants
        import structured_agent.utils.constants_common as constants

        # Dynamically import database-specific constants
        db_constants_module = importlib.import_module(
            f"structured_agent.utils.constants_{db_type.lower()}"
        )
        constants.__dict__.update(db_constants_module.__dict__)

        return constants
    except ModuleNotFoundError:
        raise ValueError(f"Constants file for {db_type} not found.")



def get_bridgeit_access_token():
    payload = "grant_type=client_credentials"
    value = base64.b64encode(
        f"{config['model_keys']['BRIDGEIT_CLIENT_ID']}:{config['model_keys']['BRIDGEIT_CLIENT_SECRET']}".encode(
            "utf-8"
        )
    ).decode("utf-8")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {value}",
    }

    token_response = requests.request(
        "POST",
        config["model_4_o_mini_api_conf"]["OAUTH_URL"],
        headers=headers,
        data=payload,
    )
    return token_response.json()["access_token"]






def get_model():
    """
    Get LLM model based on provider configuration.
    Supports: azure, openai, gemini, anthropic
    """
    retries = 3  # Number of retries
    
    # Get provider from config, default to openai
    provider = config.get("llm_provider", "provider", fallback="openai").lower()
    
    for attempt in range(1, retries + 1):
        try:
            if provider == "azure":
                # Azure OpenAI
                app_key = config["model_keys"]["BRIDGEIT_CLIENT_APPKEY"]
                model = config["model_4_o_mini_api_conf"]["OPENAI_API_MODEL"]
                temperature = float(config.get("model_4_o_mini_api_conf", "TEMPERATURE", fallback="0.1"))
                openai_api_type = config.get("model_4_o_mini_api_conf", "OPENAI_API_TYPE", fallback="azure")
                llm = AzureChatOpenAI(
                    azure_endpoint=config["model_4_o_mini_api_conf"]["OPENAI_API_BASE"],
                    api_version=config["model_4_o_mini_api_conf"]["OPENAI_API_VERSION"],
                    model=model,
                    deployment_name=model,
                    api_key=get_bridgeit_access_token(),
                    openai_api_type=openai_api_type,
                    model_kwargs={"user": f'{{"appkey": "{app_key}"}}'},
                    temperature=temperature,
                    verbose=True,
                )
                logging.info(f"✓ LLM initialized: Azure OpenAI ({model})")
                
            elif provider == "openai":
                # Standard OpenAI
                api_key = config["openai_config"]["OPENAI_API_KEY"]
                model = config["openai_config"]["MODEL"]
                temperature = float(config.get("openai_config", "TEMPERATURE", fallback="0.1"))
                llm = ChatOpenAI(
                    api_key=api_key,
                    model=model,
                    temperature=temperature,
                    verbose=True,
                )
                logging.info(f"✓ LLM initialized: OpenAI ({model})")
                
            elif provider == "gemini":
                # Google Gemini
                api_key = config["gemini_config"]["GOOGLE_API_KEY"]
                model = config["gemini_config"]["MODEL"]
                temperature = float(config.get("gemini_config", "TEMPERATURE", fallback="0.1"))
                llm = ChatGoogleGenerativeAI(
                    google_api_key=api_key,
                    model=model,
                    temperature=temperature,
                    verbose=True,
                )
                logging.info(f"✓ LLM initialized: Google Gemini ({model})")
                
            elif provider == "anthropic":
                # Anthropic Claude
                api_key = config["anthropic_config"]["ANTHROPIC_API_KEY"]
                model = config["anthropic_config"]["MODEL"]
                temperature = float(config.get("anthropic_config", "TEMPERATURE", fallback="0.1"))
                llm = ChatAnthropic(
                    anthropic_api_key=api_key,
                    model=model,
                    temperature=temperature,
                    verbose=True,
                )
                logging.info(f"✓ LLM initialized: Anthropic Claude ({model})")
                
            else:
                raise ValueError(f"Unsupported provider: {provider}. Supported providers: azure, openai, gemini, anthropic")
            
            return llm  # Return the model if successful
            
        except Exception as e:
            logging.warning(f"LLM initialization attempt {attempt}/{retries} failed: {e}")
            if attempt == retries:
                logging.error("Failed to initialize LLM after all retry attempts")
                raise  # Re-raise the exception after final attempt
            else:
                logging.info(f"Retrying LLM initialization...")







































