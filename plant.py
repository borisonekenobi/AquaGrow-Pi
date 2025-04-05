# Constants for plant happiness levels
HAPPY = "HAPPY"
NEUTRAL = "NEUTRAL"
SAD = "SAD"


class Plant:
    def __init__(self, p_name, p_image, p_min, p_max, p_category):
        self.name = p_name
        self.image = p_image
        self.min = p_min  # Minimum soil moisture
        self.max = p_max  # Maximum soil moisture
        self.category = p_category

    def get_happy_level(self, soil_moisture):
        """
        Determine plant happiness based on soil moisture level
        """
        if soil_moisture < self.min or soil_moisture > self.max:
            return SAD

        # Neutral zone is close to the edges of the acceptable range
        buffer = 5
        if (soil_moisture < self.min + buffer) or (soil_moisture > self.max - buffer):
            return NEUTRAL

        return HAPPY
