from abc import ABC, abstractmethod
from pandas import read_csv
from model import Hotel, Attraction, Airport
import re
from typing import List
from typing import Generator


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
                hotel.country_code = row["countyCode"]
                hotel.country_name = row["countyName"]
                hotel.city_code = row["cityCode"]
                hotel.city_name = row["cityName"]
                hotel.hotel_code = row["HotelCode"]
                hotel.hotel_name = row["HotelName"]
                hotel.hotel_rating = row["HotelRating"]
                hotel.address = row["Address"]

                # extract attractions and preferred airport
                attractions = HotelDataCollector.extract_attractions(
                    row["Attractions"])

                hotel.attractions = [
                    attraction for attraction in attractions["attractions"]]
                hotel.preferred_airport = attractions["preferred_airport"]

                hotel.description = row["Description"]
                hotel.fax_number = row["FaxNumber"]
                hotel.hotel_facilities = row["HotelFacilities"]
                hotel.map_coordinates = row["Map"]
                hotel.phone_number = row["PhoneNumber"]
                hotel.pin_code = row["PinCode"]
                hotel.hotel_website_url = row["HotelWebsiteUrl"]
                hotels.append(hotel)

            yield i, hotels

    def extract_attractions(text):

        # convert to string if it is not a string
        text = str(text)

        # Entferne die erste Zeile bis zum ersten <br />
        text = re.sub(r'^.*?<br />', '', text, count=1).strip()

        # Entferne alle Vorkommen von <p> und </p>
        text = text.replace('</p>', '').replace('<p>', '')

        # Splitte den Text basierend auf <br /> als Delimiter
        parts = text.split('<br />')

        attractions = []
        preferred_airport = None

        attraction_pattern = re.compile(
            r"(.*?) - (\d+\.\d+) km / (\d+\.\d+) mi")
        preferred_airport_pattern = re.compile(
            r".*? airport.*is (.*?) - (\d+\.\d+) km / (\d+\.\d+) mi")

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
                new_attraction.distance_km = float(km_distance)
                new_attraction.distance_mi = float(mi_distance)
                attractions.append(new_attraction)

        return {
            "attractions": attractions,
            "preferred_airport": preferred_airport
        }
