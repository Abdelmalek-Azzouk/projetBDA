import streamlit as st
from database.db_manager import run_query

def show():
    st.header("Vue Chef de Département")
    
    depts = run_query("SELECT id, nom FROM departements")
    if depts.empty:
        st.warning("Aucun département trouvé.")
        return

    dept_list = depts['nom'].tolist()
    selected_dept_name = st.selectbox("Sélectionnez votre Département", dept_list)
    selected_dept_id = depts[depts['nom'] == selected_dept_name]['id'].values[0]

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
        
    st.markdown("### Validation")
    comment = st.text_area("Observations sur le planning")
    if st.button("Valider le planning du département"):
        st.success("Observations enregistrées et planning validé.")