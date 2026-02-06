from git import List
import streamlit as st
import os
from dotenv import load_dotenv
from bionexo.infrastructure.utils.db import db_user_exists, get_db, get_ingredients_for_meal, get_intakes_from_db, save_user, save_intake, save_wellness_report, get_wellness_reports_from_db, get_unique_meal_names_from_db
from bionexo.infrastructure.utils.api_client import analyze_image
from bionexo.domain.entity.user import PersonalIntakesRecommendations, User, AgeGroup, Sex, Activity
# from bionexo.domain.entity.food import Food
from bionexo.domain.entity.intake import Intake
from bionexo.domain.entity.wellness_logs import Symptom, WellnessReport
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import hashlib
from PIL import Image
import io

from bionexo.infrastructure.utils.functions import hash_password, utc_to_local

class MainApp:
    def __init__(self):
        self.db = self.get_db_connection()
        st.set_page_config(
            page_title="Bionexo - Seguimiento Nutricional",
            page_icon="🍽️",
            layout="centered",
            initial_sidebar_state="expanded",
            menu_items={
                'About': "Aplicación desarrollada por el equipo de Bionexo."
            }
        )

    @staticmethod
    @st.cache_resource
    def get_db_connection():
        return get_db()
    
    def run(self):
        if not st.session_state.get("logged"):
            self.login()
        else:
            self.main()

    def login(self):
        st_login_tab, st_register_tab = st.tabs(["Iniciar Sesión", "Registrarse"])
        with st_login_tab:
            st.title("Bionexo - Login")
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            if st.button("Iniciar Sesión"):
                if db_user_exists(self.db, email, password):
                    st.session_state["logged"] = True
                    st.session_state["user_id"] = email
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

        with st_register_tab:
            self.register()
        
    def register(self):
        st.title("Bionexo - Registro")
        db = self.get_db_connection()
        with st.form("profile_form"):
            # === SECCIÓN 1: INFORMACIÓN PERSONAL ===
            st.subheader("📋 Información Personal")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre *", placeholder="Ej: Juan Pérez")
            with col2:
                email = st.text_input("Email *", placeholder="Ej: juan@email.com")
            
            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Contraseña *", type="password")
            with col2:
                password_config = st.text_input("Confirmar Contraseña *", type="password")
            
            if password != password_config:
                st.warning("Las contraseñas no coinciden")

            # === SECCIÓN 2: DATOS DEMOGRÁFICOS ===
            st.subheader("👤 Datos Demográficos")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                age_group = st.selectbox(
                    "Grupo Etario *",
                    options=[
                        AgeGroup.BABY,
                        AgeGroup.CHILDREN,
                        AgeGroup.TEEN,
                        AgeGroup.ADULT,
                        AgeGroup.ELDERLY
                    ],
                    format_func=lambda x: {
                        "baby": "Bebé (0-2 años)",
                        "children": "Niño (3-12 años)",
                        "teen": "Adolescente (13-17 años)",
                        "adult": "Adulto (18+ años)",
                        "elderly": "Adulto Mayor (65+ años)"
                    }.get(x, x)
                )
            with col2:
                sex = st.selectbox(
                    "Sexo *",
                    options=[Sex.MALE, Sex.FEMALE],
                    format_func=lambda x: "Macho" if x == Sex.MALE else "Hembra"
                )
            with col3:
                activity_level = st.selectbox(
                    "Nivel de Actividad *",
                    options=[
                        Activity.SEDENTARY,
                        Activity.ACTIVE,
                        Activity.VERY_ACTIVE
                    ],
                    format_func=lambda x: {
                        "sedentary": "Sedentario (poco o ningún ejercicio)",
                        "active": "Activo (ejercicio moderado 3-5 días/semana)",
                        "very active": "Muy Activo (ejercicio intenso 6-7 días/semana)"
                    }.get(x, x)
                )
            
            # === SECCIÓN 3: MEDIDAS FÍSICAS ===
            st.subheader("📏 Medidas Físicas")
            
            col1, col2 = st.columns(2)
            with col1:
                height_cm = st.number_input(
                    "Altura (cm) *",
                    min_value=30,
                    max_value=300,
                    value=170,
                    step=1
                )
            with col2:
                weight_kg = st.number_input(
                    "Peso (kg) *",
                    min_value=2.0,
                    max_value=600.0,
                    value=70.0,
                    step=0.5
                )
            
            # === SECCIÓN 4: CONDICIONES DE SALUD Y ALERGIAS ===
            st.subheader("⚕️ Salud y Alergias")
            
            health_conditions_input = st.text_area(
                "Condiciones de Salud (separadas por coma)",
                placeholder="Ej: diabetes, hipertensión, celiaquia",
                height=60
            )
            
            allergies_input = st.text_area(
                "Alergias Alimentarias (separadas por coma) *",
                placeholder="Ej: cacahuetes, mariscos, lácteos",
                height=60
            )
            
            # === BOTÓN SUBMIT ===
            st.divider()
            submitted = st.form_submit_button("💾 Guardar Perfil", width="stretch")
            
            if submitted:
                # Validaciones básicas
                if not name or not email or not password:
                    st.error("Por favor, completa todos los campos marcados con *")
                else:
                    try:
                        # Procesar listas
                        health_conditions = [
                            cond.strip() for cond in health_conditions_input.split(",")
                            if cond.strip()
                        ] if health_conditions_input else []
                        
                        if allergies_input.strip() == "":
                            allergies = []
                        else:
                            allergies = [
                                al.strip() for al in allergies_input.split(",")
                                if al.strip()
                            ]
                        
                        # Crear objeto User
                        user = User(
                            id=email,
                            name=name,
                            email=email,
                            password=hash_password(password),
                            personal_intakes_recommendations=PersonalIntakesRecommendations(
                                age_group=age_group,
                                sex=sex,
                                activity_level=activity_level,
                                height_cm=height_cm,
                                weight_kg=weight_kg,
                                health_conditions=health_conditions,
                                allergies=allergies,
                                nutrients_rdi=None
                            )
                        )
                        
                        # Guardar en DB
                        result = save_user(db, user)
                        if result is None:
                            st.error("❌ Error al guardar el perfil: El usuario ya existe.")
                        else:
                            st.success("✅ Perfil guardado correctamente")
                    except Exception as e:
                        st.error(f"❌ Error al guardar el perfil: {str(e)}")

    @classmethod
    @st.fragment
    def register_manual_intake(cls):
        db = get_db()
        with st.container():
            # === SECCIÓN 1: INFORMACIÓN TEMPORAL ===
            st.subheader("⏰ Información Temporal")
            
            col1, col2 = st.columns(2)
            with col1:
                meal_datetime = st.datetime_input(
                    "Fecha y hora de la comida *",
                    format="YYYY-MM-DD",
                    key="manual_meal_datetime",
                    value=st.session_state.get("manual_meal_datetime", datetime.datetime.now())
                )
            with col2:
                meal_type = st.selectbox(
                    "Tipo de comida *",
                    ["Desayuno", "Almuerzo", "Comida", "Cena", "Merienda", "Picar entre horas"]
                )
            
            # === SECCIÓN 2: NOMBRE DE LA INGESTA ===
            st.subheader("🍽️ Seleccionar o Crear Comida")
            
            # Obtener comidas previas
            previous_meals = get_unique_meal_names_from_db(db, st.session_state.get("user_id")) or []
        
            food_name = st.selectbox(
                "Selecciona una comida anterior *",
                previous_meals,
                accept_new_options=True,
                key="food_name_select",
                index=previous_meals.index(st.session_state.get("food_name_select", previous_meals[0])) if st.session_state.get("food_name_select") in previous_meals else None
            )
            ingredients_food = ""
            if food_name in previous_meals:
                ingredients_food = get_ingredients_for_meal(db, st.session_state.get("user_id"), food_name)
            
            # === SECCIÓN 5: INGREDIENTES ===
            st.subheader("🥘 Ingredientes")
            ingredients_input = st.text_area(
                "Ingredientes (separados por coma)",
                placeholder="Ej: pollo, arroz, sal, aceite",
                value=ingredients_food,
                key=f"ingredients_{food_name}",
                height=60
            )

            # === SECCIÓN 3: CANTIDAD Y CALORÍAS ===
            st.subheader("⚖️ Cantidad y Calorías")
            
            quantity = None
            quantity_description = None
            
            col1, col2 = st.columns(2)
            
            with col1:
                quantity = st.number_input(
                    "Cantidad en gramos",
                    min_value=1,
                    step=10,
                    value=100
                )
            with col2:
                quantity_description = st.text_input(
                    "Descripción (ej: medio plato, un vaso, 30% del plato)",
                    placeholder="Ej: Medio plato grande, un vaso de agua"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                kcal = st.number_input(
                    "Calorías (kcal) - Opcional",
                    min_value=0.0,
                    step=10.0,
                    value=0.0,
                    help="Se puede dejar en 0, se rellenará después con los ingredientes"
                )
                if kcal == 0.0:
                    kcal = None
            
            # === SECCIÓN 4: SENSACIÓN DESPUÉS DE COMER ===
            with col2:
                feeling_scale = st.slider(
                    "¿Cómo te sientes después? (10-20 min) *",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="1 = Con hambre, 10 = Muy hinchado/Saciado"
                )
            
            # === SECCIÓN 6: NOTAS ADICIONALES ===
            st.subheader("📝 Notas Adicionales")
            
            voice_description = st.text_area(
                "Descripción adicional (notas sobre la comida)",
                placeholder="Notas sobre la comida...",
                height=60
            )
            
            submitted = st.button("💾 Guardar Ingesta", width="stretch")
        
        if submitted:
            if not food_name:
                st.error("Por favor, ingresa el nombre de la comida")
            else:
                try:
                    # Crear timestamp completo con la fecha actual y hora especificada
                    tz = st.session_state.get("tz", "Europe/Madrid")
                    
                    # Convertir a UTC para almacenar
                    from bionexo.infrastructure.utils.functions import local_to_utc
                    intake_datetime = local_to_utc(meal_datetime, tz)
                    
                    ingredients = [
                        ing.strip() for ing in ingredients_input.split(",")
                        if ing.strip()
                    ] if ingredients_input else None
                    
                    intake = Intake(
                        user_id=st.session_state.get("user_id"),
                        food_name=food_name,
                        quantity=quantity,
                        kcal=kcal,
                        timestamp=intake_datetime,
                        meal_type=meal_type,
                        quantity_type="both",
                        quantity_description=quantity_description,
                        feeling_scale=feeling_scale,
                        ingredients=ingredients if ingredients else None,
                        voice_description=voice_description if voice_description else None
                    )
                    
                    if save_intake(db, intake):
                        st.toast("¡Ingesta guardada!", icon=":material/check:")
                    else:
                        st.toast("Error al guardar la ingesta", icon=":material/error:")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    @classmethod
    @st.fragment
    def register_image_intake(cls):
        db = get_db()
        st.subheader("Registro con Imagen")
        uploaded_file = st.file_uploader(
            "Sube una imagen de la comida",
            type=["jpg", "jpeg", "png", "webp"],
            help="Formato óptimo: JPG o PNG (máx 10MB)"
        )
        
        if uploaded_file:
            # Mostrar preview
            image = Image.open(uploaded_file)
            st.image(image, caption="Vista previa", use_column_width=True)
            
            
            # === SECCIÓN 1: INFORMACIÓN TEMPORAL ===
            st.subheader("⏰ Información Temporal")
            
            col1, col2 = st.columns(2)
            with col1:
                meal_datetime = st.datetime_input(
                    "Fecha y hora de la comida *",
                    format="YYYY-MM-DD",
                    value=st.session_state.get("image_meal_datetime", datetime.datetime.now()),
                    key="image_meal_datetime"
                )
            with col2:
                meal_type = st.selectbox(
                    "Tipo de comida *",
                    ["Desayuno", "Almuerzo", "Comida", "Cena", "Merienda", "Picar entre horas"],
                    key="image_meal_type"
                )
            
            # === SECCIÓN 2: NOMBRE DE LA INGESTA ===
            st.subheader("🍽️ Seleccionar o Crear Comida")
            
            # Obtener comidas previas
            previous_meals = get_unique_meal_names_from_db(db, st.session_state.get("user_id"))
            
            use_previous = st.checkbox("¿Usar una comida guardada previamente?", key="image_use_previous")
            
            if use_previous and previous_meals:
                food_name = st.selectbox(
                    "Selecciona una comida anterior *",
                    previous_meals,
                    key="image_previous_meals"
                )
            else:
                food_name = st.text_input(
                    "Nombre de la comida *",
                    placeholder="Ej: Pollo con arroz",
                    key="image_food_name"
                )
            
            # === SECCIÓN 3: CANTIDAD Y CALORÍAS ===
            st.subheader("⚖️ Cantidad y Calorías")
            
            quantity_option = st.radio(
                "¿Cómo prefieres indicar la cantidad? *",
                ["Gramos", "Descripción conversacional", "Ambas"],
                key="image_quantity_option"
            )
            
            quantity = None
            quantity_description = None
            
            col1, col2 = st.columns(2)
            
            if quantity_option in ["Gramos", "Ambas"]:
                with col1:
                    quantity = st.number_input(
                        "Cantidad en gramos",
                        min_value=1,
                        step=10,
                        value=100,
                        key="image_quantity"
                    )
            
            if quantity_option in ["Descripción conversacional", "Ambas"]:
                with col2 if quantity_option != "Ambas" else col1:
                    quantity_description = st.text_input(
                        "Descripción (ej: medio plato, un vaso, 30% del plato)",
                        placeholder="Ej: Medio plato grande, un vaso de agua",
                        key="image_quantity_desc_1"
                    )
            
            if quantity_option == "Ambas":
                with col2:
                    quantity_description = st.text_input(
                        "Descripción adicional",
                        placeholder="Ej: Medio plato grande",
                        key="image_quantity_desc_2"
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                kcal = st.number_input(
                    "Calorías (kcal) - Opcional",
                    min_value=0.0,
                    step=10.0,
                    value=0.0,
                    key="image_kcal",
                    help="Se puede dejar en 0, se rellenará después con los ingredientes"
                )
                if kcal == 0.0:
                    kcal = None
            
            # === SECCIÓN 4: SENSACIÓN DESPUÉS DE COMER ===
            with col2:
                feeling_scale = st.slider(
                    "¿Cómo te sientes después? (10-20 min) *",
                    min_value=1,
                    max_value=10,
                    value=5,
                    key="image_feeling_scale",
                    help="1 = Con hambre, 10 = Muy hinchado/Saciado"
                )
            
            # === SECCIÓN 5: INGREDIENTES ===
            st.subheader("🥘 Ingredientes")
            
            ingredients_input = st.text_area(
                "Ingredientes (separados por coma)",
                placeholder="Ej: pollo, arroz, sal, aceite",
                height=60,
                key="image_ingredients"
            )
            
            # === SECCIÓN 6: NOTAS ADICIONALES ===
            st.subheader("📝 Notas Adicionales")
            
            voice_description = st.text_area(
                "Descripción adicional (notas sobre la comida)",
                placeholder="Notas sobre la comida...",
                height=60,
                key="image_voice_desc"
            )
            
            submitted = st.button("💾 Guardar Ingesta con Imagen", width="stretch")
            
            if submitted:
                if not food_name:
                    st.error("Por favor, ingresa el nombre de la comida")
                elif quantity_option != "Descripción conversacional" and not quantity:
                    st.error("Por favor, ingresa la cantidad en gramos")
                elif quantity_option != "Gramos" and not quantity_description:
                    st.error("Por favor, ingresa una descripción de la cantidad")
                else:
                    try:
                        # Convertir imagen a bytes
                        image_bytes = io.BytesIO()
                        image.save(image_bytes, format="PNG")
                        image_data = image_bytes.getvalue()
                        
                        # Crear timestamp completo con la fecha actual y hora especificada
                        tz = st.session_state.get("tz", "Europe/Madrid")
                        # Convertir a UTC para almacenar
                        from bionexo.infrastructure.utils.functions import local_to_utc
                        intake_datetime = local_to_utc(meal_datetime, tz)
                        
                        ingredients = [
                            ing.strip() for ing in ingredients_input.split(",")
                            if ing.strip()
                        ] if ingredients_input else None
                        
                        intake = Intake(
                            user_id=st.session_state.get("user_id"),
                            food_name=food_name,
                            quantity=quantity,
                            kcal=kcal,
                            timestamp=intake_datetime,
                            meal_type=meal_type,
                            quantity_type=quantity_option,
                            quantity_description=quantity_description,
                            feeling_scale=feeling_scale,
                            ingredients=ingredients if ingredients else None,
                            image_data=image_data,
                            voice_description=voice_description if voice_description else None
                        )
                        
                        if save_intake(db, intake):
                            st.success("✅ Ingesta con imagen registrada correctamente")
                        else:
                            st.error("❌ Error al guardar la ingesta")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    @classmethod
    @st.fragment
    def register_intake(cls):
        tab1, tab2 = st.tabs(["Manual", "Con Imagen"])
        
        with tab1:
            cls.register_manual_intake()
        
        with tab2:
            cls.register_image_intake()


    @staticmethod
    def intake_card(intake: Intake):
        with st.container(border=True, width=200):
            with st.container(horizontal=True):
                st.write(f"**{intake.meal_type}**")
                local_timestamp = utc_to_local(intake.timestamp, st.session_state.get("tz", "Europe/Madrid"))
                st.caption(f"📅 {local_timestamp.strftime('%Y-%m-%d %H:%M')}")
            
            st.write(f"**{intake.food_name}**")
            ingredients  = intake.ingredients or []
            ingredients_str = []
            for ingredient in ingredients:
                ingredients_str.append(f"- {ingredient}")
            st.caption("\n".join(ingredients_str))

    @classmethod
    @st.fragment
    def intakes_history(cls, intakes: List[Intake]):
        st.subheader("📋 Historial de Ingestas")
        from bionexo.infrastructure.utils.functions import utc_to_local
        from collections import defaultdict
        
        if not intakes:
            st.info("No hay ingestas registradas aún.")
            return
        
        tz = st.session_state.get("tz", "Europe/Madrid")
        
        # Agrupar ingestas por fecha
        intakes_by_day = defaultdict(list)
        for intake in intakes:
            ts = getattr(intake, "timestamp", None)
            if hasattr(ts, "strftime"):
                local_ts = utc_to_local(ts, tz)
                day_key = local_ts.strftime("%Y-%m-%d")
            else:
                day_key = str(ts).split()[0]
            intakes_by_day[day_key].append(intake)
        
        # Mostrar por días (ordenados de más reciente a más antiguo)
        for day_key in sorted(intakes_by_day.keys(), reverse=True):
            day_intakes = intakes_by_day[day_key]
            
            # Ordenar ingestas por hora (de menor a mayor)
            day_intakes.sort(key=lambda intake: (
                utc_to_local(intake.timestamp, tz).time() 
                if hasattr(intake.timestamp, "strftime") 
                else "00:00"
            ))
            
            # Encabezado del día
            st.subheader(f"📅 {day_key}")
            
            # Distribuir tarjetas en columnas (4 tarjetas por fila)
            cols_per_row = 4
            for i in range(0, len(day_intakes), cols_per_row):
                cols = st.columns(min(cols_per_row, len(day_intakes) - i))
                for col_idx, col in enumerate(cols):
                    if i + col_idx < len(day_intakes):
                        with col:
                            cls.intake_card(day_intakes[i + col_idx])
            
            st.divider()

    def main(self):
        st.title("Bionexo - Seguimiento Nutricional")

        # Conectar a DB
        db = self.get_db_connection()

        # Zona horaria del usuario (sidebar)
        TIMEZONES = [
            "Europe/Madrid",
            "UTC",
            "America/New_York",
            "America/Sao_Paulo",
            "America/Los_Angeles",
            "Asia/Tokyo",
            "Asia/Shanghai"
        ]
        if "tz" not in st.session_state:
            st.session_state["tz"] = "Europe/Madrid"
        user_tz = st.sidebar.selectbox("Zona Horaria", TIMEZONES, index=TIMEZONES.index(st.session_state.get("tz", "Europe/Madrid")))
        st.session_state["tz"] = user_tz

        # Sidebar para navegación
        menu = st.sidebar.selectbox("Menú", ["Registrar Ingesta", "Registrar Bienestar", "Historial", "Análisis"])
    
            
        if menu == "Registrar Ingesta":
            st.header("Registrar Ingesta de Alimentos")
            self.register_intake()

        elif menu == "Registrar Bienestar":
            st.header("Registrar Bienestar y Síntomas")
            
            with st.container():
                st.subheader("📋 Información Temporal")
                
                col1, col2 = st.columns(2)
                with col1:
                    wellness_datetime = st.datetime_input(
                        "Fecha y hora del reporte *",
                        format="YYYY-MM-DD",
                        value=st.session_state.get("wellness_datetime", datetime.datetime.now()),
                        key="wellness_datetime"
                    )
                
                with col2:
                    time_of_day = st.selectbox(
                        "Momento del día *",
                        ["Mañana (00:00 - 11:59)", "Tarde (12:00 - 17:59)", "Noche (18:00 - 23:59)", "Personalizado"]
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    hour_start = st.number_input(
                        "Hora inicio (0-23) *",
                        min_value=0,
                        max_value=23,
                        value=12,
                        step=1
                    )
                
                with col2:
                    hour_end = st.number_input(
                        "Hora fin (0-23) (opcional)",
                        min_value=0,
                        max_value=23,
                        value=hour_start + 1,
                        step=1
                    )
                
                # Mapeo de tiempo del día
                time_of_day_map = {
                    "Mañana (00:00 - 11:59)": "Mañana",
                    "Tarde (12:00 - 17:59)": "Tarde",
                    "Noche (18:00 - 23:59)": "Noche",
                    "Personalizado": f"Custom {hour_start}:00-{hour_end}:00"
                }
                selected_time = time_of_day_map.get(time_of_day, time_of_day)
                
                st.divider()
                st.subheader("💪 Síntomas Físicos")
                
                general_pain = st.checkbox("¿Tienes dolor general?")
                pain_intensity = None
                pain_description = None
                
                if general_pain:
                    col1, col2 = st.columns(2)
                    with col1:
                        pain_intensity = st.slider(
                            "Intensidad del dolor (1-10)",
                            min_value=1,
                            max_value=10,
                            value=5
                        )
                    with col2:
                        pain_description = st.text_input("Describe el dolor (ej: pulsante, agudo)")
                
                # Síntomas específicos localizados
                st.write("**Síntomas localizados:**")
                symptoms_list = []
                
                col1, col2 = st.columns(2)
                with col1:
                    add_symptom = st.checkbox("Agregar síntoma específico")
                
                if add_symptom:
                    symptom_count = st.number_input("¿Cuántos síntomas específicos?", min_value=1, max_value=5, value=1)
                    
                    for i in range(symptom_count):
                        with st.expander(f"Síntoma {i+1}"):
                            symptom_location = st.text_input(
                                f"Zona del cuerpo *",
                                placeholder="Ej: cabeza, estómago, espalda, etc.",
                                key=f"location_{i}"
                            )
                            symptom_desc = st.text_area(
                                f"Descripción *",
                                placeholder="Ej: dolor de cabeza, náusea, etc.",
                                key=f"desc_{i}",
                                height=60
                            )
                            symptom_intensity = st.slider(
                                f"Intensidad (1-10) *",
                                min_value=1,
                                max_value=10,
                                value=5,
                                key=f"intensity_{i}"
                            )
                            symptom_duration = st.number_input(
                                f"Duración (minutos)",
                                min_value=0,
                                value=30,
                                key=f"duration_{i}"
                            )
                            
                            if symptom_location and symptom_desc:
                                symptoms_list.append(Symptom(
                                    location=symptom_location,
                                    description=symptom_desc,
                                    intensity=symptom_intensity,
                                    duration_minutes=symptom_duration if symptom_duration > 0 else None
                                ))
                
                st.divider()
                st.subheader("😊 Estado Emocional")
                
                col1, col2 = st.columns(2)
                with col1:
                    mood = st.selectbox(
                        "¿Cuál es tu estado de ánimo?",
                        ["Feliz", "Neutral", "Triste", "Ansioso", "Estresado", "Relajado", "Energético", "Cansado"]
                    )
                with col2:
                    mood_intensity = st.slider(
                        "Intensidad del sentimiento (1-10)",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="mood_intensity"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    stress_level = st.slider(
                        "Nivel de estrés (1-10)",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="stress"
                    )
                with col2:
                    anxiety_level = st.slider(
                        "Nivel de ansiedad (1-10)",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="anxiety"
                    )
                
                st.divider()
                st.subheader("⚡ Energía y Descanso")
                
                col1, col2 = st.columns(2)
                with col1:
                    energy_level = st.slider(
                        "Nivel de energía (1-10)",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="energy"
                    )
                with col2:
                    sleep_quality = st.slider(
                        "Calidad del sueño (1-10)",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="sleep"
                    )
                
                st.divider()
                st.subheader("🍽️ Síntomas Gastrointestinales")
                
                col1, col2 = st.columns(2)
                with col1:
                    digestive_issues = st.multiselect(
                        "¿Problemas digestivos?",
                        ["Hinchazón", "Estreñimiento", "Diarrea", "Reflujo", "Acidez", "Ninguno"]
                    )
                    digestive_issues_str = ", ".join(digestive_issues) if digestive_issues else None
                with col2:
                    digestive_comfort_scale = st.slider(
                        "Escala de comodidad digestiva",
                        min_value=1,
                        max_value=10,
                        value=5,
                        help="1 = Muy hinchado, 10 = Muy cómodo"
                    )
                with col2:
                    appetite_scale = st.slider(
                        "¿Cómo está tu apetito?",
                        min_value=1,
                        max_value=10,
                        value=5,
                        help="1 = Sin apetito, 10 = Muy hambriento"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    nausea = st.checkbox("¿Náusea?", key="nausea")
                with col2:
                    st.write("")
                
                st.divider()
                st.subheader("🫁 Otros Síntomas")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    breathing_difficulty = st.checkbox("Dificultad respiratoria")
                with col2:
                    dizziness = st.checkbox("Mareo")
                with col3:
                    fatigue = st.checkbox("Fatiga")
                
                st.divider()
                st.subheader("📝 Información Adicional")
                
                notes = st.text_area(
                    "Notas adicionales",
                    placeholder="Cualquier información extra que consideres importante...",
                    height=100
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    medications = st.text_input(
                        "Medicamentos tomados (separados por coma)",
                        placeholder="Ej: Ibuprofeno, Paracetamol"
                    )
                    medications_list = [m.strip() for m in medications.split(",") if m.strip()] if medications else None
                
                with col2:
                    triggers = st.text_input(
                        "Posibles desencadenantes",
                        placeholder="Ej: estrés, comida, clima"
                    )
                    triggers_list = [t.strip() for t in triggers.split(",") if t.strip()] if triggers else None
                
                st.divider()
                submitted = st.button("💾 Guardar Reporte de Síntomas", width="stretch")
                
                if submitted:
                    try:
                        tz = st.session_state.get("tz", "Europe/Madrid")
                        from bionexo.infrastructure.utils.functions import local_to_utc
                        wellness_ts = local_to_utc(wellness_datetime, tz)

                        wellness_report = WellnessReport(
                            user_id=st.session_state.get("user_id"),
                            timestamp=wellness_ts,
                            time_of_day=selected_time,
                            hour_start=hour_start,
                            hour_end=hour_end,
                            symptoms=symptoms_list if symptoms_list else None,
                            general_pain=general_pain,
                            pain_description=pain_description,
                            pain_intensity=pain_intensity,
                            mood=mood,
                            mood_intensity=mood_intensity,
                            stress_level=stress_level,
                            anxiety_level=anxiety_level,
                            energy_level=energy_level,
                            sleep_quality=sleep_quality,
                            digestive_issues=digestive_issues_str,
                            digestive_comfort_scale=digestive_comfort_scale,
                            appetite_scale=appetite_scale,
                            nausea=nausea,
                            breathing_difficulty=breathing_difficulty,
                            dizziness=dizziness,
                            fatigue=fatigue,
                            notes=notes if notes else None,
                            medications_taken=medications_list,
                            triggers=triggers_list
                        )
                        
                        if save_wellness_report(db, wellness_report):
                            st.success("✅ Reporte de síntomas guardado correctamente")
                        else:
                            st.error("❌ Error al guardar el reporte")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        elif menu == "Historial":
            st.header("Historial")
            
            hist_tab1, hist_tab2 = st.tabs(["Ingestas", "Bienestar"])
            
            with hist_tab1:
                st.subheader("Historial de Ingestas")
                
                intakes = get_intakes_from_db(db, st.session_state.get("user_id"), limit=100)
                
                if intakes:

                    self.intakes_history(intakes)
                    # Convertir a DataFrame para mejor visualización
                    display_data = []
                    from bionexo.infrastructure.utils.functions import utc_to_local
                    tz = st.session_state.get("tz", "Europe/Madrid")
                    for intake in intakes:
                        ts = getattr(intake, "timestamp", None)
                        if hasattr(ts, "strftime"):
                            local_ts = utc_to_local(ts, tz)
                            date_str = local_ts.strftime("%Y-%m-%d %H:%M")
                        else:
                            date_str = ts
                        display_data.append({
                            "Fecha": date_str,
                            "Tipo": getattr(intake, "meal_type", "-"),
                            "Alimento": intake.food_name,
                            "Cantidad": f"{intake.quantity}g" if intake.quantity else (getattr(intake, "quantity_description", "-")),
                            "Calorías": f"{intake.kcal}" if intake.kcal else "Pendiente",
                            "Sensación": f"{getattr(intake, 'feeling_scale', '-')}/10" if getattr(intake, 'feeling_scale', None) is not None else "-",
                            "Imagen": "✅" if getattr(intake, "image_data", None) else "❌"
                        })
                    
                    df = pd.DataFrame(display_data)
                    st.dataframe(df, width="stretch")
                    
                    # Estadísticas
                    st.divider()
                    st.subheader("📊 Estadísticas")
                    col1, col2, col3 = st.columns(3)
                    
                    total_kcal = sum([getattr(intake, "kcal", 0) for intake in intakes if getattr(intake, "kcal", None) is not None])
                    intakes_with_kcal = [intake for intake in intakes if getattr(intake, "kcal", None) is not None]
                    avg_kcal = total_kcal / len(intakes_with_kcal) if intakes_with_kcal else 0
                    total_meals = len(intakes)
                    
                    with col1:
                        st.metric("Total de Ingestas", total_meals)
                    with col2:
                        st.metric("Calorías Totales", f"{total_kcal:.0f} kcal" if total_kcal > 0 else "Pendiente")
                    with col3:
                        st.metric("Promedio por Ingesta", f"{avg_kcal:.0f} kcal" if avg_kcal > 0 else "Pendiente")
                else:
                    st.info("No hay ingestas registradas aún. ¡Comienza a registrar tus comidas!")
            
            with hist_tab2:
                st.subheader("Historial de Síntomas")
                
                wellness_reports = get_wellness_reports_from_db(db, st.session_state.get("user_id"), limit=100)
                
                if wellness_reports:
                    # Convertir a DataFrame para mejor visualización
                    display_data = []
                    from bionexo.infrastructure.utils.functions import utc_to_local
                    tz = st.session_state.get("tz", "Europe/Madrid")
                    for report in wellness_reports:
                        timestamp = report.get("timestamp")
                        if hasattr(timestamp, "strftime"):
                            local_ts = utc_to_local(timestamp, tz)
                            date_str = local_ts.strftime("%Y-%m-%d %H:%M")
                        else:
                            date_str = str(timestamp)
                        
                        # Resumen de síntomas
                        wellness_logs_summary = ""
                        if report.get("symptoms"):
                            wellness_logs_summary = ", ".join([f"{s.get('location', 'N/A')}" for s in report.get("symptoms", [])])
                        elif report.get("general_pain"):
                            wellness_logs_summary = f"Dolor General ({report.get('pain_intensity', '?')}/10)"
                        
                        display_data.append({
                            "Fecha": date_str,
                            "Momento": report.get("time_of_day", "N/A"),
                            "Síntomas": wellness_logs_summary or "Sin síntomas",
                            "Ánimo": report.get("mood", "N/A"),
                            "Estrés": f"{report.get('stress_level', '?')}/10",
                            "Energía": f"{report.get('energy_level', '?')}/10",
                            "Notas": "✅" if report.get("notes") else "❌"
                        })
                    
                    df = pd.DataFrame(display_data)
                    st.dataframe(df, width="stretch")
                    
                    # Estadísticas de síntomas
                    st.divider()
                    st.subheader("📊 Estadísticas de Síntomas")
                    
                    avg_stress = sum([r.get("stress_level", 0) for r in wellness_reports]) / len(wellness_reports) if wellness_reports else 0
                    avg_anxiety = sum([r.get("anxiety_level", 0) for r in wellness_reports]) / len(wellness_reports) if wellness_reports else 0
                    avg_energy = sum([r.get("energy_level", 0) for r in wellness_reports]) / len(wellness_reports) if wellness_reports else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Estrés Promedio", f"{avg_stress:.1f}/10")
                    with col2:
                        st.metric("Ansiedad Promedio", f"{avg_anxiety:.1f}/10")
                    with col3:
                        st.metric("Energía Promedio", f"{avg_energy:.1f}/10")
                    
                    # Reportes detallados
                    st.divider()
                    st.subheader("🔍 Detalles de Reportes")
                    
                    selected_report_idx = st.selectbox(
                        "Selecciona un reporte para ver detalles",
                        range(len(wellness_reports)),
                        format_func=lambda x: f"{(utc_to_local(wellness_reports[x].get('timestamp'), tz).strftime('%Y-%m-%d %H:%M') if hasattr(wellness_reports[x].get('timestamp'), 'strftime') else wellness_reports[x].get('timestamp', 'N/A'))} - {wellness_reports[x].get('time_of_day', 'N/A')}"
                    )
                    
                    if selected_report_idx is not None:
                        report = wellness_reports[selected_report_idx]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Ánimo:** {report.get('mood', 'N/A')}")
                            st.write(f"**Estrés:** {report.get('stress_level', '?')}/10")
                        with col2:
                            st.write(f"**Ansiedad:** {report.get('anxiety_level', '?')}/10")
                            st.write(f"**Energía:** {report.get('energy_level', '?')}/10")
                        with col3:
                            st.write(f"**Calidad del sueño:** {report.get('sleep_quality', '?')}/10")
                            st.write(f"**Apetito:** {report.get('appetite_scale', '?')}/10")
                        
                        if report.get("wellness_logs"):
                            st.write("**Síntomas Localizados:**")
                            for symptom in report.get("wellness_logs", []):
                                st.write(f"- **{symptom.get('location')}:** {symptom.get('description')} (Intensidad: {symptom.get('intensity')}/10)")
                        
                        if report.get("general_pain"):
                            st.write(f"**Dolor General:** {report.get('pain_description', 'N/A')} (Intensidad: {report.get('pain_intensity')}/10)")
                        
                        if report.get("digestive_issues"):
                            st.write(f"**Problemas digestivos:** {report.get('digestive_issues')}")
                        
                        if report.get("digestive_comfort_scale"):
                            st.write(f"**Comodidad digestiva:** {report.get('digestive_comfort_scale')}/10")
                        
                        if report.get("appetite_scale"):
                            st.write(f"**Apetito:** {report.get('appetite_scale')}/10")
                            
                        if report.get("notes"):
                            st.write(f"**Notas:** {report.get('notes')}")
                        
                        if report.get("medications_taken"):
                            st.write(f"**Medicamentos:** {', '.join(report.get('medications_taken', []))}")
                else:
                    st.info("No hay reportes de síntomas aún. ¡Comienza a registrar tus síntomas!")

        elif menu == "Análisis":
            st.header("Análisis Nutricional")
            # Gráficos de kcal, detección de patrones, etc.
            st.write("Funcionalidad en desarrollo")