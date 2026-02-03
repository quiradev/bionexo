# Script de Migración de Datos - Guía de Uso

## 📋 Descripción

El script `migrate_data.py` actualiza los documentos existentes en MongoDB para usar los nuevos campos introducidos en la actualización de Bionexo.

**Cambios que realiza:**

### Ingestas (intakes)
- ✅ Convierte `feeling` (string categórico) → `feeling_scale` (1-10)
- ✅ Agrega `meal_type` si no existe (default: "Comida")
- ✅ Agrega `quantity_type` si no existe (basado en si hay cantidad)

### Reportes de Bienestar (wellness_logs)
- ✅ Convierte `digestive_issues` (string) → `digestive_comfort_scale` (1-10)
- ✅ Convierte `appetite` (string) → `appetite_scale` (1-10)

---

## 🚀 Uso

### Paso 1: Preview (Recomendado)

**Ver qué cambios se realizarían SIN hacer cambios reales:**

```bash
cd d:\workspace\bionexo
python migrate_data.py
```

**Salida esperada:**
```
============================================================
  🚀 SCRIPT DE MIGRACIÓN DE DATOS - BIONEXO
============================================================

⚠️  MODO PREVIEW (sin realizar cambios)
   Use --execute para aplicar los cambios realmente

📊 MIGRACIÓN DE INGESTAS
──────────────────────────────────────────────────
Documentos a actualizar: 5
  • Pollo con Arroz: 'Saciado' → 9/10
  • Ensalada Verde: 'Bien' → 7/10
  • Pasta Carbonara: 'Hinchado' → 9/10
  ...

📊 MIGRACIÓN DE REPORTES DE BIENESTAR
──────────────────────────────────────────────────
Documentos a actualizar: 3
  • Digestión: 'Hinchazón, Acidez' → 4/10
  • Apetito: 'Bajo' → 2/10
  ...

==============================================================
📋 RESUMEN DE MIGRACIÓN
==============================================================

📊 Ingestas:
  • Total procesados: 5
  • Actualizados: 5
  • Errores: 0

📊 Reportes de Bienestar:
  • Total procesados: 3
  • Actualizados: 3
  • Errores: 0

💡 PRÓXIMO PASO:
   Ejecuta con --execute para aplicar los cambios:
   python migrate_data.py --execute
```

---

### Paso 2: Realizar Migración

**Una vez verificado que los cambios son correctos, ejecutar:**

```bash
python migrate_data.py --execute
```

**Nota:** Se pedirá confirmación presionando ENTER antes de ejecutar.

---

## 📝 Opciones del Script

| Opción | Descripción |
|--------|-------------|
| `--execute` | Ejecuta la migración realmente (sin esto solo muestra preview) |
| `--intakes-only` | Migra solo la colección de ingestas |
| `--wellness-only` | Migra solo la colección de reportes de bienestar |
| `--show-samples` | Muestra ejemplos de documentos antes y después |

### Ejemplos:

```bash
# Ver preview solo de ingestas
python migrate_data.py --intakes-only

# Ejecutar migración solo de ingestas
python migrate_data.py --intakes-only --execute

# Ver ejemplos de documentos
python migrate_data.py --show-samples

# Ejecutar migración completa
python migrate_data.py --execute
```

---

## 🔄 Mapeos de Conversión

### Conversión de `feeling` → `feeling_scale`

| Valor Original | Resultado |
|---|---|
| "Con hambre" | 1 |
| "Bien" | 7 |
| "Neutral" / "Neutro" | 5 |
| "Saciado" | 9 |
| "Hinchado" | 9 |
| Otros valores | 5 (neutral) |

### Conversión de `appetite` → `appetite_scale`

| Valor Original | Resultado |
|---|---|
| "Bajo" | 2 |
| "Normal" | 5 |
| "Alto" | 9 |
| "N/A" | None (no se actualiza) |

### Conversión de `digestive_issues` → `digestive_comfort_scale`

El script analiza la cadena y calcula un valor ponderado:

| Problema | Puntos |
|---|---|
| Hinchazón | -3 |
| Estreñimiento | -3 |
| Diarrea | -3 |
| Reflujo | -3 |
| Acidez | -4 |
| "Ninguno" | 10 |

**Ejemplo:**
- "Hinchazón, Acidez" → 10 - (3+4)/2 = 10 - 3.5 ≈ 6/10
- "Ninguno" → 10/10

---

## ⚠️ Precauciones Importantes

