# Bionexo - Seguimiento Nutricional Inteligente

## Descripción

Bionexo es una aplicación web desarrollada con Streamlit que permite gestionar el consumo de calorías y alimentos, proporcionando un seguimiento nutricional enfocado en la detección de alergenos y alimentos que puedan causar molestias. Utiliza la API de Gemini de Google (en formato compatible con OpenAI) para analizar imágenes de recetas y descomponerlas en alimentos y cantidades. Toda la información se almacena en una base de datos MongoDB remota, con credenciales gestionadas a través de un archivo `.env`.

### Funcionalidades Principales

- **Registro de Alimentos**: Ingreso manual o mediante subida de imágenes para análisis automático.
- **Seguimiento Nutricional**: Monitoreo de kcal, nutrientes y componentes adicionales.
- **Detección de Alergenos y Molestias**: Registro de cómo se siente el usuario después de la ingesta, incluyendo visitas al baño y ciclos menstruales (para mujeres).
- **Análisis Inteligente**: Inferencia de alimentos problemáticos basada en información personal y patrones de ingesta.
- **Información Personal**: Almacenamiento de datos como edad, género, alergenos conocidos y ciclo menstrual.

## Estructura del Proyecto

```
bionexo/
├── app.py                 # Aplicación principal en Streamlit
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (credenciales)
├── src/
│   ├── models/
│   │   ├── user.py        # Modelo de Usuario
│   │   ├── food.py        # Modelo de Alimento
│   │   └── intake.py      # Modelo de Ingesta
│   └── utils/
│       ├── db.py          # Conexión a MongoDB
│       └── api_client.py  # Cliente para API de Gemini
├── LICENSE
└── README.md
```

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/tuusuario/bionexo.git
   cd bionexo
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno en `.env`:
   - `MONGODB_URI`: URI de conexión a MongoDB Atlas.
   - `GEMINI_API_KEY`: Clave API de Google Gemini.

4. Ejecuta la aplicación:
   ```
   streamlit run app.py
   ```

## Uso

- **Perfil**: Ingresa tu información personal, incluyendo alergenos y ciclo menstrual.
- **Registrar Ingesta**: Elige entre ingreso manual o subida de imagen para registrar alimentos.
- **Historial**: Visualiza un registro de tus ingestas pasadas.
- **Análisis**: Explora gráficos y insights sobre tu nutrición y posibles intolerancias.

## Tecnologías Utilizadas

- **Streamlit**: Framework para la interfaz web.
- **MongoDB**: Base de datos NoSQL para almacenamiento.
- **Google Gemini API**: Análisis de imágenes para descomposición de recetas.
- **Python**: Lenguaje de programación principal.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.
