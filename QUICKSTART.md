# ⚡ Quick Start - Registro de Ingestas

## 1️⃣ Configuración Inicial

### Variables de Entorno (.env)
```env
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Inicializar BD
```bash
python setup_mongodb.py
```

## 2️⃣ Archivos Modificados/Creados

### ✅ Modificados
- **[src/bionexo/domain/entity/intake.py](src/bionexo/domain/entity/intake.py)** - Modelo mejorado con campos: `user_id`, `ingredients`, `image_data`, `voice_description`
- **[src/bionexo/infrastructure/utils/db.py](src/bionexo/infrastructure/utils/db.py)** - Funciones: `save_intake()`, compresión automática de imágenes
- **[src/bionexo/application/webapp/app.py](src/bionexo/application/webapp/app.py)** - Interfaz Streamlit con 2 tabs (Manual + Con Imagen)

### 🆕 Creados
- **[src/bionexo/infrastructure/utils/image_handler.py](src/bionexo/infrastructure/utils/image_handler.py)** - Utilidades de compresión de imágenes
- **[src/bionexo/domain/entity/food.py](src/bionexo/domain/entity/food.py)** - Modelo para recetas/alimentos
- **[src/bionexo/repository/foods.py](src/bionexo/repository/foods.py)** - CRUD para colección `foods`
- **[setup_mongodb.py](setup_mongodb.py)** - Script de inicialización
- **[examples_intakes.py](examples_intakes.py)** - Ejemplos de uso

## 3️⃣ Características Implementadas

### 📱 Interfaz Streamlit
```
Registrar Ingesta
├── 📝 Tab Manual
│   ├── Nombre del alimento
│   ├── Cantidad (g)
│   ├── Calorías
│   ├── Cómo te sientes
│   ├── Ingredientes (opcional)
│   └── Descripción de voz (opcional)
│
└── 🖼️ Tab Con Imagen
    ├── Subir imagen (JPG/PNG/WebP)
    ├── Preview en tiempo real
    └── Campos + Guardado automático
```

### 💾 Almacenamiento MongoDB
- **TimeSeries Collection**: Optimizada para consultas temporales
- **BSON Binary**: Imágenes comprimidas (30-40% menos tamaño)
- **Índices automáticos**: Búsquedas rápidas por usuario y fecha

### 📊 Historial
- Tabla de últimas ingestas
- Estadísticas: total kcal, promedio, cantidad
- Visualización: ingredientes, sentimientos, imágenes

## 4️⃣ Uso en Código

### Guardar ingesta manual
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
    ingredients=["pollo", "arroz"],
    feeling="Bien"
)

save_intake(db, intake)
```

### Guardar con imagen
```python
from PIL import Image
import io

image = Image.open("comida.jpg")
img_bytes = io.BytesIO()
image.save(img_bytes, format="PNG")

intake = Intake(
    user_id="user@example.com",
    food_name="Desayuno",
    quantity=250,
    kcal=350,
    timestamp=datetime.datetime.now(),
    image_data=img_bytes.getvalue(),
    ingredients=["huevos", "pan"],
    feeling="Saciado"
)

save_intake(db, intake)  # Compresión automática
```

### Obtener ingestas
```python
from bionexo.infrastructure.utils.db import get_intakes_from_db

intakes = get_intakes_from_db(db, "user@example.com", limit=50)

for intake in intakes:
    print(f"{intake['timestamp']}: {intake['food_name']} - {intake['kcal']} kcal")
```

## 5️⃣ Estructura MongoDB

### Colección `intakes` (TimeSeries)
```
Índices:
✓ timestamp (automático)
✓ user_id (metafield)
✓ (user_id, timestamp) compuesto

Documentos:
{
  user_id: string
  timestamp: datetime
  food_name: string
  quantity: number
  kcal: number
  ingredients: [string]
  image_data: Binary (comprimida)
  voice_description: string (opcional)
  feeling: string
}
```

### Colección `foods` (Recetas)
```
Índices:
✓ name (único)

Documentos:
{
  name: string
  description: string
  ingredients: [string]
  kcal_per_100g: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  vitamins: object
  minerals: object
  tags: [string]
  allergens: [string]
  created_at: datetime
}
```

## 6️⃣ Próximos Pasos

- [ ] Integrar análisis de imágenes con Gemini API
- [ ] Dashboard de análisis nutricional
- [ ] Exportar reportes (CSV/PDF)
- [ ] Sincronización con wearables
- [ ] Recomendaciones basadas en IA

## 7️⃣ Troubleshooting

**Error: "DuplicateKeyError" en TimeSeries**
```bash
db.intakes.drop()
python setup_mongodb.py
```

**Las imágenes se guardan muy grandes**
- La compresión es automática
- Verifica Pillow: `pip install pillow --upgrade`

**Consultas lentas**
```bash
db.intakes.getIndexes()  # Verificar índices
```

---

**📚 Más info en:** [INTAKES_SETUP.md](INTAKES_SETUP.md)
