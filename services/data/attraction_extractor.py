import re

class Attraction:
    attraction_name: str
    distance_km: float
    distance_mi: float

    def __init__(self):
        self.attraction_name = ""
        self.distance_km = 0.0
        self.distance_mi = 0.0

    def __str__(self):
        return f"Attraction({self.attraction_name})"

    def __repr__(self):
        return f"Attraction({self.attraction_name})"

    def to_dict(self) -> dict:
        return {
            "attraction_name": self.attraction_name,
            "distance_km": self.distance_km,
            "distance_mi": self.distance_mi
        }


class Airport:
    airport_name: str
    distance_km: float
    distance_mi: float

    def __init__(self):
        self.airport_name = ""
        self.distance_km = 0.0
        self.distance_mi = 0.0

    def __str__(self):
        return f"Airport({self.airport_name})"

    def __repr__(self):
        return f"Airport({self.airport_name})"

    def to_dict(self) -> dict:
        return {
            "airport_name": self.airport_name,
            "distance_km": self.distance_km,
            "distance_mi": self.distance_mi
        }


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
