import streamlit as st
import os
from scripts.kpis import main as kpis_main

st.set_page_config(layout="wide")


GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VALID_EMAIL = os.getenv("VALID_EMAIL")
VALID_PASSWORD = os.getenv("VALID_PASSWORD")


# Función para la lógica del login
def login():
    st.title("Iniciar sesión")

    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if email == VALID_EMAIL and password == VALID_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()  # Recargar la página después de iniciar sesión
        else:
            st.error("Correo electrónico o contraseña incorrectos.")


# Función principal de la app
def main():

    # Verificar si el usuario ya ha iniciado sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Si el usuario no ha iniciado sesión, mostrar pantalla de login
    if not st.session_state['logged_in']:
        login()
    else:
        # Botón de cerrar sesión
        if st.sidebar.button("Cerrar sesión"):
            st.session_state['logged_in'] = False
            st.rerun()  # Recargar la página después de cerrar sesión

        # Ejecutar el contenido principal de la aplicación (kpis)
        kpis_main()


if __name__ == "__main__":
    main()
