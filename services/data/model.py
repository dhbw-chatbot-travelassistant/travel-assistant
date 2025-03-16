class Hotel:
    id: int
    country_code: str
    country_name: str
    city_code: str
    city_name: str
    hotel_code: str
    hotel_name: str
    hotel_rating: str
    address: str
    attractions: str
    description: str
    fax_number: str
    hotel_facilities: str
    map_coordinates: str
    phone_number: str
    pin_code: str
    hotel_website_url: str

    def __init__(self, id: int):
        self.id = id
        self.country_code = ""
        self.country_name = ""
        self.city_code = ""
        self.city_name = ""
        self.hotel_code = ""
        self.hotel_name = ""
        self.hotel_rating = ""
        self.address = ""
        self.attractions = ""
        self.description = ""
        self.fax_number = ""
        self.hotel_facilities = ""
        self.map_coordinates = ""
        self.phone_number = ""
        self.pin_code = ""
        self.hotel_website_url = ""

    def __str__(self):
        return f"Hotel '{self.hotel_name}' (ID: '{self.id})'"

    def __repr__(self):
        return f"Hotel '{self.hotel_name}' (ID: '{self.id})'"

    def to_dict(self) -> dict:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "city_code": self.city_code,
            "city_name": self.city_name,
            "hotel_code": self.hotel_code,
            "hotel_name": self.hotel_name,
            "hotel_rating": self.hotel_rating,
            "address": self.address,
            "attractions": self.attractions,
            "description": self.description,
            "fax_number": self.fax_number,
            "hotel_facilities": self.hotel_facilities,
            "map_coordinates": self.map_coordinates,
            "phone_number": self.phone_number,
            "pin_code": self.pin_code,
            "hotel_website_url": self.hotel_website_url
        }
