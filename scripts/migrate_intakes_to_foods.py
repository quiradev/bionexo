#!/usr/bin/env python3
"""
Script para migrar intakes históricos a la colección 'foods' y actualizar las referencias.

Permite:
1. Crear comidas en la colección 'foods' basadas en histórico de intakes
2. Actualizar referencias food_id en las intakes existentes
3. Filtrar por usuario específico
4. Ver estadísticas de migración

Uso:
    python migrate_intakes_to_foods.py --user email@example.com
    python migrate_intakes_to_foods.py --show-stats
    python migrate_intakes_to_foods.py --all
"""

import os
import sys
from dotenv import load_dotenv
from bionexo.infrastructure.utils.db import get_db
from bionexo.domain.entity.food import Food
from bionexo.repository.foods import create_or_update_food, get_food_id_by_name
from collections import defaultdict
import argparse
from datetime import datetime

load_dotenv()

def get_unique_foods_from_intakes(db, user_id: str = None):
    """Obtiene las comidas únicas del histórico de intakes, opcionalmente filtrado por usuario."""
    intakes_collection = db["intakes"]
    
    query = {}
    if user_id:
        query["user_id"] = user_id
    
    # Obtener todos los intakes únicos por nombre de comida
    intakes = list(intakes_collection.find(query).sort("timestamp", -1))
    
    # Agrupar por food_name (case-insensitive)
    foods_dict = {}
    for intake in intakes:
        food_name = intake.get("food_name", "Unknown").lower()
        
        if food_name not in foods_dict:
            foods_dict[food_name] = {
                "name": intake.get("food_name", "Unknown"),
                "user_id": intake.get("user_id"),
                "ingredients": intake.get("ingredients", []),
                "kcal": intake.get("kcal"),
                "quantity": intake.get("quantity"),
                "count": 0,
                "first_date": intake.get("timestamp")
            }
        
        foods_dict[food_name]["count"] += 1
        if intake.get("timestamp") and foods_dict[food_name]["first_date"]:
            if intake.get("timestamp") > foods_dict[food_name]["first_date"]:
                foods_dict[food_name]["first_date"] = intake.get("timestamp")
    
    return list(foods_dict.values())

def migrate_intakes_for_user(db, user_id: str, dry_run: bool = False):
    """
    Migra los intakes de un usuario a la colección 'foods'.
    Crea los alimentos y actualiza las referencias en intakes.
    
    Args:
        db: Conexión a MongoDB
        user_id: Email del usuario
        dry_run: Si True, solo muestra qué haría sin hacer cambios
    
    Returns:
        dict con estadísticas de migración
    """
    intakes_collection = db["intakes"]
    stats = {
        "foods_created": 0,
        "foods_updated": 0,
        "intakes_updated": 0,
        "errors": 0,
        "user_id": user_id
    }
    
    # Obtener comidas únicas del usuario
    unique_foods = get_unique_foods_from_intakes(db, user_id)
    
    print(f"\n{'='*70}")
    print(f"Migrando {len(unique_foods)} comidas únicas para usuario: {user_id}")
    print(f"{'='*70}\n")
    
    # Para cada comida única, crear o actualizar en foods
    for i, food_info in enumerate(unique_foods, 1):
        food_name = food_info["name"]
        
        print(f"[{i}/{len(unique_foods)}] Procesando: {food_name}")
        print(f"    - Registros encontrados: {food_info['count']}")
        print(f"    - Ingredientes: {', '.join(food_info['ingredients'][:3]) if food_info['ingredients'] else 'N/A'}")
        
        if not dry_run:
            try:
                # Calcular calorías por 100g
                kcal_per_100g = 0
                if food_info.get("kcal") and food_info.get("quantity"):
                    kcal_per_100g = (food_info["kcal"] / food_info["quantity"]) * 100
                
                # Crear el alimento
                food = Food(
                    name=food_name,
                    ingredients=food_info.get("ingredients", []),
                    kcal_per_100g=kcal_per_100g,
                    user_created=True,
                    tags=["migrated_from_intake"]
                )
                
                # Guardar o actualizar
                existing_id = get_food_id_by_name(db, food_name)
                food_id = create_or_update_food(db, food)
                
                if existing_id:
                    stats["foods_updated"] += 1
                    print(f"    ✓ Actualizada (ID: {food_id})")
                else:
                    stats["foods_created"] += 1
                    print(f"    ✓ Creada (ID: {food_id})")
                
                # Actualizar todos los intakes con este food_name
                if food_id:
                    result = intakes_collection.update_many(
                        {
                            "user_id": user_id,
                            "food_name": {"$regex": f"^{food_name}$", "$options": "i"}
                        },
                        {"$set": {"food_id": food_id}}
                    )
                    stats["intakes_updated"] += result.modified_count
                    print(f"    ✓ Actualizados {result.modified_count} intakes")
                
            except Exception as e:
                stats["errors"] += 1
                print(f"    ✗ Error: {str(e)}")
        else:
            print(f"    (DRY RUN - No se realizan cambios)")
        
        print()
    
    return stats

