## 🏥 Sección de Síntomas - Implementación Completada

### ✅ Cambios Realizados

#### 1. **Nuevo Modelo: SymptomReport** 
   - Ubicación: `src/bionexo/domain/entity/wellness_logs.py`
   - Campos:
     - `user_id`, `timestamp` - Índices TimeSeries
     - `time_of_day`, `hour_start`, `hour_end` - Momento del día
     - **Síntomas físicos:** dolor general, síntomas localizados por zona
     - **Estado emocional:** ánimo, nivel de estrés, ansiedad
     - **Energía:** nivel de energía, calidad del sueño
     - **Gastrointestinales:** problemas digestivos, apetito, náusea
     - **Otros:** dificultad respiratoria, mareo, fatiga
     - **Notas:** medicamentos, desencadenantes, observaciones libres

#### 2. **Funciones en db.py**
   - `save_symptom_report()` - Guardar reporte de síntomas
   - `get_symptom_reports_from_db()` - Obtener reportes del usuario
   - `create_wellness_logs_timeseries_collection()` - Setup de colección

#### 3. **Interfaz Streamlit en app.py**
   - **Menú:** Agregada opción "Síntomas" (4 tabs principales)
   - **Registro de síntomas:**
     - Selector de momento del día (Mañana/Tarde/Noche o personalizado)
     - Formulario completo con 7 secciones
     - Síntomas localizados por zona corporal (expandibles)
     - Escalas 1-10 para intensidades
   
   - **Historial actualizado:**
     - 2 tabs: "Ingestas" y "Síntomas"
     - Tabla resumen de reportes
     - Estadísticas agregadas (estrés, ansiedad, energía)
     - Vista detallada seleccionable de cada reporte

#### 4. **Base de Datos MongoDB**
   - Nueva colección `wellness_logs` (TimeSeries)
   - Índice: `(user_id, timestamp)`
   - Granularidad: minutes
   - Compresión automática de datos históricos

#### 5. **Setup Script Actualizado**
   - Script `setup_mongodb.py` crea colección `wellness_logs`
   - Índices optimizados automáticamente
   - Verificación de errores

---

### 📊 Estructura de la Sección de Síntomas

```
Registro de Síntomas
├── 📋 Información Temporal
│   ├── Momento del día (Mañana/Tarde/Noche/Personalizado)
│   └── Rango de horas
│
├── 💪 Síntomas Físicos
│   ├── ¿Dolor general? → Intensidad + Descripción
│   └── Síntomas localizados
│       ├── Zona del cuerpo
│       ├── Descripción
│       ├── Intensidad
│       └── Duración
│
├── 😊 Estado Emocional
│   ├── Ánimo (Feliz/Neutral/Triste/Ansioso/etc)
│   ├── Intensidad del sentimiento
│   ├── Nivel de estrés
│   └── Nivel de ansiedad
│
├── ⚡ Energía y Descanso
│   ├── Nivel de energía (1-10)
│   └── Calidad del sueño (1-10)
│
├── 🍽️ Síntomas Gastrointestinales
│   ├── Problemas digestivos (multiselect)
│   ├── Apetito (Bajo/Normal/Alto)
│   └── ¿Náusea?
│
├── 🫁 Otros Síntomas
│   ├── Dificultad respiratoria
│   ├── Mareo
│   └── Fatiga
│
└── 📝 Información Adicional
    ├── Notas libres
    ├── Medicamentos tomados
    └── Posibles desencadenantes
```

---

### 📈 Historial - Sección de Síntomas

```
Historial de Síntomas
├── 📊 Tabla resumen
│   ├── Fecha/Hora
│   ├── Momento del día
│   ├── Síntomas detectados
│   ├── Ánimo
│   ├── Estrés
│   ├── Energía
│   └── Tiene notas ✅/❌
│
├── 📊 Estadísticas agregadas
│   ├── Estrés promedio
│   ├── Ansiedad promedio
│   └── Energía promedio
│
└── 🔍 Detalles del reporte seleccionado
    ├── Métricas (ánimo, estrés, energía, sueño, apetito)
    ├── Síntomas localizados
    ├── Dolor general
    ├── Problemas digestivos
    ├── Notas completas
    └── Medicamentos
```

---

### 🗄️ Estructura MongoDB - Colección `wellness_logs`

