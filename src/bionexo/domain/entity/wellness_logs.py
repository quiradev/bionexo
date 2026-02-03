"""
Entidad para registrar síntomas y estado del usuario en diferentes momentos del día.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Symptom(BaseModel):
    """Modelo para un síntoma específico."""
    location: str  # Zona del cuerpo (cabeza, estómago, etc.)
    description: str  # Descripción del síntoma
    intensity: int = Field(ge=1, le=10)  # Intensidad del 1-10
    duration_minutes: Optional[int] = None  # Duración en minutos

class WellnessReport(BaseModel):
    """Modelo para registrar síntomas en un momento del día."""
    user_id: str
    timestamp: datetime
    time_of_day: str  # Mañana, Tarde, Noche, o personalizado
    hour_start: int = Field(ge=0, le=23)  # Hora inicial (0-23)
    hour_end: Optional[int] = Field(ge=0, le=23, default=None)  # Hora final (opcional)
    
    # Síntomas físicos
    symptoms: Optional[List[Symptom]] = None  # Lista de síntomas
    general_pain: Optional[bool] = None  # ¿Dolor general?
    pain_description: Optional[str] = None  # Descripción del dolor general
    pain_intensity: Optional[int] = Field(ge=1, le=10, default=None)  # Intensidad del dolor
    
    # Estado emocional
    mood: Optional[str] = None  # Emoción/estado de ánimo (feliz, triste, ansioso, etc.)
    mood_intensity: Optional[int] = Field(ge=1, le=10, default=None)  # Intensidad del estado emocional
    stress_level: Optional[int] = Field(ge=1, le=10, default=None)  # Nivel de estrés
    anxiety_level: Optional[int] = Field(ge=1, le=10, default=None)  # Nivel de ansiedad
    
    # Energía y descanso
    energy_level: Optional[int] = Field(ge=1, le=10, default=None)  # Nivel de energía
    sleep_quality: Optional[int] = Field(ge=1, le=10, default=None)  # Calidad del sueño
    
    # Síntomas gastrointestinales
    digestive_issues: Optional[str] = None  # Problemas digestivos (hinchazón, estreñimiento, etc.)
    digestive_comfort_scale: Optional[int] = Field(None, ge=1, le=10, description="1=Muy hinchado, 10=Muy cómodo")  # Escala numérica adicional
    appetite_scale: Optional[int] = Field(None, ge=1, le=10, description="1=Sin apetito, 10=Muy hambriento")  # Escala numérica adicional
    nausea: Optional[bool] = None  # ¿Náusea?
    
    # Síntomas respiratorios/otros
    breathing_difficulty: Optional[bool] = None  # ¿Dificultad respiratoria?
    dizziness: Optional[bool] = None  # ¿Mareo?
    fatigue: Optional[bool] = None  # ¿Fatiga?
    
    # Notas adicionales
    notes: Optional[str] = None  # Notas libres del usuario
    medications_taken: Optional[List[str]] = None  # Medicamentos tomados
    triggers: Optional[List[str]] = None  # Posibles desencadenantes
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
