import streamlit as st
import pandas as pd
from database.db_manager import run_query, set_edt_validation, is_edt_validated

def show():
    st.header("Tableau de Bord Stratégique (Doyen)")
    st.markdown("Vue globale des indicateurs académiques et logistiques.")

    st.warning("Zone de Contrôle")
    col_v1, col_v2 = st.columns([3, 1])

    is_published = is_edt_validated()

    with col_v1:
        if is_published:
            st.success("État : PUBLIÉ. Les étudiants et professeurs ont accès aux plannings.")
        else:
            st.error("État : BROUILLON. Les plannings sont masqués pour les utilisateurs.")

    with col_v2:
        if is_published:
            if st.button("Retirer la publication", type="secondary"):
                set_edt_validation(False)
                st.rerun()
        else:
            if st.button("Valider & Publier", type="primary"):
                set_edt_validation(True)
                st.rerun()

    st.markdown("---")

    st.subheader("Observations transmises par les Chefs de Département")
    chef_msgs_sql = """
        SELECT cm.sent_at as 'Date',
               d.nom as 'Département',
               cm.message as 'Message'
        FROM chef_messages cm
        LEFT JOIN departements d ON cm.dept_id = d.id
        ORDER BY cm.sent_at DESC
    """
    chef_msgs_df = run_query(chef_msgs_sql)
    if not chef_msgs_df.empty:
        st.dataframe(chef_msgs_df, use_container_width=True)
    else:
        st.info("Aucune observation reçue des chefs de département.")

    st.markdown("---")

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