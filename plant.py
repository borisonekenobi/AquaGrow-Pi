# Constants for plant happiness levels
HAPPY = "HAPPY"
NEUTRAL = "NEUTRAL"
SAD = "SAD"


class Plant:
    def __init__(self, id, name, min, max, category):
        self.id = id
        self.name = name
        self.min = min  # Minimum soil moisture
        self.max = max  # Maximum soil moisture
        self.category = category

    def get_happy_level(self, soil_moisture):
        """
        Determine plant happiness based on soil moisture level
        """
        if soil_moisture < self.min or soil_moisture > self.max:
            return SAD

        # Neutral zone is close to the edges of the acceptable range
        buffer = 0.1
        if (soil_moisture < self.min + buffer) or (soil_moisture > self.max - buffer):
            return NEUTRAL

        return HAPPY

