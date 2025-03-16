from abc import ABC, abstractmethod
from pandas import read_csv
from model import Hotel
from typing import List, Sequence, Generator
import math


class DataCollector(ABC):
    """
    Abstract class for data collectors.
    """

    def __init__(self, source: str, chunksize: int):
        self.source = source
        self.chunksize = chunksize

    @abstractmethod
    def collect(self) -> Generator[int, dict, None]:
        """
        Collect data and return it.
        """
        pass


class CSVDataCollector(DataCollector):
    """
    Collects data from a CSV file.
    """

    def __init__(self, file_path: str, chunksize: int = 1000, nrows: int = None, skiprows: int | Sequence[int] = 0, encoding: str = 'utf-8', separator: str = ','):
        super().__init__(file_path, chunksize)
        self.nrows = nrows
        self.skiprows = skiprows
        self.encoding = encoding
        self.separator = separator

    def collect(self) -> Generator[int, dict, None]:
        """
        Collect data from a CSV file and return it as a dictionary.
        The returned dictionary should have the following structure:
        {
            "source": "source name",
            "data": {
                "row1": {
                    "column1": "value",
                    "column2": "value",
                    ...
                },
                "row2": {
                    "column1": "value",
                    "column2": "value",
                    ...
                },
                ...
            }
        }
        """
        reader = read_csv(self.source, encoding=self.encoding,
                          sep=self.separator, header=0, chunksize=self.chunksize, nrows=self.nrows, skiprows=self.skiprows)
        # remove leading and trailing whitespaces
        for i, chunk in enumerate(reader):
            chunk.columns = chunk.columns.str.strip()
            yield i, {
                "source": self.source,
                "data": chunk.to_dict(orient='index')
            }


class HotelDataCollector(DataCollector):
    """
    Collects hotel data.
    """

    UNKNOWN_VALUE = "Unknown"

    def __init__(self, file_path: str, chunksize: int = 1000, nrows: int = None, skiprows=0):
        super().__init__(file_path, chunksize)
        self.csv_data_collector = CSVDataCollector(
            file_path,  chunksize, nrows, skiprows, "Windows-1252", ",")

    def collect(self) -> Generator[int, List[Hotel], None]:

        id = 1
        for i, data in self.csv_data_collector.collect():
            hotels = []
            for _, row in data["data"].items():
                hotel = Hotel(id)
                id += 1
                hotel.country_code = self.extract_str(row["countyCode"])
                hotel.country_name = self.extract_str(row["countyName"])
                hotel.city_code = self.extract_str(row["cityCode"])
                hotel.city_name = self.extract_str(row["cityName"])
                hotel.hotel_code = self.extract_str(row["HotelCode"])
                hotel.hotel_name = self.extract_str(row["HotelName"])
                hotel.hotel_rating = self.extract_str(row["HotelRating"])
                hotel.address = self.extract_str(row["Address"])
                hotel.attractions = self.extract_str(row["Attractions"])
                hotel.description = self.extract_str(row["Description"])
                hotel.fax_number = self.extract_str(row["FaxNumber"])
                hotel.hotel_facilities = self.extract_str(
                    row["HotelFacilities"])
                hotel.map_coordinates = self.extract_str(row["Map"])
                hotel.phone_number = self.extract_str(row["PhoneNumber"])
                hotel.pin_code = self.extract_str(row["PinCode"])
                hotel.hotel_website_url = self.extract_str(
                    row["HotelWebsiteUrl"])

                hotels.append(hotel)

            yield i, hotels

    def extract_str(self, value):
        if value is None:
            return self.UNKNOWN_VALUE
        if isinstance(value, float) and math.isnan(value):
            return self.UNKNOWN_VALUE
        return str(value)

    """

    
"""
