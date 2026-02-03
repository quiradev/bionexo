"""
Script de Migración de Datos - Bionexo
Actualiza documentos existentes en MongoDB para usar los nuevos campos.

IMPORTANTE: Realizar backup de la base de datos antes de ejecutar este script.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import argparse
from typing import Optional

# Cargar variables de entorno
load_dotenv()

def get_db():
    """Obtiene conexión a la base de datos."""
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["bionexo"]
    return db

def convert_feeling_to_scale(feeling: str) -> int:
    """
    Convierte feeling categórico (string) a feeling_scale (1-10).
    
    Mapping:
    - "Con hambre" → 1-2
    - "Bien" / "Neutral" / "Neutro" → 5
    - "Saciado" → 9-10
    - "Hinchado" → 9-10
    - Otros → 5 (neutral)
    """
    if not feeling:
        return 5
    
    feeling_lower = feeling.lower().strip()
    
    if "hambre" in feeling_lower:
        return 1
    elif "hinchado" in feeling_lower:
        return 9
    elif "saciado" in feeling_lower:
        return 9
    elif "bien" in feeling_lower:
        return 7
    elif "neutro" in feeling_lower or "neutral" in feeling_lower:
        return 5
    else:
        return 5

def convert_appetite_to_scale(appetite: str) -> Optional[int]:
    """
    Convierte appetite categórico (string) a appetite_scale (1-10).
    
    Mapping:
    - "Bajo" → 1-3
    - "Normal" → 5
    - "Alto" → 8-10
    - "N/A" / None → None
    """
    if not appetite or appetite.upper() == "N/A":
        return None
    
    appetite_lower = appetite.lower().strip()
    
    if "bajo" in appetite_lower:
        return 2
    elif "normal" in appetite_lower:
        return 5
    elif "alto" in appetite_lower:
        return 9
    else:
        return 5

def convert_digestive_issues_to_scale(digestive_issues: str) -> Optional[int]:
    """
    Convierte problemas digestivos (string) a digestive_comfort_scale (1-10).
    
    Analiza la cadena de problemas y calcula un promedio ponderado:
    - "Hinchazón" → 3
    - "Estreñimiento" → 3
    - "Diarrea" → 3
    - "Reflujo" → 3
    - "Acidez" → 4
    - "Ninguno" → 10
    """
    if not digestive_issues or digestive_issues.lower() == "ninguno":
        return 10
    
    issues_lower = digestive_issues.lower()
    
    # Contar problemas
    problem_count = 0
    discomfort_level = 0
    
    if "hinchazón" in issues_lower:
        problem_count += 1
        discomfort_level += 3
    if "estreñimiento" in issues_lower:
        problem_count += 1
        discomfort_level += 3
    if "diarrea" in issues_lower:
        problem_count += 1
        discomfort_level += 3
    if "reflujo" in issues_lower:
        problem_count += 1
        discomfort_level += 3
    if "acidez" in issues_lower:
        problem_count += 1
        discomfort_level += 4
    
    if problem_count == 0:
        return 10
    
    # Escala inversa: 10 - promedio de incomodidad
    avg_discomfort = discomfort_level / problem_count
    comfort_scale = max(1, min(10, int(10 - avg_discomfort)))
    
    return comfort_scale

def migrate_intakes(db, dry_run: bool = True) -> dict:
    """
    Migra documentos en la colección 'intakes'.
    
    Cambios:
    - feeling (string) → feeling_scale (1-10)
    - Agrega meal_type si no existe (por defecto "Comida")
    - Agrega quantity_type si no existe (por defecto "gramos")
    """
    intakes_collection = db["intakes"]
    
    # Encontrar documentos sin los nuevos campos
    query = {
        "$or": [
            {"feeling_scale": {"$exists": False}},
            {"meal_type": {"$exists": False}}
        ]
    }
    
    documents = list(intakes_collection.find(query))
    count_modified = 0
    
    print(f"\n📊 MIGRACIÓN DE INGESTAS")
    print(f"─" * 50)
    print(f"Documentos a actualizar: {len(documents)}")
    
    if len(documents) == 0:
        print("✅ No hay documentos para migrar.")
        return {"total": 0, "updated": 0, "errors": 0}
    
    for doc in documents:
        try:
            update_dict = {}
            
            # Convertir feeling → feeling_scale
            if "feeling" in doc and "feeling_scale" not in doc:
                feeling_scale = convert_feeling_to_scale(doc.get("feeling"))
                update_dict["feeling_scale"] = feeling_scale
                print(f"  • {doc.get('food_name', 'Unknown')}: '{doc.get('feeling')}' → {feeling_scale}/10")
            
            # Agregar meal_type si no existe
            if "meal_type" not in doc:
                update_dict["meal_type"] = "Comida"  # Por defecto
                print(f"  • {doc.get('food_name', 'Unknown')}: meal_type = 'Comida' (default)")
            
            # Agregar quantity_type si no existe
            if "quantity_type" not in doc:
                # Si hay cantidad en gramos, usar "gramos"
                if doc.get("quantity"):
                    update_dict["quantity_type"] = "gramos"
                else:
                    update_dict["quantity_type"] = "descriptiva"
                print(f"  • {doc.get('food_name', 'Unknown')}: quantity_type = '{update_dict['quantity_type']}'")
            
            # Ejecutar actualización (delete + insert para time-series)
            if update_dict:
                if not dry_run:
                    # Para time-series: eliminar documento antiguo e insertar uno nuevo
                    intakes_collection.delete_one({"_id": doc["_id"]})
                    # Combinar documento original con actualizaciones
                    updated_doc = {**doc, **update_dict}
                    # No remover _id, es necesario mantenerlo
                    intakes_collection.insert_one(updated_doc)
                count_modified += 1
        
        except Exception as e:
            print(f"  ❌ Error procesando {doc.get('food_name', 'Unknown')}: {str(e)}")
    
    return {"total": len(documents), "updated": count_modified, "errors": 0}

def migrate_wellness_reports(db, dry_run: bool = True) -> dict:
    """
    Migra documentos en la colección 'wellness_logs'.
    
    Cambios:
    - digestive_issues permanece igual (multiselect)
    - Se agrega digestive_comfort_scale (1-10) si no existe
    - Se agrega appetite_scale (1-10) si no existe (basado en appetite antiguo si existe)
    """
    wellness_collection = db["wellness_logs"]
    
    # Encontrar documentos sin los nuevos campos
    query = {
        "$or": [
            {"digestive_comfort_scale": {"$exists": False}},
            {"appetite_scale": {"$exists": False}}
        ]
    }
    
    documents = list(wellness_collection.find(query))
    count_modified = 0
    
    print(f"\n📊 MIGRACIÓN DE REPORTES DE BIENESTAR")
    print(f"─" * 50)
    print(f"Documentos a actualizar: {len(documents)}")
    
    if len(documents) == 0:
        print("✅ No hay documentos para migrar.")
        return {"total": 0, "updated": 0, "errors": 0}
    
    for doc in documents:
        try:
            update_dict = {}
            
            # Agregar digestive_comfort_scale basado en digestive_issues si existe
            if "digestive_issues" in doc and "digestive_comfort_scale" not in doc:
                digestive_scale = convert_digestive_issues_to_scale(doc.get("digestive_issues"))
                update_dict["digestive_comfort_scale"] = digestive_scale
                print(f"  • Digestión: '{doc.get('digestive_issues', 'N/A')}' → {digestive_scale}/10")
            elif "digestive_comfort_scale" not in doc:
                # Si no hay digestive_issues, poner valor neutro
                update_dict["digestive_comfort_scale"] = 5
                print(f"  • Digestión: sin datos → 5/10 (neutro)")
            
            # Agregar appetite_scale basado en appetite antiguo si existe
            if "appetite" in doc and "appetite_scale" not in doc:
                appetite_scale = convert_appetite_to_scale(doc.get("appetite"))
                if appetite_scale is not None:
                    update_dict["appetite_scale"] = appetite_scale
                    print(f"  • Apetito: '{doc.get('appetite', 'N/A')}' → {appetite_scale}/10")
            elif "appetite_scale" not in doc:
                # Si no hay appetite antiguo, poner valor neutro
                update_dict["appetite_scale"] = 5
                print(f"  • Apetito: sin datos → 5/10 (neutro)")
            
            # Ejecutar actualización (delete + insert para time-series)
            if update_dict:
                if not dry_run:
                    # Para time-series: eliminar documento antiguo e insertar uno nuevo
                    wellness_collection.delete_one({"_id": doc["_id"]})
                    # Combinar documento original con actualizaciones
                    updated_doc = {**doc, **update_dict}
                    # No remover _id, es necesario mantenerlo
                    wellness_collection.insert_one(updated_doc)
                count_modified += 1
        
        except Exception as e:
            print(f"  ❌ Error procesando documento: {str(e)}")
    
    return {"total": len(documents), "updated": count_modified, "errors": 0}

def show_sample_documents(db):
    """Muestra ejemplos de documentos antes y después."""
    print(f"\n📄 EJEMPLOS DE DOCUMENTOS")
    print(f"─" * 50)
    
    # Mostrar una ingesta de ejemplo
    intake = db["intakes"].find_one()
    if intake:
        print(f"\n✏️ Ejemplo de Ingesta:")
        print(f"  • food_name: {intake.get('food_name')}")
        print(f"  • feeling (antiguo): {intake.get('feeling', 'N/A')}")
        print(f"  • feeling_scale (nuevo): {intake.get('feeling_scale', 'N/A')}")
        print(f"  • meal_type: {intake.get('meal_type', 'N/A')}")
        print(f"  • quantity_type: {intake.get('quantity_type', 'N/A')}")
    
    # Mostrar un reporte de ejemplo
    wellness = db["wellness_logs"].find_one()
    if wellness:
        print(f"\n✏️ Ejemplo de Reporte de Bienestar:")
        print(f"  • digestive_issues (antiguo): {wellness.get('digestive_issues', 'N/A')}")
        print(f"  • digestive_comfort_scale (nuevo): {wellness.get('digestive_comfort_scale', 'N/A')}")
        print(f"  • appetite (antiguo): {wellness.get('appetite', 'N/A')}")
        print(f"  • appetite_scale (nuevo): {wellness.get('appetite_scale', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(
        description="Script de migración de datos para Bionexo"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar la migración (sin este flag, solo se mostrará preview)"
    )
    parser.add_argument(
        "--intakes-only",
        action="store_true",
        help="Migrar solo ingestas"
    )
    parser.add_argument(
        "--wellness-only",
        action="store_true",
        help="Migrar solo reportes de bienestar"
    )
    parser.add_argument(
        "--show-samples",
        action="store_true",
        help="Mostrar ejemplos de documentos"
    )
    
    args = parser.parse_args()
    
    # Conectar a BD
    db = get_db()
    
    print("=" * 60)
    print("  🚀 SCRIPT DE MIGRACIÓN DE DATOS - BIONEXO")
    print("=" * 60)
    
    if args.show_samples:
        show_sample_documents(db)
        return
    
    dry_run = not args.execute
    
    if dry_run:
        print("\n⚠️  MODO PREVIEW (sin realizar cambios)")
        print("   Use --execute para aplicar los cambios realmente\n")
    else:
        print("\n✅ EJECUTANDO MIGRACIÓN (los cambios se aplicarán)\n")
        input("Presiona ENTER para continuar... ")
    
    results = {"intakes": {}, "wellness": {}}
    
    # Migrar ingestas
    if not args.wellness_only:
        results["intakes"] = migrate_intakes(db, dry_run=dry_run)
    
    # Migrar reportes de bienestar
    if not args.intakes_only:
        results["wellness"] = migrate_wellness_reports(db, dry_run=dry_run)
    
    # Resumen
    print(f"\n{'=' * 60}")
    print("📋 RESUMEN DE MIGRACIÓN")
    print(f"{'=' * 60}")
    
    if not args.wellness_only:
        print(f"\n📊 Ingestas:")
        print(f"  • Total procesados: {results['intakes'].get('total', 0)}")
        print(f"  • Actualizados: {results['intakes'].get('updated', 0)}")
        print(f"  • Errores: {results['intakes'].get('errors', 0)}")
    
    if not args.intakes_only:
        print(f"\n📊 Reportes de Bienestar:")
        print(f"  • Total procesados: {results['wellness'].get('total', 0)}")
        print(f"  • Actualizados: {results['wellness'].get('updated', 0)}")
        print(f"  • Errores: {results['wellness'].get('errors', 0)}")
    
    if dry_run:
        print(f"\n💡 PRÓXIMO PASO:")
        print(f"   Ejecuta con --execute para aplicar los cambios:")
        print(f"   python migrate_data.py --execute")
    else:
        print(f"\n✅ MIGRACIÓN COMPLETADA")
    
    print(f"\n{'=' * 60}\n")

if __name__ == "__main__":
    main()
