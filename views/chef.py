import streamlit as st
from database.db_manager import run_query

def show():
    st.header("Vue Chef de Département")

    user_id = st.session_state.get("user_id", None)
    if user_id is None:
        st.error("Utilisateur non identifié.")
        return

    dept = run_query(f"SELECT id, nom FROM departements WHERE id = {user_id}")
    if dept.empty:
        st.warning("Aucun département correspondant à votre accès n'a été trouvé.")
        return

    selected_dept_id = dept.iloc[0]['id']
    selected_dept_name = dept.iloc[0]['nom']

    st.markdown(f"### Planning : {selected_dept_name}")

    stats = run_query(f"""
        SELECT COUNT(e.id) 
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        WHERE f.dept_id = {selected_dept_id}
    """)
    st.metric("Examens Départementaux", stats.iloc[0,0])

    sql_schedule = f"""
        SELECT f.nom as Formation, m.nom as Module, e.date_examen, e.heure_debut, s.nom as Salle
        FROM examens e
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN salles s ON e.salle_id = s.id
        WHERE f.dept_id = {selected_dept_id}
        ORDER BY f.nom, e.date_examen
    """
    df_sched = run_query(sql_schedule)
    
    if not df_sched.empty:
        st.dataframe(df_sched, use_container_width=True)
    else:
        st.info("Aucun examen planifié pour ce département.")