### Antes de ejecutar:

1. **HACER BACKUP** de la base de datos MongoDB:
   ```bash
   # En Windows (si tienes MongoDB instalado)
   mongodump --uri="mongodb://localhost:27017/bionexo" --out=backup_$(date +%Y%m%d)
   ```

2. **Verificar conexión** a la base de datos:
   ```bash
   # Asegúrate de que MONGODB_URI esté configurada en .env
   cat .env | findstr MONGODB_URI
   ```

3. **Ejecutar en modo preview** primero:
   ```bash
   python migrate_data.py
   ```

4. **Revisar los cambios propuestos** antes de ejecutar con `--execute`

---

## ✅ Verificación Post-Migración

Después de ejecutar la migración, verifica que los cambios se aplicaron correctamente:

```bash
# Ver ejemplos de documentos actualizados
python migrate_data.py --show-samples
```

**Salida esperada:**
```
📄 EJEMPLOS DE DOCUMENTOS
──────────────────────────────────────────────────

✏️ Ejemplo de Ingesta:
  • food_name: Pollo con Arroz
  • feeling (antiguo): Saciado
  • feeling_scale (nuevo): 9
  • meal_type: Comida
  • quantity_type: gramos

✏️ Ejemplo de Reporte de Bienestar:
  • digestive_issues (antiguo): Hinchazón
  • digestive_comfort_scale (nuevo): 7
  • appetite (antiguo): Normal
  • appetite_scale (nuevo): 5
```

---

## 🔍 Campos Nuevos Agregados Automáticamente

### Para Ingestas sin `meal_type`:
```python
meal_type = "Comida"  # Por defecto
```

### Para Ingestas sin `quantity_type`:
```python
# Si quantity (gramos) existe:
quantity_type = "gramos"

# Si no existe:
quantity_type = "descriptiva"
```

---

## 📚 Información Técnica

### Requisitos:
- Python 3.7+
- MongoDB conectado y disponible
- Variable de entorno `MONGODB_URI` configurada

### Lógica del Script:

1. Se conecta a MongoDB usando `MONGODB_URI`
2. Para cada colección, busca documentos que cumplan:
   - Tengan campos antiguos (`feeling`, `digestive_issues`, `appetite`)
   - Y NO tengan aún los campos nuevos (`feeling_scale`, `digestive_comfort_scale`, `appetite_scale`)
3. En modo preview, solo muestra qué cambios haría
4. En modo execute, aplica los cambios usando `update_one()`
5. Muestra resumen de documentos procesados

---

## 🐛 Solución de Problemas

### Error: "MONGODB_URI not found"
**Solución:** Verifica que el archivo `.env` existe y contiene:
```
MONGODB_URI=mongodb+srv://usuario:contraseña@host/database
```

### Error: "No documents to migrate"
**Solución:** Significa que todos los documentos ya tienen los campos nuevos. ¡Nada que hacer!

### Error de conexión a MongoDB
**Solución:** 
- Verifica que MongoDB está funcionando
- Verifica la URI de conexión
- Prueba con MongoDB Compass

---

## 📊 Ejemplo Completo de Flujo

```bash
# 1. Ver preview
$ python migrate_data.py
[... muestra qué cambiaría ...]

# 2. Ver ejemplos
$ python migrate_data.py --show-samples
[... muestra documentos de ejemplo ...]

# 3. Hacer backup (recomendado)
$ mongodump --uri="mongodb://..." --out=backup_20260203

# 4. Ejecutar migración
$ python migrate_data.py --execute
[Presiona ENTER para confirmar]
[... aplica cambios ...]

# 5. Verificar resultados
$ python migrate_data.py --show-samples
[... muestra documentos actualizados ...]
```

---

## ✅ Checklist

- [ ] Archivo `.env` configurado con `MONGODB_URI`
- [ ] MongoDB está corriendo y accesible
- [ ] Ejecuté en modo preview: `python migrate_data.py`
- [ ] Revisé los cambios propuestos
- [ ] Hice backup de la base de datos (recomendado)
- [ ] Ejecuté: `python migrate_data.py --execute`
- [ ] Verifiqué con: `python migrate_data.py --show-samples`

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los errores mostrados por el script
2. Verifica la conexión a MongoDB
3. Asegúrate que los datos antiguos están presentes
4. Revisa el archivo `.env`

**Nota:** El script es seguro - en modo preview no hace cambios. Puedes ejecutarlo múltiples veces para verificar.

