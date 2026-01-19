import streamlit as st
from views import doyen, admin, chef, student_prof
from database.db_manager import init_db
import os

if not os.path.exists("data/university.db"):
    init_db()

st.set_page_config(page_title="POETEU - Planning Examens", layout="wide", page_icon=None)

st.sidebar.title("ProjetBDA")
st.sidebar.markdown("*Plateforme d'Optimisation des Emplois du Temps*")
st.sidebar.markdown("---")

role = st.sidebar.radio(
    "Accès par Rôle :",
    ("Vice-Doyen / Doyen", "Administrateur (Planif)", "Chef de Département", "Étudiant / Prof")
)

st.sidebar.markdown("---")
st.sidebar.info("Base de données : Connectée")

if role == "Vice-Doyen / Doyen":
    doyen.show()
elif role == "Administrateur (Planif)":
    admin.show()
elif role == "Chef de Département":
    chef.show()
elif role == "Étudiant / Prof":
    student_prof.show()