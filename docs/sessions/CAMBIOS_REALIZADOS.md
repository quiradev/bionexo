# Cambios Realizados - Mejora de Ingestas y Síntomas

## Resumen
Se ha actualizado la aplicación Bionexo para mejorar significativamente la experiencia de registro de ingestas y síntomas, convirtiendo campos categóricos en escalas numéricas y permitiendo mayor flexibilidad en cómo los usuarios ingresan información.

---

## 1. Actualización de Entidades (Domain Models)

### 1.1 Ingesta (`src/bionexo/domain/entity/intake.py`)

**Cambios realizados:**
- ✅ Agregado campo `meal_type`: Tipo de comida (Desayuno, Almuerzo, Comida, Cena, Merienda, Picar entre horas)
- ✅ Agregado campo `feeling_scale` (1-10): Escala numérica de sensación después de comer
  - 1 = Con hambre
  - 10 = Muy hinchado/Saciado
- ✅ Agregado campo `quantity_type`: Indica si la cantidad es en "gramos", "descriptiva" o "ambas"
- ✅ Agregado campo `quantity_description`: Descripción conversacional de la cantidad (ej: "medio plato grande", "un vaso", "30% del plato")
- ✅ Campos `quantity` y `kcal` ahora son opcionales
- ❌ Removidos campos: `feeling` (string categórico) y `bathroom`

**Nuevos campos:**
```python
meal_type: str  # desayuno, almuerzo, comida, cena, merienda, picar
quantity_type: str  # gramos, descriptiva, ambas
quantity_description: Optional[str]  # conversacional
feeling_scale: Optional[int]  # 1-10
```

### 1.2 Reporte de Bienestar (`src/bionexo/domain/entity/wellness_logs.py`)

**Cambios realizados:**
- ✅ Reemplazado `digestive_issues` (string categórico) con `digestive_comfort_scale` (1-10)
  - 1 = Muy hinchado
  - 10 = Muy cómodo
- ✅ Reemplazado `appetite` (string categórico) con `appetite_scale` (1-10)
  - 1 = Sin apetito
  - 10 = Muy hambriento

---

## 2. Funciones Auxiliares (`src/bionexo/infrastructure/utils/db.py`)

**Nuevas funciones:**
- ✅ `get_unique_meal_names_from_db(db, user_id)`: Obtiene lista de nombres únicos de comidas guardadas previamente
  - Permite crear un select_box para reutilizar comidas anteriores
  - Retorna lista ordenada alfabéticamente

---

## 3. Interfaz de Usuario (Streamlit) - `src/bionexo/application/webapp/app.py`

### 3.1 Sección "Registrar Ingesta"

**Mejoras principales:**

1. **Información Temporal**
   - ✅ Selector de hora (time_input) para indicar cuándo se consumió
   - ✅ Selector de tipo de comida (Desayuno, Almuerzo, Comida, Cena, Merienda, Picar entre horas)

2. **Seleccionar o Crear Comida**
   - ✅ Checkbox para usar comida guardada previamente
   - ✅ Si se selecciona, se muestra select_box con comidas anteriores (`accept_new_options=False`)
   - ✅ Si se crea nueva, campo de texto para ingresar nombre
   - ✅ Los ingredientes se pueden agregar/actualizar

3. **Cantidad y Calorías**
   - ✅ Radio button para elegir método de entrada:
     - **Gramos**: campo numérico (g)
     - **Descripción conversacional**: texto libre (ej: medio plato grande, un vaso)
     - **Ambas**: permite ingreso de ambas
   - ✅ Campo de calorías (kcal) ahora es **opcional**
     - Se rellenará posteriormente según ingredientes
     - Por defecto está en 0

4. **Sensación Después de Comer**
   - ✅ Reemplazado selectbox categórico con slider 1-10
   - ✅ Escala clara: 1 = Con hambre, 10 = Muy hinchado/Saciado
   - ✅ Mide sensación después de 10-20 minutos

5. **Ingredientes**
   - ✅ Se pueden agregar/actualizar ingredientes
   - ✅ Entrada por texto separada por comas

6. **Notas Adicionales**
   - ✅ Campo para descripción adicional (ya existía, mejorado)

**Cambio en timestamp:**
- ✅ El timestamp ahora combina la fecha actual con la hora ingresada por el usuario
- ✅ Se almacena como datetime completo internamente

### 3.2 Sección "Registrar Bienestar"

**Cambios en Síntomas Gastrointestinales:**

1. **Comodidad Digestiva**
   - ❌ Removido: multiselect de problemas digestivos (Hinchazón, Estreñimiento, Diarrea, etc.)
   - ✅ Agregado: slider 1-10 (`digestive_comfort_scale`)
   - 1 = Muy hinchado
   - 10 = Muy cómodo

