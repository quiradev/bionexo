from typing import Literal
from pydantic import BaseModel, Field


from typing import Literal, Optional
from pydantic import BaseModel, Field, PositiveFloat

# 1. Definimos las constantes en clases "namespace" para evitar "magic strings"
# Esto te permite usar Activity.ACTIVE en tu código en lugar de escribir "active" cada vez.
class AgeGroup:
    BABY = "baby"
    CHILDREN = "children"
    TEEN = "teen"
    ADULT = "adult"
    ELDERLY = "elderly"

class Sex:
    MALE = "male"
    FEMALE = "female"

class Activity:
    SEDENTARY = "sedentary"
    ACTIVE = "active"
    VERY_ACTIVE = "very active"

# 2. Definimos los Tipos Literales para que el editor (IDE) y Pydantic validen
# Nota: Repetimos los strings aquí para que el type checker estático funcione al 100%
AgeGroupType = Literal["baby", "children", "teen", "adult", "elderly"]
SexType = Literal["male", "female"]
ActivityType = Literal["sedentary", "active", "very active"]

# 3. La Clase Principal
class PersonalIntakesRecommendations(BaseModel):
    # Demográficos
    age_group: AgeGroupType = Field(..., description="Grupo etario del usuario")
    sex: SexType = Field(..., description="Sexo biológico")
    
    # Nivel de actividad usando el alias de tipo
    activity_level: ActivityType = Field(
        ..., 
        description="Nivel de actividad física"
    )

    # Medidas Físicas (Usamos PositiveFloat para evitar valores negativos)
    height_cm: PositiveFloat = Field(..., gt=30, lt=300, description="Altura en cm")
    weight_kg: PositiveFloat = Field(..., gt=2, lt=600, description="Peso en kg")

    # Listas y Diccionarios (Opcionales con default factory para seguridad)
    health_conditions: list[str] = Field(
        default_factory=list, 
        description="Lista de patologías (ej. diabetes)"
    )
    
    allergies: list[str] = Field(
        default_factory=list, 
        description="Lista de alergias alimentarias"
    )

    # Diccionario opcional para valores precalculados
    nutrients_rdi: Optional[dict[str, float]] = Field(
        default=None,
        description="Valores de referencia de nutrientes personalizados"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "age_group": AgeGroup.ADULT,  # Usamos la constante en el ejemplo
                "sex": Sex.FEMALE,
                "activity_level": Activity.ACTIVE,
                "height_cm": 165.0,
                "weight_kg": 60.0,
                "health_conditions": ["hypertension"],
                "allergies": []
            }
        }

class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    personal_intakes_recommendations: PersonalIntakesRecommendations
