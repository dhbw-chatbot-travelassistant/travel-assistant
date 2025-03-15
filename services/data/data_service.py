import kagglehub
from typing import List
from data_collector import DataCollector, HotelDataCollector
from embedding_creator import EmbeddingCreator, HotelPineconeEmbeddingCreator
from embedding_storage import EmbeddingStorage, PineconeEmbeddingStorage
import os


class DataService:
    def __init__(self, data_collectors: List[DataCollector], embedding_creator: EmbeddingCreator, embedding_storage: EmbeddingStorage):
        self.data_collectors = data_collectors
        self.embedding_creator = embedding_creator
        self.embedding_storage = embedding_storage

    def run(self):
        print("Running data service...")
        for data_collector in self.data_collectors:
            print(f"Collecting data from {data_collector.source}...")
            for i, data in data_collector.collect():
                print(f"Processing chunk {i + 1}...")
                print(f"Collected data: {data}")
                print(
                    f"Creating embeddings for {data_collector.source} in index {self.embedding_creator.index_name}...")
                embeddings = self.embedding_creator.create(data)
                print(
                    f"Storing embeddings in index {self.embedding_creator.index_name}...")
                self.embedding_storage.store(embeddings)

        print("Data service completed.")


if __name__ == '__main__':

    ###################################### Parameters #######################################
    # Dataset
    KAGGLE_DATASET = "raj713335/tbo-hotels-dataset"  # Replace with the actual dataset
    DATASET_PATH = "datasets/hotels.csv"  # Replace with your target directory

    # Pinecone
    PINECONE_API_KEY = "<YOUR_PINECONE_API_KEY>"
    PINECONE_INDEX_NAME = "hotels"
    PINECONE_NAMESPACE = "hotels"

    # Data processing
    CHUNKSIZE = 1  # Specify the number of rows to read, embed and store at a time
    NROWS = 1  # Specify the number of rows to process, or 'None' to process all rows
    ########################################################################################

    if not os.path.exists(DATASET_PATH):
        print("Downloading dataset...")
        kagglehub.dataset_download(
            KAGGLE_DATASET, path=DATASET_PATH)
    else:
        print("Dataset already exists.")

    data_collectors = [
        HotelDataCollector(DATASET_PATH, CHUNKSIZE, NROWS)
    ]
    embedding_creator = HotelPineconeEmbeddingCreator(
        PINECONE_INDEX_NAME, PINECONE_API_KEY)
    embedding_storage = PineconeEmbeddingStorage(
        PINECONE_INDEX_NAME, PINECONE_NAMESPACE, PINECONE_API_KEY)

    data_service = DataService(
        data_collectors, embedding_creator, embedding_storage)

    data_service.run()
