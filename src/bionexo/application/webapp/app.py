import streamlit as st
import os
from dotenv import load_dotenv
from bionexo.infrastructure.utils.db import db_user_exists, get_db, get_intakes_from_db, save_user
from bionexo.infrastructure.utils.api_client import analyze_image
from bionexo.domain.entity.user import PersonalIntakesRecommendations, User, AgeGroup, Sex, Activity
# from bionexo.domain.entity.food import Food
from bionexo.domain.entity.intake import Intake
import datetime
import pandas as pd
import hashlib

from bionexo.infrastructure.utils.functions import hash_password

class MainApp:
    def __init__(self):
        self.db = self.get_db_connection()

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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Nombre *", placeholder="Ej: Juan Pérez")
            with col2:
                email = st.text_input("Email *", placeholder="Ej: juan@email.com")
            with col3:
                password = st.text_input("Contraseña *", type="password")
            
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
        menu = st.sidebar.selectbox("Menú", ["Perfil", "Registrar Ingesta", "Historial", "Análisis"])

        if menu == "Perfil":
            st.header("Perfil de Usuario")
            
            
        elif menu == "Registrar Ingesta":
            st.header("Registrar Ingesta de Alimentos")
            # Opción para subir imagen o manual
            option = st.radio("Método", ["Manual", "Subir Imagen"])
            if option == "Manual":
                food_name = st.text_input("Nombre del Alimento")
                quantity = st.number_input("Cantidad (g)", min_value=1)
                kcal = st.number_input("Kcal")
                if st.button("Registrar"):
                    intake = Intake(food_name, quantity, kcal, datetime.datetime.now())
                    # Guardar en DB
                    st.success("Registrado")
            elif option == "Subir Imagen":
                uploaded_file = st.file_uploader("Sube una imagen de la receta")
                if uploaded_file:
                    # Analizar con Gemini
                    result = analyze_image(uploaded_file)
                    st.write("Alimentos detectados:", result)
                    # Permitir editar y registrar

        elif menu == "Historial":
            st.header("Historial de Ingestas")
            # Mostrar tabla de ingestas
            intakes = get_intakes_from_db(db, st.session_state.get("user_id"))  # Función hipotética
            df = pd.DataFrame(intakes)
            st.dataframe(df)

        elif menu == "Análisis":
            st.header("Análisis Nutricional")
            # Gráficos de kcal, detección de patrones, etc.
            st.write("Funcionalidad en desarrollo")