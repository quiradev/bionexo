# 🛠️ Instrucciones de Instalación y Configuración

## Paso 1: Clonar/Actualizar Repositorio
```bash
cd d:\workspace\bionexo
git pull  # Si es necesario
```

## Paso 2: Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# .env
MONGODB_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/?retryWrites=true&w=majority

# Opcional (para API de análisis)
GEMINI_API_KEY=tu_clave_aqui
```

## Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

Verifica que estén instaladas:
```bash
pip list | grep -E "pymongo|pillow|streamlit|pydantic"
```

## Paso 4: Inicializar Base de Datos MongoDB
```bash
python setup_mongodb.py
```

**Output esperado:**
```
🔧 Inicializando base de datos Bionexo...

📝 Creando índices...
✅ Índice en 'users.email' creado
⏱️ Creando colección timeseries para 'intakes'...
✅ Colección timeseries 'intakes' creada exitosamente
✅ Índice compuesto en 'intakes' creado
🍽️ Preparando colección 'foods'...
✅ Índice en 'foods.name' creado

✅ Base de datos configurada exitosamente!

📋 Colecciones disponibles:
  - users: Información de usuarios
  - intakes: Registro de comidas (timeseries)
  - foods: Recetas y alimentos
```

## Paso 5: (Opcional) Cargar Datos de Ejemplo
```bash
python examples_intakes.py
```

Este script:
- ✅ Crea base de datos de 6 alimentos comunes
- ✅ Simula ingesta de una semana
- ✅ Demuestra búsquedas y filtros

## Paso 6: Ejecutar la Aplicación Streamlit
```bash
streamlit run src/bionexo/application/webapp/main.py
```

La aplicación se abrirá en: `http://localhost:8501`

---

## 📋 Verificación

### Verificar MongoDB
```bash
# Verificar conexión
mongo "mongodb+srv://usuario:contraseña@cluster.mongodb.net/?retryWrites=true&w=majority"

# En MongoDB Shell:
use bionexo
db.intakes.getIndexes()
db.foods.getIndexes()
db.users.getIndexes()
```

### Verificar Pydantic Models
```python
from bionexo.domain.entity.intake import Intake
from bionexo.domain.entity.food import Food
print("✅ Modelos cargados correctamente")
```

### Verificar Conexión a DB
```python
from bionexo.infrastructure.utils.db import get_db
db = get_db()
print("✅ Base de datos conectada")
print(db.list_collection_names())
```

---

## 🎯 Flujo de la Aplicación

### 1. **Login/Registro**
```
┌─────────────────────────────────┐
│   Bionexo - Login               │
├─────────────────────────────────┤
│                                 │
│  Email: [ _________ ]           │
│  Contraseña: [ *** ]            │
│                                 │
│  [ Iniciar Sesión ]             │
│                                 │
│  O Registrarse → (ver Tab 2)    │
└─────────────────────────────────┘
```

### 2. **Registro (primera vez)**
```
┌─────────────────────────────────┐
│ 📋 Información Personal         │
├─────────────────────────────────┤
│ Nombre: [________________]       │
│ Email: [________________]        │
│ Contraseña: [________]          │
│                                 │
│ 👤 Datos Demográficos           │
│ Edad: [Adulto ▼]                │
│ Sexo: [Macho ▼]                 │
│ Actividad: [Activo ▼]           │
│                                 │
│ 📏 Medidas Físicas              │
│ Altura: [170] cm                │
│ Peso: [70.0] kg                 │
│                                 │
│ ⚕️ Salud y Alergias            │
│ Condiciones: [_____________]    │
│ Alergias: [_____________]       │
│                                 │
│ [ 💾 Guardar Perfil ]           │
└─────────────────────────────────┘
```

### 3. **Registrar Ingesta - Tab Manual**
```
┌─────────────────────────────────────────┐
│ Registrar Ingesta de Alimentos          │
├─ Manual ─────┬─ Con Imagen ────────────┤
│              │                         │
│ 📝 Registro Manual                      │
│                                         │
│ Nombre del Alimento: [________________] │
│ Cantidad (g): [150]                    │
│                                         │
│ Calorías (kcal): [320]                 │
│ ¿Cómo te sientes?: [Bien ▼]            │
│                                         │
│ Ingredientes:                           │
│ [__________________________________]   │
│ Pollo, arroz, sal, aceite              │
│                                         │
│ Descripción adicional:                  │
│ [__________________________________]   │
│ Comida sabrosa, bien balanceada        │
│                                         │
│ [ 💾 Guardar Ingesta ]                 │
└─────────────────────────────────────────┘
```

### 4. **Registrar Ingesta - Tab Con Imagen**
```
┌──────────────────────────────────────┐
│ Registrar Ingesta de Alimentos       │
├─ Manual ─────┬─ Con Imagen ─────────┤
│              │                      │
│ [Subir Imagen]                      │
│                                     │
│ ┌──────────────────────────┐        │
│ │                          │        │
│ │   [🖼️ Imagen Preview]    │        │
│ │                          │        │
│ └──────────────────────────┘        │
│                                     │
│ Nombre: [________________]          │
│ Cantidad: [150] g                  │
│ Calorías: [320] kcal               │
│ Sentimiento: [Bien ▼]              │
│ Ingredientes: [____________]       │
│                                     │
│ [ 💾 Guardar con Imagen ]          │
└──────────────────────────────────────┘
```

