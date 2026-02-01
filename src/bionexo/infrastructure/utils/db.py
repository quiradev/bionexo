import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import Binary
from datetime import datetime

from bionexo.domain.entity.user import User
from bionexo.domain.entity.intake import Intake
from bionexo.domain.entity.symptoms import SymptomReport
from bionexo.infrastructure.utils.functions import hash_password
from bionexo.infrastructure.utils.image_handler import compress_image
from PIL import Image
import io

def get_db():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["bionexo"]
    return db

def db_user_exists(db, email: str, password: str) -> bool:
    users_collection = db["users"]
    user = users_collection.find_one({"email": email, "password": hash_password(password)})
    return user is not None

def save_user(db, user_data: User):
    users_collection = db["users"]
    try:
        users_collection.insert_one(user_data.model_dump())
        return True
    except DuplicateKeyError:
        return None

def save_intake(db, intake: Intake) -> bool:
    """
    Guarda una ingesta en MongoDB con soporte para imágenes en BSON Binary.
    Las imágenes se comprimen automáticamente para optimizar almacenamiento.
    La colección 'intakes' debe tener un índice timeseries con user_id y timestamp.
    """
    intakes_collection = db["intakes"]
    try:
        intake_dict = intake.model_dump()
        
        # Comprimir y convertir imagen a BSON Binary si existe
        if intake_dict.get("image_data") and isinstance(intake_dict["image_data"], bytes):
            try:
                # Intentar comprimir la imagen
                image = Image.open(io.BytesIO(intake_dict["image_data"]))
                compressed_data = compress_image(image, max_width=800, quality=85)
                intake_dict["image_data"] = Binary(compressed_data)
                intake_dict["image_size_bytes"] = len(compressed_data)
            except Exception as e:
                print(f"Error comprimiendo imagen: {e}")
                intake_dict["image_data"] = Binary(intake_dict["image_data"])
                intake_dict["image_size_bytes"] = len(intake_dict["image_data"])
        
        # Asegurar que timestamp sea datetime
        if isinstance(intake_dict.get("timestamp"), str):
            intake_dict["timestamp"] = datetime.fromisoformat(intake_dict["timestamp"])
        
        intakes_collection.insert_one(intake_dict)
        return True
    except Exception as e:
        print(f"Error al guardar ingesta: {str(e)}")
        return False

def get_intakes_from_db(db, user_id: str, limit: int = 50):
    """Obtiene las ingestas de un usuario, ordenadas por timestamp descendente."""
    intakes_collection = db["intakes"]
    intakes = list(intakes_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit))
    
    # Convertir ObjectId a string para serialización
    for intake in intakes:
        if "_id" in intake:
            intake["_id"] = str(intake["_id"])
        # Las imágenes en Binary se quedan así para usarlas después si es necesario
    
    return intakes

def create_intakes_timeseries_collection(db):
    """
    Crea una colección timeseries optimizada para intakes.
    Ejecutar una sola vez.
    """
    try:
        db.create_collection(
            "intakes",
            timeseries={
                "timeField": "timestamp",
                "metaField": "user_id",
                "granularity": "minutes"
            }
        )
        print("Colección timeseries 'intakes' creada exitosamente")
    except Exception as e:
        print(f"La colección 'intakes' ya existe o hubo un error: {str(e)}")

def save_symptom_report(db, symptom_report: SymptomReport) -> bool:
    """
    Guarda un reporte de síntomas en MongoDB.
    La colección 'symptoms' debe tener un índice timeseries con user_id y timestamp.
    """
    symptoms_collection = db["symptoms"]
    try:
        report_dict = symptom_report.model_dump()
        
        # Asegurar que timestamp sea datetime
        if isinstance(report_dict.get("timestamp"), str):
            report_dict["timestamp"] = datetime.fromisoformat(report_dict["timestamp"])
        
        # Convertir objetos Symptom a dict si es necesario
        if report_dict.get("symptoms"):
            report_dict["symptoms"] = [
                s.model_dump() if hasattr(s, "model_dump") else s 
                for s in report_dict["symptoms"]
            ]
        
        symptoms_collection.insert_one(report_dict)
        return True
    except Exception as e:
        print(f"Error al guardar reporte de síntomas: {str(e)}")
        return False

def get_symptom_reports_from_db(db, user_id: str, limit: int = 50):
    """Obtiene los reportes de síntomas de un usuario, ordenados por timestamp descendente."""
    symptoms_collection = db["symptoms"]
    reports = list(symptoms_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit))
    
    # Convertir ObjectId a string para serialización
    for report in reports:
        if "_id" in report:
            report["_id"] = str(report["_id"])
    
    return reports

def create_symptoms_timeseries_collection(db):
    """
    Crea una colección timeseries optimizada para síntomas.
    Ejecutar una sola vez.
    """
    try:
        db.create_collection(
            "symptoms",
            timeseries={
                "timeField": "timestamp",
                "metaField": "user_id",
                "granularity": "minutes"
            }
        )
        print("Colección timeseries 'symptoms' creada exitosamente")
    except Exception as e:
        print(f"La colección 'symptoms' ya existe o hubo un error: {str(e)}")