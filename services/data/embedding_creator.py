from abc import ABC, abstractmethod
from pinecone import Pinecone, ServerlessSpec
from typing import List
from model import Hotel
from google import genai


class EmbeddingCreator(ABC):
    """
    Abstract class for embedding creators
    """
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

    def __init__(self, api_key: str):
        self.api_key = api_key

    def create(self, data: List[Hotel]) -> dict:
        pc = Pinecone(api_key=self.api_key)

        hotel_data = []
        for hotel in data:
            hotel_data.append(str(hotel.to_dict()))

        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=hotel_data,
            parameters={"input_type": "passage", "truncate": "END"}
        )

        # create key-value pairs for embeddings
        embeddings_dict = {}
        for hotel, embedding in zip(data, embeddings):
            embeddings_dict[hotel.id] = {
                "values": embedding["values"],
                "metadata": hotel.to_dict()
            }

        return embeddings_dict


class HotelGeminiEmbeddingCreator(EmbeddingCreator):
    """
    Creates embeddings for hotels using Gemeni.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def create(self, data: List[Hotel]) -> dict:
        client = genai.Client(api_key=self.api_key)
        embeddings_dict = {}

        hotel_data = []
        for hotel in data:
            hotel_data.append(str(hotel.to_dict()))
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=hotel_data
        )

        for hotel, embedding in zip(data, result.embeddings):
            embeddings_dict[hotel.id] = {
                "values": embedding.values,
                "metadata": hotel.to_dict()
            }

        return embeddings_dict
