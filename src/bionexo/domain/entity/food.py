"""
Entidad para representar un alimento o receta en la base de datos.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Food(BaseModel):
    """Modelo para alimentos/recetas en la colección 'foods'."""
    name: str
    description: Optional[str] = None
    ingredients: List[str]
    kcal_per_100g: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    vitamins: Optional[dict] = None  # Ej: {"vitamin_c": 10, "vitamin_a": 100}
    minerals: Optional[dict] = None   # Ej: {"calcium": 50, "iron": 2}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: Optional[List[str]] = None  # Ej: ["organic", "vegan", "gluten-free"]
    allergens: Optional[List[str]] = None
    user_created: Optional[bool] = False  # True si fue creado por usuario (receta personalizada)
    
    class Config:
        arbitrary_types_allowed = True
