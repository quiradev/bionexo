"""
Funciones para gestionar la colección de alimentos (foods) en MongoDB.
"""

from bionexo.domain.entity.food import Food
from typing import Optional, List

def save_food(db, food: Food) -> bool:
    """Guarda un alimento/receta en la colección 'foods'."""
    foods_collection = db["foods"]
    try:
        foods_collection.insert_one(food.model_dump())
        return True
    except Exception as e:
        print(f"Error al guardar alimento: {str(e)}")
        return False

def get_food_by_name(db, name: str) -> Optional[dict]:
    """Obtiene un alimento por nombre."""
    foods_collection = db["foods"]
    food = foods_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if food:
        food["_id"] = str(food["_id"])
    return food

def search_foods(db, query: str, limit: int = 20) -> List[dict]:
    """Busca alimentos por nombre o descripción."""
    foods_collection = db["foods"]
    foods = list(foods_collection.find(
        {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        }
    ).limit(limit))
    
    for food in foods:
        if "_id" in food:
            food["_id"] = str(food["_id"])
    
    return foods

def get_foods_by_tag(db, tag: str, limit: int = 50) -> List[dict]:
    """Obtiene alimentos por etiqueta (ej: vegan, organic)."""
    foods_collection = db["foods"]
    foods = list(foods_collection.find(
        {"tags": tag}
    ).limit(limit))
    
    for food in foods:
        if "_id" in food:
            food["_id"] = str(food["_id"])
    
    return foods

def get_foods_by_allergen(db, allergen: str) -> List[dict]:
    """Obtiene alimentos que contienen un alérgeno específico."""
    foods_collection = db["foods"]
    foods = list(foods_collection.find(
        {"allergens": allergen}
    ))
    
    for food in foods:
        if "_id" in food:
            food["_id"] = str(food["_id"])
    
    return foods

def get_foods_by_calories_range(db, min_kcal: float, max_kcal: float, limit: int = 50) -> List[dict]:
    """Obtiene alimentos dentro de un rango de calorías."""
    foods_collection = db["foods"]
    foods = list(foods_collection.find(
        {"kcal_per_100g": {"$gte": min_kcal, "$lte": max_kcal}}
    ).limit(limit))
    
    for food in foods:
        if "_id" in food:
            food["_id"] = str(food["_id"])
    
    return foods

def update_food(db, name: str, update_data: dict) -> bool:
    """Actualiza un alimento existente."""
    foods_collection = db["foods"]
    try:
        result = foods_collection.update_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error al actualizar alimento: {str(e)}")
        return False

def delete_food(db, name: str) -> bool:
    """Elimina un alimento de la colección."""
    foods_collection = db["foods"]
    try:
        result = foods_collection.delete_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}}
        )
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error al eliminar alimento: {str(e)}")
        return False