### 5. **Historial**
```
┌─────────────────────────────────────────────────┐
│ Historial de Ingestas                           │
├─────────────────────────────────────────────────┤
│                                                 │
│ Fecha            │ Alimento  │ Kcal │ Imagen   │
│ 2024-01-15 14:30 │ Pollo     │ 320  │ ✅       │
│ 2024-01-15 12:00 │ Ensalada  │ 150  │ ❌       │
│ 2024-01-15 08:00 │ Desayuno  │ 350  │ ✅       │
│                                                 │
│ 📊 Estadísticas                                │
│ Total de Ingestas: 3                           │
│ Calorías Totales: 820 kcal                     │
│ Promedio por Ingesta: 273.3 kcal              │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Estructura de Directorios Creada

```
d:\workspace\bionexo\
├── setup_mongodb.py                     ← Script setup
├── examples_intakes.py                  ← Ejemplos
├── QUICKSTART.md                        ← Guía rápida
├── INTAKES_SETUP.md                     ← Guía completa
├── IMPLEMENTATION_SUMMARY.md            ← Resumen
├── INSTALLATION_GUIDE.md                ← Este archivo
│
├── src/bionexo/
│   ├── domain/entity/
│   │   ├── intake.py                    ✅ MODIFICADO
│   │   └── food.py                      ✅ NUEVO
│   │
│   ├── infrastructure/utils/
│   │   ├── db.py                        ✅ MODIFICADO
│   │   └── image_handler.py             ✅ NUEVO
│   │
│   ├── repository/
│   │   └── foods.py                     ✅ NUEVO
│   │
│   └── application/webapp/
│       └── app.py                       ✅ MODIFICADO
│
└── requirements.txt                     (sin cambios)
```

---

## 🧪 Pruebas

### Test 1: Guardar ingesta manual
```python
from datetime import datetime
from bionexo.domain.entity.intake import Intake
from bionexo.infrastructure.utils.db import get_db, save_intake

db = get_db()

intake = Intake(
    user_id="test@example.com",
    food_name="Pizza",
    quantity=200,
    kcal=500,
    timestamp=datetime.now(),
    ingredients=["harina", "queso", "tomate"],
    feeling="Saciado"
)

result = save_intake(db, intake)
print(f"Guardado: {result}")
```

### Test 2: Recuperar ingestas
```python
from bionexo.infrastructure.utils.db import get_db, get_intakes_from_db

db = get_db()
intakes = get_intakes_from_db(db, "test@example.com", limit=10)
print(f"Ingestas recuperadas: {len(intakes)}")
for intake in intakes:
    print(f"  - {intake['food_name']}: {intake['kcal']} kcal")
```

### Test 3: Crear alimento
```python
from datetime import datetime
from bionexo.domain.entity.food import Food
from bionexo.repository.foods import save_food
from bionexo.infrastructure.utils.db import get_db

db = get_db()

food = Food(
    name="Arroz Blanco",
    description="Arroz cocido simple",
    ingredients=["arroz", "agua", "sal"],
    kcal_per_100g=130,
    protein_g=2.7,
    carbs_g=28,
    fat_g=0.3,
    tags=["carbohidrato", "base"]
)

result = save_food(db, food)
print(f"Alimento guardado: {result}")
```

---

## 🐛 Troubleshooting

### Error: "MONGODB_URI not found"
```bash
# Verificar .env existe
cat .env

# Debe contener:
MONGODB_URI=mongodb+srv://...

# Si no existe, crearlo:
echo 'MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority' > .env
```

### Error: "Connection refused"
```bash
# Verificar MongoDB está en línea
# 1. Ir a MongoDB Atlas
# 2. Verificar cluster está activo
# 3. Verificar IP está whitelisted
# 4. Verificar credenciales en .env
```

### Error: "ModuleNotFoundError: No module named 'bionexo'"
```bash
# Agregar raíz al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:d:\workspace\bionexo\src"

# O en PowerShell:
$env:PYTHONPATH += ";d:\workspace\bionexo\src"
```

### Error: "Pillow no está instalado"
```bash
pip install pillow --upgrade
```

### Error: "La colección 'intakes' ya existe"
```bash
# En MongoDB Shell:
db.intakes.drop()

# Luego:
python setup_mongodb.py
```

---

## ✅ Checklist Final

- [ ] `.env` configurado con MONGODB_URI
- [ ] `pip install -r requirements.txt` ejecutado
- [ ] `python setup_mongodb.py` ejecutado sin errores
- [ ] MongoDB collections creadas (verificar en Atlas)
- [ ] `streamlit run src/bionexo/application/webapp/main.py` ejecutado
- [ ] Registro de usuario completado
- [ ] Ingesta manual guardada
- [ ] Ingesta con imagen guardada
- [ ] Historial muestra datos
- [ ] No hay errores en consola

---

## 📞 Soporte

Si tienes problemas, verifica:
1. [QUICKSTART.md](QUICKSTART.md) - Configuración rápida
2. [INTAKES_SETUP.md](INTAKES_SETUP.md) - Documentación detallada
3. [examples_intakes.py](examples_intakes.py) - Ejemplos de código
4. Errores de consola (copia el mensaje)

---

**¡Listo! Tu sistema de registro de ingestas está configurado** ✅
