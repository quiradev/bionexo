import streamlit as st
import os
from dotenv import load_dotenv
from src.utils.db import get_db
from src.utils.api_client import analyze_image
from src.models.user import User
from src.models.food import Food
from src.models.intake import Intake
import datetime
import pandas as pd

load_dotenv()

st.title("Bionexo - Seguimiento Nutricional")

# Conectar a DB
db = get_db()

# Sidebar para navegación
menu = st.sidebar.selectbox("Menú", ["Perfil", "Registrar Ingesta", "Historial", "Análisis"])

if menu == "Perfil":
    st.header("Perfil de Usuario")
    # Formulario para info personal
    name = st.text_input("Nombre")
    age = st.number_input("Edad", min_value=1)
    gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
    allergies = st.text_area("Alergenos conocidos (separados por coma)")
    if st.button("Guardar Perfil"):
        user = User(name, age, gender, allergies.split(','))
        # Guardar en DB
        st.success("Perfil guardado")

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
    intakes = []  # Query from DB
    df = pd.DataFrame(intakes)
    st.dataframe(df)

elif menu == "Análisis":
    st.header("Análisis Nutricional")
    # Gráficos de kcal, detección de patrones, etc.
    st.write("Funcionalidad en desarrollo")