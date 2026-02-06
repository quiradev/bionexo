"""
Ejemplos de uso del sistema de registro de ingestas.
Ejecutar con: python examples_intakes.py
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bionexo.infrastructure.utils.db import get_db, save_intake, get_intakes_from_db
from bionexo.domain.entity.intake import Intake
from bionexo.domain.entity.food import Food
from bionexo.repository.foods import save_food, search_foods, get_foods_by_tag
import random

load_dotenv()

def example_save_intake():
    """Ejemplo: Guardar una ingesta simple."""
    print("\n📝 Ejemplo 1: Guardando una ingesta simple...")
    
    db = get_db()
    
    intake = Intake(
        user_id="usuario@example.com",
        food_name="Desayuno Nutritivo",
        quantity=250,
        kcal=350,
        timestamp=datetime.now(),
        ingredients=["huevos", "pan integral", "café"],
        feeling="Bien",
        voice_description="Desayuno balanceado, me siento con energía"
    )
    
    if save_intake(db, intake):
        print("✅ Ingesta guardada correctamente")
    else:
        print("❌ Error al guardar ingesta")

def example_create_food_database():
    """Ejemplo: Crear una base de datos inicial de alimentos."""
    print("\n🍽️ Ejemplo 2: Creando base de datos de alimentos...")
    
    db = get_db()
    
    foods_data = [
        {
            "name": "Pollo a la Parrilla",
            "description": "Pechuga de pollo asada sin piel",
            "ingredients": ["pollo", "limón", "sal", "pimienta"],
            "kcal_per_100g": 165,
            "protein_g": 31,
            "carbs_g": 0,
            "fat_g": 3.6,
            "tags": ["alto en proteína", "bajo en grasas", "saludable"],
            "allergens": []
        },
        {
            "name": "Arroz Integral",
            "description": "Arroz integral cocido",
            "ingredients": ["arroz integral", "agua", "sal"],
            "kcal_per_100g": 111,
            "protein_g": 2.6,
            "carbs_g": 23,
            "fat_g": 0.9,
            "tags": ["carbohidrato complejo", "fibra"],
            "allergens": []
        },
        {
            "name": "Ensalada Mixta",
            "description": "Ensalada con lechuga, tomate y pepino",
            "ingredients": ["lechuga", "tomate", "pepino", "cebolla"],
            "kcal_per_100g": 15,
            "protein_g": 0.9,
            "carbs_g": 3.1,
            "fat_g": 0.2,
            "tags": ["bajo en calorías", "vegetariano", "saludable"],
            "allergens": []
        },
        {
            "name": "Salmón a la Mantequilla",
            "description": "Filete de salmón cocido",
            "ingredients": ["salmón", "mantequilla", "ajo", "limón"],
            "kcal_per_100g": 208,
            "protein_g": 20,
            "carbs_g": 0,
            "fat_g": 13,
            "tags": ["alto en omega-3", "proteína", "saludable"],
            "allergens": ["pescado"]
        },
        {
            "name": "Yogur Griego Natural",
            "description": "Yogur griego sin azúcar añadido",
            "ingredients": ["leche", "cultivos probióticos"],
            "kcal_per_100g": 59,
            "protein_g": 10,
            "carbs_g": 3.2,
            "fat_g": 0.4,
            "tags": ["probióticos", "proteína", "bajo en grasas"],
            "allergens": ["lactosa"]
        },
        {
            "name": "Frutas Mixtas",
            "description": "Mezcla de frutas frescas",
            "ingredients": ["manzana", "plátano", "fresa", "arándano"],
            "kcal_per_100g": 50,
            "protein_g": 0.8,
            "carbs_g": 12,
            "fat_g": 0.3,
            "tags": ["vitaminas", "antioxidantes", "vegano"],
            "allergens": []
        }
    ]
    
    count = 0
    for food_data in foods_data:
        food = Food(**food_data)
        if save_food(db, food):
            print(f"✅ Alimento guardado: {food.name}")
            count += 1
        else:
            print(f"❌ Error guardando: {food.name}")
    
    print(f"\n📊 Total alimentos guardados: {count}/{len(foods_data)}")

def example_get_intakes():
    """Ejemplo: Obtener todas las ingestas de un usuario."""
    print("\n📊 Ejemplo 3: Obteniendo ingestas del usuario...")
    
    db = get_db()
    
    intakes = get_intakes_from_db(db, "usuario@example.com", limit=10)
    
    if intakes:
        print(f"\n📋 Últimas {len(intakes)} ingestas:")
        for i, intake in enumerate(intakes, 1):
            timestamp = intake.timestamp
            if hasattr(timestamp, "strftime"):
                ts_str = timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                ts_str = str(timestamp)
            
            print(f"\n{i}. {intake.food_name}")
            print(f"   📅 {ts_str}")
            print(f"   🔥 {intake.kcal} kcal | 📏 {intake.quantity}g")
            if hasattr(intake, "ingredients") and intake.ingredients:
                print(f"   🥘 {', '.join(intake.ingredients)}")
            if hasattr(intake, "feeling") and intake.feeling:
                print(f"   😊 Sentimiento: {intake.feeling}")
            if hasattr(intake, "image_data") and intake.image_data:
                print(f"   🖼️ Imagen: {getattr(intake, 'image_size_bytes', 0)} bytes")
    else:
        print("ℹ️ No hay ingestas registradas")

def example_search_foods():
    """Ejemplo: Buscar alimentos."""
    print("\n🔍 Ejemplo 4: Buscando alimentos...")
    
    db = get_db()
    
    # Buscar por nombre
    results = search_foods(db, "pollo", limit=5)
    print(f"\n✅ Alimentos encontrados con 'pollo': {len(results)}")
    for food in results:
        print(f"  • {food['name']}: {food['kcal_per_100g']} kcal/100g")
    
    # Filtrar por etiqueta
    healthy_foods = get_foods_by_tag(db, "saludable")
    print(f"\n✅ Alimentos etiquetados como 'saludable': {len(healthy_foods)}")
    for food in healthy_foods[:5]:
        print(f"  • {food['name']}")

def example_simulate_week_intakes():
    """Ejemplo: Simular una semana de ingestas."""
    print("\n📅 Ejemplo 5: Simulando ingestas de una semana...")
    
    db = get_db()
    
    user_id = "usuario@example.com"
    foods = ["Pollo a la Parrilla", "Arroz Integral", "Ensalada Mixta", "Salmón a la Mantequilla"]
    feelings = ["Bien", "Saciado", "Con hambre", "Neutro", "Hinchado"]
    
    base_time = datetime.now() - timedelta(days=7)
    count = 0
    
    for day in range(7):
        for meal_num in range(3):  # 3 comidas por día
            timestamp = base_time + timedelta(days=day, hours=8 + (meal_num * 5))
            
            intake = Intake(
                user_id=user_id,
                food_name=random.choice(foods),
                quantity=random.randint(100, 300),
                kcal=random.randint(200, 600),
                timestamp=timestamp,
                ingredients=["ingrediente1", "ingrediente2"],
                feeling=random.choice(feelings)
            )
            
            if save_intake(db, intake):
                count += 1
    
    print(f"✅ {count} ingestas de prueba guardadas para la última semana")
    
    # Mostrar estadísticas
    intakes = get_intakes_from_db(db, user_id, limit=100)
    total_kcal = sum([i.kcal or 0 for i in intakes])
    avg_kcal = total_kcal / len(intakes) if intakes else 0
    
    print(f"\n📊 Estadísticas:")
    print(f"  • Total ingestas: {len(intakes)}")
    print(f"  • Total calorías: {total_kcal:.0f}")
    print(f"  • Promedio kcal por ingesta: {avg_kcal:.0f}")

if __name__ == "__main__":
    print("=" * 60)
    print("🍽️  EJEMPLOS DE USO - SISTEMA DE INGESTAS")
    print("=" * 60)
    
    try:
        # example_save_intake()
        example_create_food_database()
        example_search_foods()
        example_simulate_week_intakes()
        example_get_intakes()
        
        print("\n" + "=" * 60)
        print("✅ Todos los ejemplos completados exitosamente")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
