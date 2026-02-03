"""
Script de Testing - Verifica que la migración funcionó correctamente
Compara documentos antes y después de la migración
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import json

load_dotenv()

def get_db():
    """Obtiene conexión a la base de datos."""
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["bionexo"]
    return db

def test_intakes_migration():
    """Verifica que las ingestas se migraron correctamente."""
    db = get_db()
    intakes_collection = db["intakes"]
    
    print("\n" + "="*60)
    print("🧪 TEST: MIGRACIÓN DE INGESTAS")
    print("="*60)
    
    # Contar documentos con campos antiguos
    old_feeling = intakes_collection.count_documents({"feeling": {"$exists": True}})
    new_feeling_scale = intakes_collection.count_documents({"feeling_scale": {"$exists": True}})
    no_meal_type = intakes_collection.count_documents({"meal_type": {"$exists": False}})
    no_quantity_type = intakes_collection.count_documents({"quantity_type": {"$exists": False}})
    
    print(f"\n📊 Estadísticas:")
    print(f"  • Documentos con 'feeling' (antiguo): {old_feeling}")
    print(f"  • Documentos con 'feeling_scale' (nuevo): {new_feeling_scale}")
    print(f"  • Documentos sin 'meal_type': {no_meal_type}")
    print(f"  • Documentos sin 'quantity_type': {no_quantity_type}")
    
    # Verificaciones
    all_pass = True
    
    if no_meal_type == 0:
        print(f"\n✅ Todos los documentos tienen 'meal_type'")
    else:
        print(f"\n❌ {no_meal_type} documentos sin 'meal_type'")
        all_pass = False
    
    if no_quantity_type == 0:
        print(f"✅ Todos los documentos tienen 'quantity_type'")
    else:
        print(f"❌ {no_quantity_type} documentos sin 'quantity_type'")
        all_pass = False
    
    # Mostrar ejemplos
    print(f"\n📄 Ejemplos de Ingestas Migradas:")
    sample = intakes_collection.find_one({"feeling_scale": {"$exists": True}})
    if sample:
        print(f"\n  Documento:")
        print(f"    • food_name: {sample.get('food_name')}")
        print(f"    • feeling (antiguo): {sample.get('feeling', 'N/A')}")
        print(f"    • feeling_scale: {sample.get('feeling_scale', 'N/A')}/10 ✓")
        print(f"    • meal_type: {sample.get('meal_type', 'N/A')} ✓")
        print(f"    • quantity_type: {sample.get('quantity_type', 'N/A')} ✓")
    
    return all_pass

def test_wellness_migration():
    """Verifica que los reportes de bienestar se migraron correctamente."""
    db = get_db()
    wellness_collection = db["wellness_logs"]
    
    print("\n" + "="*60)
    print("🧪 TEST: MIGRACIÓN DE REPORTES DE BIENESTAR")
    print("="*60)
    
    # Contar documentos con campos antiguos/nuevos
    old_appetite = wellness_collection.count_documents({"appetite": {"$exists": True}})
    new_appetite_scale = wellness_collection.count_documents({"appetite_scale": {"$exists": True}})
    old_digestive = wellness_collection.count_documents({"digestive_issues": {"$exists": True}})
    new_digestive_scale = wellness_collection.count_documents({"digestive_comfort_scale": {"$exists": True}})
    
    print(f"\n📊 Estadísticas - Apetito:")
    print(f"  • Documentos con 'appetite' (original): {old_appetite}")
    print(f"  • Documentos con 'appetite_scale' (nuevo): {new_appetite_scale}")
    
    print(f"\n📊 Estadísticas - Digestión:")
    print(f"  • Documentos con 'digestive_issues' (original): {old_digestive}")
    print(f"  • Documentos con 'digestive_comfort_scale' (nuevo): {new_digestive_scale}")
    
    # Verificaciones
    all_pass = True
    
    if new_appetite_scale > 0:
        print(f"\n✅ Se encontraron {new_appetite_scale} documentos con 'appetite_scale'")
    else:
        print(f"\n⚠️  No hay documentos con 'appetite_scale' aún")
    
    if new_digestive_scale > 0:
        print(f"✅ Se encontraron {new_digestive_scale} documentos con 'digestive_comfort_scale'")
    else:
        print(f"⚠️  No hay documentos con 'digestive_comfort_scale' aún")
    
    # Mostrar ejemplos
    print(f"\n📄 Ejemplos de Reportes Migrados:")
    sample = wellness_collection.find_one(
        {"$or": [
            {"appetite_scale": {"$exists": True}},
            {"digestive_comfort_scale": {"$exists": True}}
        ]}
    )
    if sample:
        print(f"\n  Documento:")
        print(f"    • time_of_day: {sample.get('time_of_day')}")
        print(f"    • digestive_issues (original): {sample.get('digestive_issues', 'N/A')}")
        print(f"    • digestive_comfort_scale (nuevo): {sample.get('digestive_comfort_scale', 'N/A')}/10 ✓")
        print(f"    • appetite_scale (nuevo): {sample.get('appetite_scale', 'N/A')}/10 ✓")
    
    return all_pass

def test_data_validation():
    """Valida que los datos migrados tienen valores correctos."""
    db = get_db()
    
    print("\n" + "="*60)
    print("🧪 TEST: VALIDACIÓN DE DATOS")
    print("="*60)
    
    all_pass = True
    
    # Validar feeling_scale (debe ser 1-10)
    intakes = db["intakes"].find({"feeling_scale": {"$exists": True}})
    invalid_feeling = 0
    for intake in intakes:
        scale = intake.get("feeling_scale")
        if not (1 <= scale <= 10):
            print(f"  ❌ Ingesta {intake.get('food_name')}: feeling_scale = {scale} (debe ser 1-10)")
            invalid_feeling += 1
            all_pass = False
    
    if invalid_feeling == 0:
        print(f"✅ Todas las ingestas tienen feeling_scale válido (1-10)")
    
    # Validar appetite_scale (debe ser 1-10 o None)
    wellness = db["wellness_logs"].find({"appetite_scale": {"$exists": True}})
    invalid_appetite = 0
    for report in wellness:
        scale = report.get("appetite_scale")
        if scale is not None and not (1 <= scale <= 10):
            print(f"  ❌ Reporte: appetite_scale = {scale} (debe ser 1-10 o None)")
            invalid_appetite += 1
            all_pass = False
    
    if invalid_appetite == 0:
        print(f"✅ Todos los reportes tienen appetite_scale válido")
    
    # Validar digestive_comfort_scale (debe ser 1-10 o None)
    wellness = db["wellness_logs"].find({"digestive_comfort_scale": {"$exists": True}})
    invalid_digestive = 0
    for report in wellness:
        scale = report.get("digestive_comfort_scale")
        if scale is not None and not (1 <= scale <= 10):
            print(f"  ❌ Reporte: digestive_comfort_scale = {scale} (debe ser 1-10 o None)")
            invalid_digestive += 1
            all_pass = False
    
    if invalid_digestive == 0:
        print(f"✅ Todos los reportes tienen digestive_comfort_scale válido")
    
    return all_pass

def main():
    print("\n" + "="*60)
    print("  🧪 TEST SUITE - VALIDACIÓN DE MIGRACIÓN")
    print("="*60)
    
    try:
        db = get_db()
        print("\n✅ Conexión a MongoDB exitosa")
    except Exception as e:
        print(f"\n❌ Error de conexión: {str(e)}")
        return
    
    # Ejecutar tests
    test1 = test_intakes_migration()
    test2 = test_wellness_migration()
    test3 = test_data_validation()
    
    # Resumen
    print("\n" + "="*60)
    print("📋 RESUMEN DE TESTS")
    print("="*60)
    
    if test1 and test2 and test3:
        print("\n✅ TODOS LOS TESTS PASARON")
        print("\n🎉 La migración se completó correctamente!")
    else:
        print("\n⚠️  ALGUNOS TESTS NO PASARON")
        print("\n   Por favor, revisa los errores arriba.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
