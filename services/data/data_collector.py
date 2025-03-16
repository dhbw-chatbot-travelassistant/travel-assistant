from abc import ABC, abstractmethod
from pandas import read_csv
from model import Hotel
import re
from typing import List
from typing import Generator
import math


class DataCollector(ABC):
    """
    Abstract class for data collectors.
    """

    def __init__(self, source: str, chunksize: int, nrows):
        self.source = source
        self.chunksize = chunksize
        self.nrows = nrows

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

    def __init__(self, file_path: str, chunksize: int = 1000, nrows: int = None, encoding: str = 'utf-8', separator: str = ','):
        super().__init__(file_path, chunksize, nrows)
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
                          sep=self.separator, header=0, chunksize=self.chunksize, nrows=self.nrows)
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

    def __init__(self, file_path: str, chunksize: int = 1000, nrows: int = None):
        super().__init__(file_path, chunksize, nrows)
        self.csv_data_collector = CSVDataCollector(
            file_path,  chunksize, nrows, "Windows-1252", ",")

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
                # attractions = self.extract_attractions(row["Attractions"])
                # hotel.attractions = attractions["attractions"]
                # hotel.preferred_airport = attractions["preferred_airport"]

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

    def extract_attractions(self, text):

        # convert to string if it is not a string
        if isinstance(text, str):
            # Entferne die erste Zeile bis zum ersten <br />
            text = re.sub(r'^Distances are(.*?)<br />',
                          '', text, count=1).strip()

            # Entferne alle Vorkommen von <p> und </p>
            text = text.replace('</p>', '').replace('<p>', '')

            # Splitte den Text basierend auf <br /> als Delimiter
            parts = []
            if ('<br />' not in text):
                parts.append(text)
            else:
                while '<br />' in text:
                    line = re.search(r'^(.*?)<br />', text).group(1)
                    parts.append(line)
                    text = text[len(line) + 6:]

            attractions = []
            preferred_airport = None

            attraction_pattern = re.compile(
                r"(.*?) - (\d+\.\d+) km / (\d+\.\d+) mi")
            preferred_airport_pattern = re.compile(
                r".*? airport.*is (.*?) - (\d+\.\d+) km / (\d+\.\d+) mi")

            # create regular expression that splits lines by <br />

            for part in parts:
                part = part.strip()
                airport_match = preferred_airport_pattern.search(part)

                if airport_match:
                    airport_name, km_distance, mi_distance = airport_match.groups()
                    preferred_airport = Airport()
                    preferred_airport.airport_name = airport_name.strip()
                    preferred_airport.distance_km = float(km_distance)
                    preferred_airport.distance_mi = float(mi_distance)
                    continue

                match = attraction_pattern.match(part)
                if match:
                    attraction_name, km_distance, mi_distance = match.groups()
                    new_attraction = Attraction()
                    new_attraction.attraction_name = attraction_name.strip()
                    if (not new_attraction.attraction_name):
                        continue
                    new_attraction.distance_km = float(km_distance)
                    new_attraction.distance_mi = float(mi_distance)
                    attractions.append(new_attraction)

            if len(attractions) == 0:
                if text:
                    attractions = text
                else:
                    attractions = self.UNKNOWN_VALUE
        else:
            attractions = self.UNKNOWN_VALUE
            preferred_airport = self.UNKNOWN_VALUE
        return {
            "attractions": attractions,
            "preferred_airport": preferred_airport if preferred_airport else self.UNKNOWN_VALUE
        }
"""
