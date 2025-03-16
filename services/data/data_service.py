import kagglehub
from typing import List
from data_collector import DataCollector, HotelDataCollector
from embedding_creator import EmbeddingCreator, HotelPineconeEmbeddingCreator
from embedding_storage import EmbeddingStorage, PineconeEmbeddingStorage
import os
import time


class DataService:
    def __init__(self, data_collectors: List[DataCollector], embedding_creator: EmbeddingCreator, embedding_storage: EmbeddingStorage):
        self.data_collectors = data_collectors
        self.embedding_creator = embedding_creator
        self.embedding_storage = embedding_storage
        self.chunks_completed = 0

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
                self.chunks_completed += 1

        print("Data service completed.")


if __name__ == '__main__':

    ###################################### Parameters #######################################
    # Dataset
    KAGGLE_DATASET = "raj713335/tbo-hotels-dataset"  # Replace with the actual dataset
    DATASET_PATH = "datasets/hotels.csv"  # Replace with your target directory

    # Pinecone
    # Replace with your Pinecone API key
    PINECONE_API_KEY = "<YOUR_PINECONE_API_KEY>"
    PINECONE_INDEX_NAME = "hotels"
    PINECONE_NAMESPACE = "hotels"

    # Data processing
    CHUNKSIZE = 96  # Specify the number of rows to read, embed and store at a time
    NROWS = None  # Specify the number of rows to process, or 'None' to process all rows
    # Specify the number of rows to skip initially (excluding the header row)
    SKIPROWS = 0
    # Specify the number of hours to wait before running the data service again
    SCHEDULE_HOURS = 1
    ########################################################################################

    if not os.path.exists(DATASET_PATH):
        print("Downloading dataset...")
        kagglehub.dataset_download(
            KAGGLE_DATASET, path=DATASET_PATH)
    else:
        print("Dataset already exists.")

    embedding_creator = HotelPineconeEmbeddingCreator(
        PINECONE_INDEX_NAME, PINECONE_API_KEY)
    embedding_storage = PineconeEmbeddingStorage(
        PINECONE_INDEX_NAME, PINECONE_NAMESPACE, PINECONE_API_KEY)

    skiprows = SKIPROWS
    reschedule = True
    while (reschedule):
        data_collectors = [
            HotelDataCollector(DATASET_PATH, CHUNKSIZE, NROWS, skiprows)
        ]

        data_service = DataService(
            data_collectors, embedding_creator, embedding_storage)

        try:
            data_service.run()
            reschedule = False
        except Exception as e:
            print(f"An error occurred: {e}")
            print(
                f"Schedule data service to run again in {SCHEDULE_HOURS} hours...")
            time.sleep(SCHEDULE_HOURS * 3600)
            # Skip the already processed rows (preserve the header row)
            skiprows = range(2, 2 + SKIPROWS +
                             data_service.chunks_completed * CHUNKSIZE)
