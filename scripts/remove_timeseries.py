"""
Script para convertir colecciones time-series en colecciones regulares.

Uso:
  python remove_timeseries.py --dry-run --collections intakes,wellness_logs
  python remove_timeseries.py --apply --collections intakes

Opciones:
  --dry-run   : Solo mostrar lo que se haría (por defecto si no se pasa --apply)
  --apply     : Ejecutar los cambios
  --force-backup : Si existe backup con el mismo nombre, sobrescribirlo

Precaución: ejecutar primero en `--dry-run` y revisar la salida.
"""

import os
import argparse
from pymongo import MongoClient
from pymongo.errors import BulkWriteError


def get_db(uri=None):
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI no definido")
    client = MongoClient(uri)
    return client.get_database("bionexo")


def is_timeseries(db, coll_name):
    info = db.command("listCollections", filter={"name": coll_name})
    first = info.get("cursor", {}).get("firstBatch", [])
    if not first:
        return False, None
    opts = first[0].get("options", {})
    ts = opts.get("timeseries")
    return (ts is not None), ts


def copy_collection(src, dst, batch_size=1000, force=False):
    # dst is a Collection object
    if dst.name in src.database.list_collection_names() and force:
        dst.drop()

    # Avoid no_cursor_timeout (not allowed on some Atlas tiers)
    cursor = src.find({}).batch_size(batch_size)
    buf = []
    inserted = 0
    for doc in cursor:
        buf.append(doc)
        if len(buf) >= batch_size:
            dst.insert_many(buf)
            inserted += len(buf)
            buf = []
    if buf:
        dst.insert_many(buf)
        inserted += len(buf)
    return inserted


def process_collection(db, coll_name, dry_run=True, force_backup=False):
    coll = db[coll_name]
    ts_flag, ts_opts = is_timeseries(db, coll_name)
    if not ts_flag:
        print(f"Colección '{coll_name}' no es time-series. Se omite.")
        return {"coll": coll_name, "skipped": True}

    backup_name = f"{coll_name}_backup_ts"
    if dry_run:
        count = coll.count_documents({})
        print(f"[DRY] {coll_name}: es time-series, documentos={count}. Se crearÃ­a backup '{backup_name}' y se recrearía como colección regular.")
        return {"coll": coll_name, "dry_count": count}

    # En apply mode
    # 1) crear backup
    if backup_name in db.list_collection_names():
        if force_backup:
            print(f"Backup '{backup_name}' ya existe, se eliminará por --force-backup")
            db[backup_name].drop()
        else:
            raise RuntimeError(f"Backup '{backup_name}' ya existe. Use --force-backup para sobrescribir.")

    print(f"Creando backup '{backup_name}' desde '{coll_name}'... Esto puede tardar.")
    backup_coll = db[backup_name]
    inserted = copy_collection(coll, backup_coll, force=True)
    print(f"Backup creado: {inserted} documentos copiados a '{backup_name}'.")

    # 2) drop original
    print(f"Eliminando colección original '{coll_name}'...")
    db.drop_collection(coll_name)

    # 3) crear colección regular vacía
    print(f"Creando nueva colección regular '{coll_name}'...")
    db.create_collection(coll_name)

    # 4) copiar desde backup a nueva
    print(f"Restaurando datos desde '{backup_name}' a '{coll_name}'...")
    new_coll = db[coll_name]
    restored = copy_collection(backup_coll, new_coll)
    print(f"Restauración completada: {restored} documentos insertados en '{coll_name}'.")

    # 5) eliminar backup
    print(f"Eliminando backup temporal '{backup_name}'...")
    db.drop_collection(backup_name)

    return {"coll": coll_name, "restored": restored}


def main():
    parser = argparse.ArgumentParser(description="Eliminar indices time-series convirtiendo a colecciones regulares")
    parser.add_argument("--apply", action="store_true", help="Aplicar cambios (por defecto dry-run)")
    parser.add_argument("--collections", default="intakes,wellness_logs,symptoms", help="Colecciones a procesar (coma-separadas)")
    parser.add_argument("--force-backup", action="store_true", help="Sobrescribir backup existente si lo hay")
    args = parser.parse_args()

    dry_run = not args.apply
    coll_names = [c.strip() for c in args.collections.split(",") if c.strip()]

    db = get_db()

    summary = {}
    for coll in coll_names:
        try:
            print(f"Procesando colección '{coll}' (dry_run={dry_run})")
            res = process_collection(db, coll, dry_run=dry_run, force_backup=args.force_backup)
            summary[coll] = res
        except Exception as e:
            print(f"Error procesando '{coll}': {e}")
            summary[coll] = {"error": str(e)}

    print("\nResumen:")
    for coll, info in summary.items():
        print(f"- {coll}: {info}")


if __name__ == "__main__":
    main()
