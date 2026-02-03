"""
Script de migración para corregir fechas en las colecciones `intakes` y `wellness_logs`.

Características:
- Detecta y parsea timestamps (strings o datetimes).
- Convierte fechas a UTC (almacenadas en Mongo como naive UTC).
- Opciones para intentar intercambiar día/mes cuando corresponde.
- Opción para sumar un día cuando sea necesario.
- `--dry-run` por defecto; usar `--apply` para ejecutar cambios.

Uso:
  python migrate_fix_dates.py --dry-run --collections intakes,wellness_logs --fix-swap

Precaución: ejecutar primero en `--dry-run` y revisar el resumen.
"""

import os
import argparse
from datetime import datetime, timedelta
from pymongo import MongoClient
from dateutil import parser as date_parser
from dateutil.tz import tzutc, tzlocal


def get_db(uri=None):
    uri = uri or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI no definido")
    client = MongoClient(uri)
    return client.get_database("bionexo")


def parse_dt(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date_parser.parse(value)
        except Exception:
            return None
    return None


def ensure_utc_naive(dt: datetime) -> datetime:
    """Convierte a UTC y retorna datetime naive (sin tzinfo) apropiado para almacenar en MongoDB."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzlocal())
    dt_utc = dt.astimezone(tzutc())
    # PyMongo stores datetimes as naive UTC; quitamos tzinfo
    return dt_utc.replace(tzinfo=None)


def try_swap_day_month(dt: datetime):
    """Intenta intercambiar day<->month si resulta en una fecha válida.
    Retorna la nueva fecha o None si no es válida.
    """
    y = dt.year
    d = dt.day
    m = dt.month
    # Intentar swap
    try:
        swapped = datetime(y, d, m, dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=dt.tzinfo)
        return swapped
    except Exception:
        return None


def process_collection(db, coll_name, fields, dry_run=True, fix_swap=False, force_swap=False, add_day=False):
    coll = db[coll_name]
    cursor = coll.find({})
    total = 0
    modified = 0
    errors = 0

    for doc in cursor:
        total += 1
        updates = {}
        for field in fields:
            if field not in doc:
                continue
            orig = doc[field]
            parsed = parse_dt(orig)
            if parsed is None:
                # intentar saltar si es None
                continue

            new_dt = parsed

            # Si se detecta mes inválido (>12) y fix_swap está activado, intentar swap
            if (force_swap or (fix_swap and new_dt.month > 12)):
                swapped = try_swap_day_month(new_dt)
                if swapped:
                    new_dt = swapped

            # Aplicar add_day si solicitado
            if add_day:
                new_dt = new_dt + timedelta(days=1)

            # Convertir a UTC naive
            try:
                utc_naive = ensure_utc_naive(new_dt)
            except Exception as e:
                print(f"Error convirtiendo a UTC doc={doc.get('_id')} field={field}: {e}")
                errors += 1
                continue

            # Si hay diferencia significativa, registrar
            stored = doc.get(field)
            # Comparar con valor actual; si distinto, actualizar
            if isinstance(stored, datetime):
                current = stored.replace(tzinfo=None)
            else:
                # Si era string u otro, usar parsed->utc for comparison
                try:
                    cur_parsed = parse_dt(stored)
                    current = ensure_utc_naive(cur_parsed) if cur_parsed else None
                except Exception:
                    current = None

            if current != utc_naive:
                updates[field] = utc_naive

        if updates:
            modified += 1
            if dry_run:
                print(f"[DRY] {coll_name} {_id_repr(doc)} -> updates: {list(updates.keys())}")
            else:
                try:
                    coll.update_one({"_id": doc["_id"]}, {"$set": updates})
                    print(f"[OK]  {coll_name} {_id_repr(doc)} updated: {list(updates.keys())}")
                except Exception as e:
                    print(f"[ERR] {coll_name} {_id_repr(doc)} failed update: {e}")
                    errors += 1

    return {"total": total, "modified": modified, "errors": errors}


def _id_repr(doc):
    return str(doc.get("_id"))


def main():
    parser = argparse.ArgumentParser(description="Migra y corrige fechas en intakes y wellness_logs")
    parser.add_argument("--apply", action="store_true", help="Aplicar cambios en la DB (por defecto dry-run)")
    parser.add_argument("--collections", default="intakes,wellness_logs", help="Colecciones a procesar (coma-separadas)")
    parser.add_argument("--fix-swap", action="store_true", help="Intentar swap día/mes cuando el mes sea inválido")
    parser.add_argument("--force-swap", action="store_true", help="Forzar swap día/mes en todos los documentos")
    parser.add_argument("--add-day", action="store_true", help="Sumar 1 día a las fechas (use con precaución)")
    args = parser.parse_args()

    dry_run = not args.apply
    coll_names = [c.strip() for c in args.collections.split(",") if c.strip()]

    db = get_db()

    summary = {}

    for coll in coll_names:
        if coll == "intakes":
            fields = ["timestamp"]
        elif coll == "wellness_logs":
            fields = ["timestamp", "created_at"]
        else:
            # por defecto intentar timestamp y created_at
            fields = ["timestamp", "created_at"]

        print(f"Procesando colección {coll} campos={fields} dry_run={dry_run}")
        res = process_collection(db, coll, fields, dry_run=dry_run, fix_swap=args.fix_swap, force_swap=args.force_swap, add_day=args.add_day)
        summary[coll] = res

    print("\nResumen de migración:")
    for coll, res in summary.items():
        print(f"- {coll}: total={res['total']} modificados={res['modified']} errores={res['errors']}")


if __name__ == "__main__":
    main()
