SAD: str = 'sad'
NEUTRAL: str = 'neutral'
HAPPY: str = 'happy'


class Plant:
    id: int
    name: str
    min_moisture: float
    max_moisture: float
    category: str

    def __init__(self, plant_id: int, name: str, min_moisture: float, max_moisture: float, category: str) -> None:
        self.id = plant_id
        self.name = name
        self.min_moisture = min_moisture
        self.max_moisture = max_moisture
        self.category = category

    def get_happy_level(self, soil_moisture: float) -> str:
        """
        Returns the happy level of the plant based on the soil moisture.
        """
        if soil_moisture < self.min_moisture or soil_moisture > self.max_moisture:
            return SAD
        elif soil_moisture <= self.min_moisture + 0.05 or soil_moisture >= self.max_moisture - 0.05:
            return NEUTRAL
        else:
            return HAPPY
