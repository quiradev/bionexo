# 📦 Scripts de Migración - Instrucciones Rápidas

## 🎯 Resumen

Se han creado dos scripts Python para migrar y validar los datos existentes en MongoDB según los nuevos cambios de campos:

| Script | Propósito |
|--------|-----------|
| `migrate_data.py` | Actualiza documentos existentes con los nuevos campos |
| `test_migration.py` | Valida que la migración se realizó correctamente |

---

## ⚡ Inicio Rápido

### 1️⃣ Ver qué cambiaría (sin hacer nada)
```bash
cd d:\workspace\bionexo
python migrate_data.py
```

### 2️⃣ Ejecutar la migración
```bash
python migrate_data.py --execute
```

### 3️⃣ Validar que todo está correcto
```bash
python test_migration.py
```

---

## 📋 Cambios que realiza `migrate_data.py`

### Ingestas (intakes)
```
feeling: "Saciado"        →  feeling_scale: 9
feeling: "Con hambre"     →  feeling_scale: 1
feeling: "Bien"           →  feeling_scale: 7
(sin meal_type)           →  meal_type: "Comida" (default)
(sin quantity_type)       →  quantity_type: "gramos" o "descriptiva"
```

### Reportes de Bienestar (wellness_logs)
```
appetite: "Bajo"          →  appetite_scale: 2
appetite: "Normal"        →  appetite_scale: 5
appetite: "Alto"          →  appetite_scale: 9
digestive_issues: "..."   →  digestive_comfort_scale: 1-10
```

---

## 🔍 Opciones del Script

```bash
# Solo preview
python migrate_data.py

# Ejecutar migración
python migrate_data.py --execute

# Solo migrar ingestas
python migrate_data.py --intakes-only --execute

# Solo migrar reportes de bienestar
python migrate_data.py --wellness-only --execute

# Ver ejemplos de documentos
python migrate_data.py --show-samples

# Validar migración
python test_migration.py
```

---

## ✅ Checklist Recomendado

```
1. ☐ Conectar a la BD (verificar MONGODB_URI en .env)
2. ☐ Ver preview: python migrate_data.py
3. ☐ Revisar cambios propuestos
4. ☐ Hacer backup de la BD (recomendado)
5. ☐ Ejecutar: python migrate_data.py --execute
6. ☐ Presionar ENTER para confirmar
7. ☐ Validar: python test_migration.py
8. ☐ Ver ejemplos: python migrate_data.py --show-samples
```

---

## 📊 Ejemplo de Ejecución

```
$ python migrate_data.py

============================================================
  🚀 SCRIPT DE MIGRACIÓN DE DATOS - BIONEXO
============================================================

⚠️  MODO PREVIEW (sin realizar cambios)

📊 MIGRACIÓN DE INGESTAS
──────────────────────────────────────────────────
Documentos a actualizar: 3
  • Pollo con Arroz: 'Saciado' → 9/10
  • Ensalada: 'Con hambre' → 1/10
  • Pasta: 'Bien' → 7/10

📊 MIGRACIÓN DE REPORTES DE BIENESTAR
──────────────────────────────────────────────────
Documentos a actualizar: 2
  • Digestión: 'Hinchazón, Acidez' → 4/10
  • Apetito: 'Bajo' → 2/10

==============================================================
📋 RESUMEN DE MIGRACIÓN
==============================================================

📊 Ingestas:
  • Total procesados: 3
  • Actualizados: 3
  • Errores: 0

📊 Reportes de Bienestar:
  • Total procesados: 2
  • Actualizados: 2
  • Errores: 0

💡 PRÓXIMO PASO:
   Ejecuta con --execute para aplicar los cambios:
   python migrate_data.py --execute
```

---

## 🧪 Validación Post-Migración

```
$ python test_migration.py

============================================================
🧪 TEST SUITE - VALIDACIÓN DE MIGRACIÓN
============================================================

✅ MIGRACIÓN DE INGESTAS
  • Documentos con 'feeling_scale': 3
  ✅ Todos tienen 'meal_type'
  ✅ Todos tienen 'quantity_type'

✅ MIGRACIÓN DE REPORTES
  • Documentos con 'appetite_scale': 2
  • Documentos con 'digestive_comfort_scale': 2

✅ VALIDACIÓN DE DATOS
  ✅ Todos los valores están en rango 1-10

============================================================
📋 RESUMEN
============================================================
✅ TODOS LOS TESTS PASARON
🎉 ¡La migración se completó correctamente!
```

---

## 🐛 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| "MONGODB_URI not found" | Verifica `.env` tenga `MONGODB_URI=...` |
| "No documents to migrate" | ✅ Significa que ya todo está migrado |
| Error de conexión | Verifica que MongoDB está activo |
| Script no corre | Instala: `pip install pymongo python-dotenv` |

---

## 📚 Documentación Completa

Para más detalles, ver:
- `MIGRATION_GUIDE.md` - Guía detallada de migración
- `CAMBIOS_REALIZADOS.md` - Cambios implementados
- `RESUMEN_CAMBIOS.md` - Resumen ejecutivo

---

## 🔐 Seguridad

**⚠️ Importantes:**
1. Los scripts **no hacen cambios** en modo preview (default)
2. Siempre usar `--execute` para aplicar cambios
3. Se pide confirmación antes de hacer cambios
4. Hacer **backup antes** de ejecutar (recomendado):
   ```bash
   mongodump --uri="mongodb://..." --out=backup_$(date)
   ```

---

## 💡 Tips

- Ejecutar en modo preview primero: `python migrate_data.py`
- Ver ejemplos: `python migrate_data.py --show-samples`
- Validar después: `python test_migration.py`
- Migrar solo ingestas: `python migrate_data.py --intakes-only --execute`

**¡Listo para usar! 🚀**
