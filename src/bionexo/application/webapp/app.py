import streamlit as st
import os
from dotenv import load_dotenv
from bionexo.infrastructure.utils.db import db_user_exists, get_db, get_intakes_from_db, save_user, save_intake, save_wellness_report, get_wellness_reports_from_db
from bionexo.infrastructure.utils.api_client import analyze_image
from bionexo.domain.entity.user import PersonalIntakesRecommendations, User, AgeGroup, Sex, Activity
# from bionexo.domain.entity.food import Food
from bionexo.domain.entity.intake import Intake
from bionexo.domain.entity.wellness_logs import Symptom, WellnessReport
import datetime
import pandas as pd
import hashlib
from PIL import Image
import io

from bionexo.infrastructure.utils.functions import hash_password

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
            submitted = st.form_submit_button("💾 Guardar Perfil", use_container_width=True)
            
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
                            st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error al guardar el perfil: {str(e)}")


    def main(self):
        st.title("Bionexo - Seguimiento Nutricional")

        # Conectar a DB
        db = self.get_db_connection()

        # Sidebar para navegación
        menu = st.sidebar.selectbox("Menú", ["Perfil", "Registrar Ingesta", "Registrar Bienestar", "Historial", "Análisis"])

        if menu == "Perfil":
            st.header("Perfil de Usuario")
            
            
        elif menu == "Registrar Ingesta":
            st.header("Registrar Ingesta de Alimentos")
            
            # Opción para subir imagen o manual
            tab1, tab2 = st.tabs(["Manual", "Con Imagen"])
            
            with tab1:
                st.subheader("Registro Manual")
                with st.form("manual_intake_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        food_name = st.text_input("Nombre del Alimento *", placeholder="Ej: Pollo con arroz")
                    with col2:
                        quantity = st.number_input("Cantidad (g) *", min_value=1, step=10, value=100)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        kcal = st.number_input("Calorías (kcal) *", min_value=0.0, step=10.0, value=200.0)
                    with col2:
                        feeling = st.selectbox(
                            "¿Cómo te sientes después?",
                            ["Bien", "Neutro", "Hinchado", "Con hambre", "Saciado"]
                        )
                    
                    ingredients_input = st.text_area(
                        "Ingredientes (separados por coma)",
                        placeholder="Ej: pollo, arroz, sal, aceite",
                        height=60
                    )
                    
                    voice_description = st.text_area(
                        "Descripción adicional (voz transcrita o notas)",
                        placeholder="Notas sobre la comida...",
                        height=60
                    )
                    
                    submitted = st.form_submit_button("💾 Guardar Ingesta", use_container_width=True)
                    
                    if submitted:
                        if not food_name or quantity <= 0 or kcal <= 0:
                            st.error("Por favor, completa todos los campos marcados con *")
                        else:
                            try:
                                ingredients = [
                                    ing.strip() for ing in ingredients_input.split(",")
                                    if ing.strip()
                                ] if ingredients_input else None
                                
                                intake = Intake(
                                    user_id=st.session_state.get("user_id"),
                                    food_name=food_name,
                                    quantity=quantity,
                                    kcal=kcal,
                                    timestamp=datetime.datetime.now(),
                                    ingredients=ingredients if ingredients else None,
                                    voice_description=voice_description if voice_description else None,
                                    feeling=feeling
                                )
                                
                                if save_intake(db, intake):
                                    st.success("✅ Ingesta registrada correctamente")
                                    st.balloons()
                                else:
                                    st.error("❌ Error al guardar la ingesta")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            
            with tab2:
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
                    
                    with st.form("image_intake_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            food_name = st.text_input("Nombre del Alimento *", placeholder="Ej: Pollo con arroz")
                        with col2:
                            quantity = st.number_input("Cantidad (g) *", min_value=1, step=10, value=100)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            kcal = st.number_input("Calorías (kcal) *", min_value=0.0, step=10.0, value=200.0)
                        with col2:
                            feeling = st.selectbox(
                                "¿Cómo te sientes después?",
                                ["Bien", "Neutro", "Hinchado", "Con hambre", "Saciado"],
                                key="feeling_image"
                            )
                        
                        ingredients_input = st.text_area(
                            "Ingredientes (separados por coma)",
                            placeholder="Ej: pollo, arroz, sal, aceite",
                            height=60
                        )
                        
                        voice_description = st.text_area(
                            "Descripción adicional (voz transcrita o notas)",
                            placeholder="Notas sobre la comida...",
                            height=60
                        )
                        
                        submitted = st.form_submit_button("💾 Guardar Ingesta con Imagen", use_container_width=True)
                        
                        if submitted:
                            if not food_name or quantity <= 0 or kcal <= 0:
                                st.error("Por favor, completa todos los campos marcados con *")
                            else:
                                try:
                                    # Convertir imagen a bytes
                                    image_bytes = io.BytesIO()
                                    image.save(image_bytes, format="PNG")
                                    image_data = image_bytes.getvalue()
                                    
                                    ingredients = [
                                        ing.strip() for ing in ingredients_input.split(",")
                                        if ing.strip()
                                    ] if ingredients_input else None
                                    
                                    intake = Intake(
                                        user_id=st.session_state.get("user_id"),
                                        food_name=food_name,
                                        quantity=quantity,
                                        kcal=kcal,
                                        timestamp=datetime.datetime.now(),
                                        ingredients=ingredients if ingredients else None,
                                        image_data=image_data,
                                        voice_description=voice_description if voice_description else None,
                                        feeling=feeling
                                    )
                                    
                                    if save_intake(db, intake):
                                        st.success("✅ Ingesta con imagen registrada correctamente")
                                        st.balloons()
                                    else:
                                        st.error("❌ Error al guardar la ingesta")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")

        elif menu == "Registrar Bienestar":
            st.header("Registrar Bienestar y Síntomas")
            
            with st.form("wellness_report_form"):
                st.subheader("📋 Información Temporal")
                
                col1, col2 = st.columns(2)
                with col1:
                    time_of_day = st.selectbox(
                        "Momento del día *",
                        ["Mañana (00:00 - 11:59)", "Tarde (12:00 - 17:59)", "Noche (18:00 - 23:59)", "Personalizado"]
                    )
                
                with col2:
                    hour_start = st.number_input(
                        "Hora inicio (0-23) *",
                        min_value=0,
                        max_value=23,
                        value=12,
                        step=1
                    )
                
                hour_end = None
                if time_of_day != "Personalizado":
                    hour_end = hour_start + 1
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("")
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
                    appetite = st.selectbox(
                        "¿Cómo está tu apetito?",
                        ["Bajo", "Normal", "Alto", "N/A"]
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
                submitted = st.form_submit_button("💾 Guardar Reporte de Síntomas", use_container_width=True)
                
                if submitted:
                    try:
                        wellness_report = WellnessReport(
                            user_id=st.session_state.get("user_id"),
                            timestamp=datetime.datetime.now(),
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
                            appetite=appetite if appetite != "N/A" else None,
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
                            st.balloons()
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
                    # Convertir a DataFrame para mejor visualización
                    display_data = []
                    for intake in intakes:
                        display_data.append({
                            "Fecha": intake.get("timestamp").strftime("%Y-%m-%d %H:%M") if hasattr(intake.get("timestamp"), "strftime") else intake.get("timestamp"),
                            "Alimento": intake.get("food_name"),
                            "Cantidad (g)": intake.get("quantity"),
                            "Calorías": intake.get("kcal"),
                            "Ingredientes": ", ".join(intake.get("ingredients", [])) if intake.get("ingredients") else "-",
                            "Cómo te sentiste": intake.get("feeling", "-"),
                            "Imagen": "✅" if intake.get("image_data") else "❌"
                        })
                    
                    df = pd.DataFrame(display_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Estadísticas
                    st.divider()
                    st.subheader("📊 Estadísticas")
                    col1, col2, col3 = st.columns(3)
                    
                    total_kcal = sum([intake.get("kcal", 0) for intake in intakes])
                    avg_kcal = total_kcal / len(intakes) if intakes else 0
                    total_meals = len(intakes)
                    
                    with col1:
                        st.metric("Total de Ingestas", total_meals)
                    with col2:
                        st.metric("Calorías Totales", f"{total_kcal:.0f} kcal")
                    with col3:
                        st.metric("Promedio por Ingesta", f"{avg_kcal:.0f} kcal")
                else:
                    st.info("No hay ingestas registradas aún. ¡Comienza a registrar tus comidas!")
            
            with hist_tab2:
                st.subheader("Historial de Síntomas")
                
                wellness_reports = get_wellness_reports_from_db(db, st.session_state.get("user_id"), limit=100)
                
                if wellness_reports:
                    # Convertir a DataFrame para mejor visualización
                    display_data = []
                    for report in wellness_reports:
                        timestamp = report.get("timestamp")
                        if hasattr(timestamp, "strftime"):
                            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
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
                    st.dataframe(df, use_container_width=True)
                    
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
                        format_func=lambda x: f"{wellness_reports[x].get('timestamp', 'N/A')} - {wellness_reports[x].get('time_of_day', 'N/A')}"
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
                            st.write(f"**Apetito:** {report.get('appetite', 'N/A')}")
                        
                        if report.get("wellness_logs"):
                            st.write("**Síntomas Localizados:**")
                            for symptom in report.get("wellness_logs", []):
                                st.write(f"- **{symptom.get('location')}:** {symptom.get('description')} (Intensidad: {symptom.get('intensity')}/10)")
                        
                        if report.get("general_pain"):
                            st.write(f"**Dolor General:** {report.get('pain_description', 'N/A')} (Intensidad: {report.get('pain_intensity')}/10)")
                        
                        if report.get("digestive_issues"):
                            st.write(f"**Problemas digestivos:** {report.get('digestive_issues')}")
                        
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