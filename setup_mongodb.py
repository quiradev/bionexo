"""
Script para configurar las colecciones de MongoDB.
Ejecutar una sola vez para inicializar la base de datos.

Uso: python setup_mongodb.py
"""

import os
from dotenv import load_dotenv
from bionexo.infrastructure.utils.db import get_db, create_intakes_timeseries_collection, create_symptoms_timeseries_collection

load_dotenv()

def setup_database():
    """Configura las colecciones necesarias en MongoDB."""
    print("🔧 Inicializando base de datos Bionexo...")
    
    db = get_db()
    
    print("\n📝 Creando índices...")
    
    # Crear índice en colección de usuarios
    users_collection = db["users"]
    try:
        users_collection.create_index("email", unique=True)
        print("✅ Índice en 'users.email' creado")
    except Exception as e:
        print(f"⚠️ Error creando índice en users: {e}")
    
    # Crear colección timeseries para intakes
    print("\n⏱️ Creando colección timeseries para 'intakes'...")
    try:
        create_intakes_timeseries_collection(db)
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Crear índice compuesto en intakes (si la colección timeseries ya existe)
    intakes_collection = db["intakes"]
    try:
        intakes_collection.create_index([("user_id", 1), ("timestamp", 1)])
        print("✅ Índice compuesto en 'intakes' creado")
    except Exception as e:
        print(f"⚠️ Error creando índice en intakes: {e}")
    
    # Crear colección de alimentos (foods)
    print("\n🍽️ Preparando colección 'foods'...")
    foods_collection = db["foods"]
    try:
        foods_collection.create_index("name", unique=True)
        print("✅ Índice en 'foods.name' creado")
    except Exception as e:
        print(f"⚠️ Error creando índice en foods: {e}")
    
    # Crear colección timeseries para symptoms
    print("\n🏥 Creando colección timeseries para 'symptoms'...")
    try:
        create_symptoms_timeseries_collection(db)
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # Crear índice compuesto en symptoms
    symptoms_collection = db["symptoms"]
    try:
        symptoms_collection.create_index([("user_id", 1), ("timestamp", -1)])
        print("✅ Índice compuesto en 'symptoms' creado")
    except Exception as e:
        print(f"⚠️ Error creando índice en symptoms: {e}")
    
    print("\n✅ Base de datos configurada exitosamente!")
    print("\n📋 Colecciones disponibles:")
    print("  - users: Información de usuarios")
    print("  - intakes: Registro de comidas (timeseries)")
    print("  - foods: Recetas y alimentos")
    print("  - symptoms: Registro de síntomas (timeseries)")

if __name__ == "__main__":
    setup_database()
