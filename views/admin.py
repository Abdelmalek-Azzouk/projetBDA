import streamlit as st
import time
from src.scheduler import generate_schedule
from database.db_manager import run_query
import pandas as pd

def show():
    st.header("Administration des Examens")
    st.info("Service Planification : Génération et Optimisation")

    with st.expander("Paramètres de l'Algorithme", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Date début session", value=pd.to_datetime("2024-06-01"))
        with col2:
            days = st.number_input("Nombre de jours", min_value=1, value=5, step=1)

    if st.button("Lancer la Génération Automatique", type="primary"):
        status_container = st.status("Exécution de l'algorithme...", expanded=True)
        
        status_container.write("Calcul de répartition des salles...")
        time.sleep(0.5)
            
        start_time = time.time()
        
        unique_scheduled, rooms_booked, total_modules = generate_schedule(start_date, int(days))
        
        duration = time.time() - start_time
        success_rate = (unique_scheduled / total_modules) * 100 if total_modules > 0 else 0
            
        status_container.update(label="Terminé !", state="complete", expanded=False)

        st.subheader("Résultats de l'Optimisation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Temps d'exécution", f"{duration:.2f} s")
        c2.metric("Examens Placés", f"{unique_scheduled} / {total_modules}")
        c3.metric("Salles Réservées", rooms_booked)
        
        st.progress(success_rate / 100)
        
        if unique_scheduled < total_modules:
            st.error(f"Attention : {total_modules - unique_scheduled} modules n'ont pas pu être placés.")
        else:
            st.success(f"Planification complète réussie ! {rooms_booked} réservations de salles effectuées pour {unique_scheduled} examens.")