import streamlit as st
import pandas as pd
from database.db_manager import run_query

def show():
    st.header("Tableau de Bord Stratégique (Doyen)")
    st.markdown("Vue globale des indicateurs académiques et logistiques.")

    col1, col2, col3, col4 = st.columns(4)
    total_exams = run_query("SELECT COUNT(DISTINCT module_id) FROM examens").iloc[0,0]
    util_salles = run_query("""
        SELECT COUNT(DISTINCT salle_id) * 100.0 / (SELECT COUNT(*) FROM salles) 
        FROM examens
    """).iloc[0,0]
    nb_profs = run_query("SELECT COUNT(DISTINCT prof_id) FROM surveillances").iloc[0,0]

    col1.metric("Examens Planifiés", total_exams)
    col2.metric("Salles Utilisées", f"{util_salles:.1f}%")
    col3.metric("Profs Mobilisés", nb_profs)
    col4.metric("Incidents Signales", "0") 

    st.markdown("---")

    st.subheader("Évolution de la Charge des Examens par Jour")
    st.caption("Nombre d'examens uniques (modules) par département")

    daily_sql = """
        SELECT e.date_examen, d.nom as Departement, COUNT(DISTINCT e.module_id) as nb_examens
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        GROUP BY e.date_examen, d.nom
        ORDER BY e.date_examen
    """
    daily_df = run_query(daily_sql)
    if not daily_df.empty:
        chart_data = daily_df.pivot(index='date_examen', columns='Departement', values='nb_examens').fillna(0)
        st.bar_chart(chart_data)
    else:
        st.info("Aucune donnée d'examen pour le graphique.")

    st.markdown("---")
    
    st.subheader("Analyse Détaillée par Département")
    depts = run_query("SELECT id, nom FROM departements")
    if not depts.empty:
        selected_dept_nom = st.selectbox("Sélectionner un département :", depts['nom'])
        selected_dept_id = depts[depts['nom'] == selected_dept_nom]['id'].values[0]
        d_col1, d_col2, d_col3 = st.columns(3)
        vol = run_query(f"""
            SELECT COUNT(DISTINCT e.module_id) 
            FROM examens e
            JOIN modules m ON e.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            WHERE f.dept_id = {selected_dept_id}
        """).iloc[0,0]
        profs_active = run_query(f"""
            SELECT COUNT(DISTINCT p.id)
            FROM professeurs p
            JOIN surveillances s ON p.id = s.prof_id
            WHERE p.dept_id = {selected_dept_id}
        """).iloc[0,0]
        nb_forms = run_query(f"""
            SELECT COUNT(DISTINCT f.id)
            FROM formations f
            JOIN modules m ON m.formation_id = f.id
            JOIN examens e ON e.module_id = m.id
            WHERE f.dept_id = {selected_dept_id}
        """).iloc[0,0]
        d_col1.metric(f"Examens (Modules)", vol)
        d_col2.metric("Profs Sollicités", profs_active)
        d_col3.metric("Formations", nb_forms)
    
    st.markdown("---")

    st.subheader("Taux d'Occupation Global (Salles & Amphis)")
    occupation_df = run_query("""
        SELECT s.nom, s.type, COUNT(e.id) as sessions
        FROM salles s
        LEFT JOIN examens e ON s.id = e.salle_id
        GROUP BY s.id
        ORDER BY sessions DESC
    """)
    st.bar_chart(occupation_df.set_index("nom")["sessions"])