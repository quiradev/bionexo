from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Intake(BaseModel):
    user_id: str
    food_name: str
    food_id: Optional[str] = None  # ID de la colección foods (ObjectId como string)
    quantity: Optional[float] = None  # en gramos (opcional)
    kcal: Optional[float] = None  # Calorías (opcional, se rellenará después con ingredientes)
    timestamp: datetime  # Timestamp exacto de la ingesta
    
    # Información de tipo de comida y hora
    meal_type: str = Field(..., description="Tipo de comida: desayuno, almuerzo, comida, cena, merienda, picar")
    
    # Cantidad - múltiples formas de entrada
    quantity_type: str = Field(..., description="Tipo de cantidad: gramos, descriptiva")
    quantity_description: Optional[str] = None  # Descripción conversacional (ej: "medio plato grande", "un vaso", "30% del plato")
    
    # Sensación después de comer (escala 1-10)
    # 1 = Con hambre, 10 = Muy hinchado/Saciado
    feeling_scale: Optional[int] = Field(None, ge=1, le=10, description="1=Con hambre, 10=Muy hinchado/Saciado")
    
    ingredients: Optional[List[str]] = None
    image_data: Optional[bytes] = None  # Imagen en bytes (BSON Binary)
    voice_description: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True