def migrate_all_intakes(db, dry_run: bool = False):
    """
    Migra todos los intakes de todos los usuarios.
    
    Args:
        db: Conexión a MongoDB
        dry_run: Si True, solo muestra qué haría sin hacer cambios
    
    Returns:
        dict con estadísticas totales de migración
    """
    intakes_collection = db["intakes"]
    
    # Obtener usuarios únicos
    users = list(intakes_collection.find().distinct("user_id"))
    
    print(f"\n{'='*70}")
    print(f"Migrando intakes de {len(users)} usuarios")
    print(f"{'='*70}\n")
    
    total_stats = {
        "total_foods_created": 0,
        "total_foods_updated": 0,
        "total_intakes_updated": 0,
        "total_errors": 0,
        "by_user": {}
    }
    
    for user_id in users:
        user_stats = migrate_intakes_for_user(db, user_id, dry_run)
        
        total_stats["total_foods_created"] += user_stats["foods_created"]
        total_stats["total_foods_updated"] += user_stats["foods_updated"]
        total_stats["total_intakes_updated"] += user_stats["intakes_updated"]
        total_stats["total_errors"] += user_stats["errors"]
        total_stats["by_user"][user_id] = user_stats
    
    return total_stats

def show_migration_stats(db):
    """Muestra estadísticas de la migración actual."""
    intakes_collection = db["intakes"]
    foods_collection = db["foods"]
    
    # Estadísticas de intakes
    total_intakes = intakes_collection.count_documents({})
    intakes_with_food_id = intakes_collection.count_documents({"food_id": {"$ne": None}})
    intakes_without_food_id = total_intakes - intakes_with_food_id
    
    # Estadísticas de foods
    total_foods = foods_collection.count_documents({})
    user_created_foods = foods_collection.count_documents({"user_created": True})
    
    # Por usuario
    users = list(intakes_collection.find().distinct("user_id"))
    
    print(f"\n{'='*70}")
    print("📊 ESTADÍSTICAS DE MIGRACIÓN")
    print(f"{'='*70}\n")
    
    print("📈 Intakes:")
    print(f"  - Total intakes: {total_intakes}")
    print(f"  - Con food_id: {intakes_with_food_id} ({100*intakes_with_food_id//total_intakes if total_intakes else 0}%)")
    print(f"  - Sin food_id: {intakes_without_food_id}")
    
    print(f"\n🍽️  Comidas (Foods):")
    print(f"  - Total comidas: {total_foods}")
    print(f"  - Creadas por usuario: {user_created_foods}")
    
    print(f"\n👥 Usuarios:")
    for user_id in users:
        user_intakes = intakes_collection.count_documents({"user_id": user_id})
        user_foods = intakes_collection.count_documents({
            "user_id": user_id,
            "food_id": {"$ne": None}
        })
        print(f"  - {user_id}: {user_intakes} intakes, {user_foods} con food_id")
    
    print(f"\n{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Migrar intakes históricos a la colección 'foods'",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python migrate_intakes_to_foods.py --user usuario@email.com
  python migrate_intakes_to_foods.py --all
  python migrate_intakes_to_foods.py --show-stats
  python migrate_intakes_to_foods.py --user usuario@email.com --dry-run
        """
    )
    
    parser.add_argument("--user", type=str, help="Email del usuario para migrar")
    parser.add_argument("--all", action="store_true", help="Migrar todos los usuarios")
    parser.add_argument("--show-stats", action="store_true", help="Mostrar estadísticas de migración")
    parser.add_argument("--dry-run", action="store_true", help="Simular migración sin hacer cambios")
    
    args = parser.parse_args()
    
    db = get_db()
    
    try:
        if args.show_stats:
            show_migration_stats(db)
        elif args.user:
            stats = migrate_intakes_for_user(db, args.user, args.dry_run)
            print(f"\n{'='*70}")
            print("✅ RESUMEN DE MIGRACIÓN")
            print(f"{'='*70}")
            print(f"Comidas creadas: {stats['foods_created']}")
            print(f"Comidas actualizadas: {stats['foods_updated']}")
            print(f"Intakes actualizadas: {stats['intakes_updated']}")
            print(f"Errores: {stats['errors']}")
            if args.dry_run:
                print("\n⚠️  (DRY RUN - No se realizaron cambios reales)")
            print(f"{'='*70}\n")
        elif args.all:
            stats = migrate_all_intakes(db, args.dry_run)
            print(f"\n{'='*70}")
            print("✅ RESUMEN TOTAL DE MIGRACIÓN")
            print(f"{'='*70}")
            print(f"Comidas creadas: {stats['total_foods_created']}")
            print(f"Comidas actualizadas: {stats['total_foods_updated']}")
            print(f"Intakes actualizadas: {stats['total_intakes_updated']}")
            print(f"Errores: {stats['total_errors']}")
            if args.dry_run:
                print("\n⚠️  (DRY RUN - No se realizaron cambios reales)")
            print(f"{'='*70}\n")
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
