from pydantic import BaseModel, Field

class Intake(BaseModel):
    food_name: str
    quantity: float
    kcal: float
    timestamp: str
    feeling: str = None  # Después de comer
    bathroom: str = None  # Info de baño