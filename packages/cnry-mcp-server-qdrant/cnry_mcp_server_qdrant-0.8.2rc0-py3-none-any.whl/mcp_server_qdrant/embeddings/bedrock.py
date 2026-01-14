import asyncio
import json
import os
from typing import List

from boto3 import Session
from fastembed.common.model_description import DenseModelDescription
from mcp_server_qdrant.embeddings.base import EmbeddingProvider


class BedrockEmbedProvider(EmbeddingProvider):
    """
    Bedrock implementation of the embedding provider.
    :param model_name: The name of the Bedrock model to use.
    """

    def __init__(self, model_name: str, vector_name: str, vector_size: int):
        self.model_name = model_name

        self.vector_name = vector_name
        self.vector_size = vector_size

        self._aws_session = Session()

        self._bedrock_client = self._aws_session.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_REGION"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )

    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Embed a list of documents into vectors."""
        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self._embed(document) for document in documents)
        )
        return [embedding for embedding in embeddings]

    async def embed_query(self, query: str) -> list[float]:
        """Embed a query into a vector."""
        # Run in a thread pool since FastEmbed is synchronous
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: list(self._embed(query))
        )
        return embeddings

    def get_vector_name(self) -> str:
        """
        Return the name of the vector for the Qdrant collection.
        """
        return self.vector_name

    def get_vector_size(self) -> int:
        """Get the size of the vector for the Qdrant collection."""
        return self.vector_size

    def _embed(self, body: str) -> List[float]:
        try:
            response = self._bedrock_client.invoke_model(
                body=json.dumps({"inputText": body}),
                modelId=self.model_name,
                accept="application/json",
                contentType="application/json",
            )

            return json.loads(response.get("body").read()).get("embedding")
        except Exception as e:
            raise e
