import streamlit as st
from database.db_manager import run_query

def show():
    st.header("Espace Étudiant & Professeur")
    
    tab1, tab2 = st.tabs(["Étudiant", "Professeur"])
    
    with tab1:
        st.subheader("Mon Emploi du Temps")
        student_id = st.number_input("Entrez votre ID Étudiant", min_value=0, step=1, value=0, format="%d")
        
        if student_id > 0:
            sql = """
                SELECT e.date_examen, e.heure_debut, m.nom as Module, s.nom as Lieu
                FROM etudiants et
                JOIN inscriptions i ON et.id = i.etudiant_id
                JOIN examens e ON i.module_id = e.module_id
                JOIN modules m ON m.id = e.module_id
                JOIN salles s ON s.id = e.salle_id
                WHERE et.id = ?
                ORDER BY e.date_examen
            """
            df = run_query(sql, (student_id,))
            if not df.empty:
                df = df.drop_duplicates(subset=["date_examen", "heure_debut", "Module", "Lieu"])
                st.table(df)
            else:
                st.warning(f"Aucun résultat trouvé pour l'ID {student_id}.")

    with tab2:
        st.subheader("Mes Surveillances")
        prof_id = st.number_input("Entrez votre ID Professeur", min_value=0, step=1, value=0, format="%d")
        
        if prof_id > 0:
            sql = """
                SELECT e.date_examen, e.heure_debut, m.nom as Module, s.nom as Lieu
                FROM professeurs p
                JOIN surveillances surv ON p.id = surv.prof_id
                JOIN examens e ON surv.examen_id = e.id
                JOIN modules m ON m.id = e.module_id
                JOIN salles s ON s.id = e.salle_id
                WHERE p.id = ?
                ORDER BY e.date_examen
            """
            df = run_query(sql, (prof_id,))
            if not df.empty:
                df = df.drop_duplicates(subset=["date_examen", "heure_debut", "Module", "Lieu"])
                st.table(df)
            else:
                st.warning(f"Aucun planning trouvé pour l'ID {prof_id}.")
