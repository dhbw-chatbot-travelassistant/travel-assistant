from abc import ABC, abstractmethod
from pinecone import Pinecone, ServerlessSpec


class EmbeddingStorage(ABC):
    """
    Abstract class for embedding storage.
    """

    def __init__(self, index_name: str,dimension: int, namespace: str):
        self.index_name = index_name
        self.dimension = dimension
        self.namespace = namespace

    @abstractmethod
    def store(self, embeddings: dict):
        """
        Store the given data.
        """
        pass


class PineconeEmbeddingStorage(EmbeddingStorage):
    """
    Stores embeddings in Pinecone.
    """

    def __init__(self, index_name: str, dimension: int, namespace: str, api_key: str):
        super().__init__(index_name, dimension, namespace)
        self.api_key = api_key

    def store(self, embeddings: dict):
        pc = Pinecone(api_key=self.api_key)
        if not pc.has_index(self.index_name):
            pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        index = pc.Index(self.index_name)

        vectors = []
        for key, embedding in embeddings.items():
            vectors.append({
                "id": str(key),
                "values": embedding['values'],
                "metadata": embedding['metadata']
            })

        index.upsert(
            vectors=vectors,
            namespace=self.namespace
        )