```javascript
{
  _id: ObjectId,
  user_id: "usuario@email.com",              // Metafield
  timestamp: ISODate("2024-01-15T14:30"),   // Timefield
  time_of_day: "Tarde",
  hour_start: 14,
  hour_end: 17,
  
  // Síntomas físicos
  wellness_logs: [
    {
      location: "cabeza",
      description: "dolor pulsante",
      intensity: 7,
      duration_minutes: 60
    }
  ],
  general_pain: true,
  pain_description: "dolor general moderado",
  pain_intensity: 5,
  
  // Estado emocional
  mood: "Ansioso",
  mood_intensity: 7,
  stress_level: 8,
  anxiety_level: 7,
  
  // Energía
  energy_level: 3,
  sleep_quality: 6,
  
  // GI
  digestive_issues: "Hinchazón, Reflujo",
  appetite: "Bajo",
  nausea: false,
  
  // Otros
  breathing_difficulty: false,
  dizziness: true,
  fatigue: true,
  
  // Notas
  notes: "Día estresante en el trabajo",
  medications_taken: ["Ibuprofeno"],
  triggers: ["estrés", "poco sueño"],
  created_at: ISODate("2024-01-15T14:30")
}
```

---

### 📝 Campos del Modelo SymptomReport

**Temporales:**
- `user_id: str` - Usuario propietario
- `timestamp: datetime` - Cuándo se registró
- `time_of_day: str` - Etiqueta del momento
- `hour_start: int` - Hora inicio (0-23)
- `hour_end: int` - Hora fin (0-23, opcional)

**Síntomas Físicos:**
- `wellness_logs: List[Symptom]` - Síntomas por zona (opcional)
- `general_pain: bool` - ¿Hay dolor general?
- `pain_description: str` - Tipo de dolor
- `pain_intensity: int` - Intensidad 1-10

**Estado Emocional:**
- `mood: str` - Feliz/Triste/Ansioso/etc
- `mood_intensity: int` - Intensidad 1-10
- `stress_level: int` - Estrés 1-10
- `anxiety_level: int` - Ansiedad 1-10

**Energía:**
- `energy_level: int` - Energía 1-10
- `sleep_quality: int` - Calidad sueño 1-10

**Gastrointestinales:**
- `digestive_issues: str` - Problemas digestivos
- `appetite: str` - Bajo/Normal/Alto
- `nausea: bool` - ¿Hay náusea?

**Otros:**
- `breathing_difficulty: bool` - Dificultad respiratoria
- `dizziness: bool` - Mareo
- `fatigue: bool` - Fatiga

**Notas:**
- `notes: str` - Observaciones libres
- `medications_taken: List[str]` - Medicamentos
- `triggers: List[str]` - Posibles desencadenantes

---

### 🔄 Flujo de Datos

1. **Usuario rellena formulario de síntomas**
   - Selecciona momento del día o rango personalizado
   - Completa todas las secciones (opcional excepto hora_start)
   - Puede agregar síntomas localizados específicos

2. **Sistema procesa y guarda**
   - Valida campos requeridos
   - Convierte listas de texto a arrays
   - Guarda con compresión en TimeSeries

3. **Usuario visualiza en Historial**
   - Ve tabla resumen de todos los reportes
   - Consulta estadísticas agregadas
   - Puede ver detalles completos de cada reporte

---

### ✅ Archivos Modificados/Creados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/bionexo/domain/entity/wellness_logs.py` | ✅ NUEVO | Modelo SymptomReport y Symptom |
| `src/bionexo/infrastructure/utils/db.py` | ✅ MODIFICADO | Funciones de síntomas + imports |
| `src/bionexo/application/webapp/app.py` | ✅ MODIFICADO | Sección "Síntomas" + Historial mejorado |
| `setup_mongodb.py` | ✅ MODIFICADO | Setup colección wellness_logs |

---

### 🚀 Uso

1. **Ejecutar setup (si es primera vez):**
   ```bash
   python setup_mongodb.py
   ```

2. **Usar en la app:**
   - Login → Registrar Ingesta → **Síntomas** ← NUEVO
   - Historial → Tab "Síntomas" (ver reportes previos)

3. **Programáticamente:**
   ```python
   from bionexo.domain.entity.wellness_logs import SymptomReport, Symptom
   from bionexo.infrastructure.utils.db import save_symptom_report, get_symptom_reports_from_db
   
   # Crear reporte
   report = SymptomReport(
       user_id="user@example.com",
       timestamp=datetime.now(),
       time_of_day="Tarde",
       hour_start=14,
       mood="Ansioso",
       stress_level=7
   )
   
   # Guardar
   save_symptom_report(db, report)
   
   # Recuperar
   reports = get_symptom_reports_from_db(db, "user@example.com")
   ```

---

**✅ Implementación completada exitosamente - Sin documentación adicional generada**
