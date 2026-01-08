from pydantic import BaseModel, Field


class PersonalIntakesRecommendations(BaseModel):
    age_group: str  # e.g., 'adults', 'children', 'pregnant women', etc.
    gender: str  # 'male', 'female', 'other'
    activity_level: str  # 'sedentary', 'active', 'very active'
    height_cm: float
    weight_kg: float
    health_conditions: list[str] = None  # e.g., ['diabetes', 'hypertension']
    nutrients_rdi: dict[str, float] = None  # e.g., {'protein': 50.0, 'vitamin_c': 90.0, ...}
    allergies: list[str] = None  # e.g., ['peanuts', 'shellfish']

class User(BaseModel):
    id: str
    name: str
    email: str
    personal_intakes_recommendations: PersonalIntakesRecommendations