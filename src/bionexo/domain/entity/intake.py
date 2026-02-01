from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Intake(BaseModel):
    user_id: str
    food_name: str
    quantity: float  # en gramos
    kcal: float
    timestamp: datetime
    ingredients: Optional[List[str]] = None
    image_data: Optional[bytes] = None  # Imagen en bytes (BSON Binary)
    voice_description: Optional[str] = None
    feeling: Optional[str] = None  # Después de comer
    bathroom: Optional[str] = None  # Info de baño
    
    class Config:
        arbitrary_types_allowed = True