2. **Apetito**
   - ❌ Removido: selectbox categórico (Bajo, Normal, Alto)
   - ✅ Agregado: slider 1-10 (`appetite_scale`)
   - 1 = Sin apetito
   - 10 = Muy hambriento

### 3.3 Sección "Historial de Ingestas"

**Mejoras en visualización:**
- ✅ Columna "Tipo": Muestra tipo de comida
- ✅ Columna "Cantidad": Muestra gramos O descripción (según qué se ingresó)
- ✅ Columna "Calorías": Muestra valor o "Pendiente" si está vacío
- ✅ Columna "Sensación": Muestra escala 1-10 O "-" si no está disponible
- ✅ Estadísticas actualizadas para manejar calorías opcionales

### 3.4 Sección "Historial de Síntomas"

**Actualizaciones:**
- ✅ Campo "Apetito" ahora muestra valor 1-10 (`appetite_scale`)
- ✅ Campo "Comodidad digestiva" reemplaza "Problemas digestivos" con valor 1-10 (`digestive_comfort_scale`)

---

## 4. Datos de Ejemplo

### Ingesta con nuevos campos:
```python
Intake(
    user_id="usuario@email.com",
    food_name="Pollo con Arroz",
    quantity=200,  # opcional, en gramos
    kcal=None,  # opcional, se rellenará después
    timestamp=datetime(2026, 2, 3, 12, 30),
    meal_type="Comida",
    quantity_type="ambas",
    quantity_description="Medio plato grande con un vaso de agua",
    feeling_scale=7,  # 1-10
    ingredients=["pollo", "arroz", "sal", "aceite"]
)
```

### Reporte de Bienestar con nuevos campos:
```python
WellnessReport(
    ...
    digestive_comfort_scale=8,  # 1-10, antes era string
    appetite_scale=9,  # 1-10, antes era string
    ...
)
```

---

## 5. Compatibilidad con Base de Datos

**Nota importante:** 
- Los cambios son principalmente a nivel de campos en las entidades Pydantic
- MongoDB almacena los documentos tal cual se envíen
- Los nuevos campos serán creados automáticamente en los documentos
- Los registros anteriores que usen los campos antiguos (`feeling`, `digestive_issues`, `appetite`) pueden coexistir
- Se recomienda migrar datos antiguos si es necesario

---

## 6. Validaciones Realizadas

✅ Sin errores de sintaxis en:
- `src/bionexo/application/webapp/app.py`
- `src/bionexo/domain/entity/intake.py`
- `src/bionexo/domain/entity/wellness_logs.py`
- `src/bionexo/infrastructure/utils/db.py`

---

## 7. Flujos de Uso

### Registrar Ingesta Estándar:
1. Seleccionar hora de la comida
2. Elegir tipo de comida (Desayuno/Almuerzo/etc.)
3. Elegir si reutilizar comida anterior o crear nueva
4. Seleccionar método para indicar cantidad (Gramos/Descripción/Ambas)
5. Ingreso de cantidad según método seleccionado
6. Opcionalmente ingresar calorías
7. Indicar sensación después (escala 1-10)
8. Agregar ingredientes (opcional)
9. Guardar

### Registrar Bienestar:
1. Indicar momento del día y horas
2. Síntomas físicos (igual que antes)
3. Estado emocional (igual que antes)
4. Energía y descanso (igual que antes)
5. **Nuevos campos gastrointestinales:**
   - Slider: Comodidad digestiva (1-10)
   - Slider: Apetito (1-10)
   - Checkbox: Náusea
6. Otros síntomas (igual que antes)
7. Notas adicionales (igual que antes)

---

## 8. Próximos Pasos Sugeridos

1. **Conversión de cantidad descriptiva a gramos**: Implementar función que convierta descripciones conversacionales a estimaciones de gramos basadas en el alimento
2. **Cálculo automático de calorías**: Al seleccionar ingredientes, calcular calorías automáticamente
3. **Migración de datos**: Script para migrar registros antiguos que usen campos deprecated
4. **Reportes mejorados**: Gráficos y análisis con las nuevas escalas numéricas
5. **Sugerencias inteligentes**: Sistema que aprenda de patrones entre comidas, sensaciones y síntomas

---

## 9. Archivos Modificados

- ✅ `src/bionexo/domain/entity/intake.py`
- ✅ `src/bionexo/domain/entity/wellness_logs.py`
- ✅ `src/bionexo/infrastructure/utils/db.py`
- ✅ `src/bionexo/application/webapp/app.py`

---

**Fecha de actualización:** 3 de febrero de 2026
**Estado:** ✅ Listo para probar
