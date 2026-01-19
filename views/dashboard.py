import streamlit as st
from database.db_manager import run_query

def show():
    st.title("Tableau de Bord Stratégique")
    
    stats = run_query("""
        SELECT 
            (SELECT COUNT(*) FROM examens) as nb_examens,
            (SELECT COUNT(*) FROM inscriptions) as nb_copies,
            (SELECT COUNT(*) FROM surveillances) as nb_surveillants
    """)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Examens", stats['nb_examens'][0])
    kpi2.metric("Inscriptions gérées", stats['nb_copies'][0])
    kpi3.metric("Surveillances affectées", stats['nb_surveillants'][0])
    
    st.markdown("---")
    
    st.subheader("Analyse des Conflits (Détection SQL)")
    
    conflicts_query = """
        SELECT e.date_examen, i.etudiant_id, COUNT(*) as daily_exams
        FROM examens e
        JOIN inscriptions i ON e.module_id = i.module_id
        GROUP BY e.date_examen, i.etudiant_id
        HAVING daily_exams > 1
    """
    conflicts = run_query(conflicts_query)
    
    if conflicts.empty:
        st.success("Aucun conflit Étudiant (Max 1 examen/jour) détecté.")
    else:
        st.error(f"{len(conflicts)} conflits étudiants détectés !")
        st.dataframe(conflicts)
        
    st.subheader("Volume par Département")
    dept_stats = run_query("""
        SELECT d.nom, COUNT(e.id) as examens_planifies
        FROM departements d
        JOIN formations f ON f.dept_id = d.id
        JOIN modules m ON m.formation_id = f.id
        LEFT JOIN examens e ON e.module_id = m.id
        GROUP BY d.nom
    """)
    st.bar_chart(dept_stats.set_index('nom'))