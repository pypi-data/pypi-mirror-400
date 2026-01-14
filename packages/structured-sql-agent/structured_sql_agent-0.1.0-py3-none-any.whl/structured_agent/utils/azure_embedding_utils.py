import requests
import json
from typing import List
import sys
import os

sys.path.extend(
    [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..")]
)


class CustomAzureOpenAIEmbedding:
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the CustomAzureOpenAIEmbedding class with API URL, API key, and OAuth details.

        :param api_url: The endpoint URL for the embedding service.
        :param api_key: The API key for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key

    def embed_documents(
        self, texts: List[str], model: str = "bge-en-icl"
    ) -> List[List[float]]:
        """
        Embed a list of documents using the specified model.

        :param texts: List of documents to embed.
        :param model: The model to use for embedding.
        :return: List of embeddings for the provided documents.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": self.api_key,
        }

        data = {"input": texts, "model": model}

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return [embedding["embedding"] for embedding in response.json()["data"]]
        else:
            response.raise_for_status()

    def embed_query(self, text: str, model: str = "bge-en-icl") -> List[float]:
        """
        Embed a single query using the specified model.

        :param text: The query to embed.
        :param model: The model to use for embedding.
        :return: Embedding for the provided query.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": self.api_key,
        }

        data = {"input": [text], "model": model}

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            response.raise_for_status()
