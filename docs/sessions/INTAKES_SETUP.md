# Guía de Configuración - Registro de Ingestas con MongoDB

## Descripción

Este módulo implementa la funcionalidad completa de registrar ingestas de alimentos con soporte para:
- ✅ Registro manual de comidas
- ✅ Subida y almacenamiento de imágenes (comprimidas en BSON Binary)
- ✅ Almacenamiento de ingredientes y nutrientes
- ✅ Notas de voz transcrita
- ✅ Información sobre cómo se siente el usuario después de comer
- ✅ Colección timeseries optimizada para consultas temporales

## Estructura de Datos

### Colección `intakes` (TimeSeries)
```json
{
  "_id": ObjectId,
  "user_id": "usuario@email.com",
  "timestamp": 2024-01-15T14:30:00Z,
  "food_name": "Pollo con arroz",
  "quantity": 150,
  "kcal": 320,
  "ingredients": ["pollo", "arroz", "sal", "aceite"],
  "image_data": Binary,
  "image_size_bytes": 45000,
  "voice_description": "Comida sabrosa, bien balanceada",
  "feeling": "Bien"
}
```

**Índices:**
- Timeseries en `timestamp` (campo temporal)
- Metafield en `user_id`
- Índice compuesto: `(user_id, timestamp)`

### Colección `foods` (Recetas/Alimentos)
```json
{
  "_id": ObjectId,
  "name": "Pollo con arroz",
  "description": "Plato tradicional",
  "ingredients": ["pollo", "arroz", "sal"],
  "kcal_per_100g": 150,
  "protein_g": 25,
  "carbs_g": 30,
  "fat_g": 3,
  "fiber_g": 0,
  "vitamins": {"B12": 2.4, "D": 0},
  "minerals": {"calcium": 50, "iron": 2},
  "created_at": 2024-01-15T10:00:00Z,
  "updated_at": 2024-01-15T10:00:00Z,
  "tags": ["tradicional", "alto en proteína"],
  "allergens": [],
  "user_created": false
}
```

**Índices:**
- Único en `name`

## Instalación

### 1. Configurar variables de entorno
Crear archivo `.env`:
```env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### 2. Inicializar la base de datos
```bash
python setup_mongodb.py
```

Este script:
- Crea índices en `users`
- Crea colección timeseries en `intakes`
- Crea índices en `foods`

### 3. Dependencias necesarias
Las siguientes están en `requirements.txt`:
- `pymongo~=4.15.5` - Driver de MongoDB
- `pillow~=12.1.0` - Manejo de imágenes
- `streamlit~=1.52.2` - Interfaz web

## Uso en la Aplicación

### Registro Manual
```python
from bionexo.domain.entity.intake import Intake
from bionexo.infrastructure.utils.db import save_intake
import datetime

intake = Intake(
    user_id="user@example.com",
    food_name="Almuerzo",
    quantity=200,
    kcal=450,
    timestamp=datetime.datetime.now(),
    ingredients=["pollo", "arroz", "ensalada"],
    feeling="Bien"
)

save_intake(db, intake)
```

### Registro con Imagen
```python
from PIL import Image
from bionexo.domain.entity.intake import Intake
from bionexo.infrastructure.utils.db import save_intake
import io

# Cargar imagen
image = Image.open("comida.jpg")

# Convertir a bytes
img_bytes = io.BytesIO()
image.save(img_bytes, format="PNG")
img_bytes.seek(0)

intake = Intake(
    user_id="user@example.com",
    food_name="Desayuno",
    quantity=250,
    kcal=350,
    timestamp=datetime.datetime.now(),
    ingredients=["huevos", "pan", "café"],
    image_data=img_bytes.getvalue(),
    feeling="Saciado"
)

save_intake(db, intake)
```

### Consultar Ingestas
```python
from bionexo.infrastructure.utils.db import get_intakes_from_db

# Obtener últimas 50 ingestas del usuario
intakes = get_intakes_from_db(db, "user@example.com", limit=50)

for intake in intakes:
    print(f"{intake['timestamp']}: {intake['food_name']} - {intake['kcal']} kcal")
```

### Gestionar Alimentos/Recetas
```python
from bionexo.domain.entity.food import Food
from bionexo.repository.foods import save_food, search_foods
from datetime import datetime

# Crear receta
food = Food(
    name="Ensalada Griega",
    description="Ensalada mediterránea",
    ingredients=["tomate", "pepino", "queso feta", "aceitunas"],
    kcal_per_100g=50,
    protein_g=3,
    carbs_g=5,
    fat_g=2,
    tags=["vegetariano", "saludable"],
    allergens=["lactosa"]
)

save_food(db, food)

# Buscar alimentos
results = search_foods(db, "ensalada")

# Filtrar por calorías
low_cal_foods = get_foods_by_calories_range(db, 0, 100)
```

## Optimizaciones en MongoDB

### ¿Por qué TimeSeries?
- ✅ Compresión automática de datos con el tiempo
- ✅ Índices optimizados para consultas temporales
- ✅ Granularidad configurable (minutes)
- ✅ Ideal para datos de seguimiento nutricional

### Almacenamiento de Imágenes
- Las imágenes se comprimen automáticamente con PIL
- Formato: BSON Binary (más eficiente que Base64)
- Reducción: ~30-40% del tamaño original
- Máximo: 16MB por documento (limite de MongoDB)

### Índices
```javascript
// Timeseries (automático)
db.intakes.createIndex({ "timestamp": 1 })

// Búsqueda rápida por usuario
db.intakes.createIndex({ "user_id": 1, "timestamp": -1 })

// Búsqueda de alimentos
db.foods.createIndex({ "name": 1 }, { unique: true })
```

## Flujo de la Aplicación Streamlit

1. **Login/Registro** → Autenticación de usuario
2. **Registrar Ingesta**
   - Tab Manual: Rellenar formulario manualmente
   - Tab Con Imagen: Subir imagen + datos nutricionales
3. **Historial**
   - Tabla de últimas ingestas
   - Estadísticas agregadas (total kcal, promedio, etc.)
4. **Análisis** (próximamente)
   - Gráficos de tendencias
   - Recomendaciones nutricionales

## Troubleshooting

### Error: "La colección 'intakes' ya existe"
MongoDB no permite cambiar una colección regular a timeseries. Elimina la colección:
```bash
db.intakes.drop()
python setup_mongodb.py
```

### Las imágenes no se guardan
Verifica que:
- El campo `image_data` no sea None
- El tamaño total del documento no exceda 16MB
- Pillow esté correctamente instalado

### Consultas lentas
Verifica los índices:
```bash
db.intakes.getIndexes()
db.foods.getIndexes()
```

## Próximas Mejoras

- [ ] Integración con API de análisis de imágenes (Gemini)
- [ ] Exportar datos a CSV/PDF
- [ ] Sincronización con wearables
- [ ] Análisis de patrones con IA
- [ ] Recomendaciones personalizadas
