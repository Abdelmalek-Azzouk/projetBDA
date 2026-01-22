import streamlit as st
from database.db_manager import run_query, is_edt_validated

def show():
    st.header("📅 Espace Étudiant & Professeur")
    
    if not is_edt_validated():
        st.info("**Les emplois du temps sont en cours d'élaboration.**")
        st.warning("La consultation sera ouverte une fois les plannings validés par le Doyen.")
        return

    user_id = st.session_state.get("user_id", None)
    username = st.session_state.get("username", "")
    if user_id is None:
        st.error("Utilisateur non identifié, impossible d'afficher le planning.")
        return

    role_hint = None
    student_res = run_query("SELECT id FROM etudiants WHERE id = ?", (user_id,))
    if not student_res.empty:
        role_hint = "student"
    else:
        teacher_res = run_query("SELECT id FROM professeurs WHERE id = ?", (user_id,))
        if not teacher_res.empty:
            role_hint = "teacher"

    if role_hint == "student":
        st.subheader("Mon Emploi du Temps (Étudiant)")
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
        df = run_query(sql, (user_id,))
        if not df.empty:
            st.table(df)
        else:
            st.warning("Aucun examen planifié pour votre identifiant.")

    elif role_hint == "teacher":
        st.subheader("Mes Surveillances (Professeur)")
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
        df = run_query(sql, (user_id,))
        if not df.empty:
            st.table(df)
        else:
            st.warning("Aucune surveillance planifiée pour votre identifiant.")
    else:
        st.error("Impossible de déterminer votre type d'utilisateur (étudiant ou professeur). Contactez l'administrateur.")