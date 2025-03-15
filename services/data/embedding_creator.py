from abc import ABC, abstractmethod
from pinecone import Pinecone, ServerlessSpec
from typing import List
from model import Hotel


class EmbeddingCreator(ABC):
    """
    Abstract class for embedding creators
    """

    def __init__(self, index_name: str):
        self.index_name = index_name

    @abstractmethod
    def create(self, data: dict) -> dict:
        """
        Create embeddings from the given data and return them as a dictionary.
        The returned dictionary should have the following structure:
        {
            "key1": [0.1, 0.2, ..., 0.9],
            "key2": [0.3, 0.4, ..., 0.8],
            ...
        }
        """
        pass


class HotelPineconeEmbeddingCreator(EmbeddingCreator):
    """
    Creates embeddings for hotels using Pinecone.
    """

    def __init__(self, index_name: str, api_key: str):
        super().__init__(index_name)
        self.api_key = api_key

    def create(self, data: List[Hotel]) -> dict:
        pc = Pinecone(api_key=self.api_key)

        if not pc.has_index(self.index_name):
            pc.create_index(
                name=self.index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        hotel_data = []
        for hotel in data:
            hotel_data.append(str(hotel.to_dict()))

        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=hotel_data,
            parameters={"input_type": "passage", "truncate": "END"}
        )

        # create key-value pairs for embeddings
        embeddings = {hotel.id: embedding for hotel,
                      embedding in zip(data, embeddings)}

        return embeddings
