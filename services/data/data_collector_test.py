import unittest
from data_collector import HotelDataCollector


class TestHotelDataCollector(unittest.TestCase):

    def test_data_of_each_hotel_is_not_empty(self):
        data_collector = HotelDataCollector(
            "service/data/datasets/hotels.csv", 2, 10)

        for _, data in data_collector.collect():
            for hotel in data:
                self.assertTrue(hotel)
                self.assertTrue(hotel.id)
                self.assertTrue(hotel.hotel_name)
                self.assertTrue(hotel.hotel_rating)
                self.assertTrue(hotel.address)
                self.assertTrue(hotel.attractions)
                self.assertTrue(hotel.description)
                self.assertTrue(hotel.fax_number)
                self.assertTrue(hotel.hotel_facilities)
                self.assertTrue(hotel.map_coordinates)
                self.assertTrue(hotel.phone_number)
                self.assertTrue(hotel.pin_code)
                self.assertTrue(hotel.hotel_website_url)

    def test_to_dict_returns_dict(self):
        data_collector = HotelDataCollector(
            "service/data/datasets/hotels.csv", 1, 100)

        for _, data in data_collector.collect():
            for hotel in data:
                print(hotel.to_dict()["attractions"])
                self.assertTrue(hotel.to_dict())


if __name__ == '__main__':
    unittest.main()
