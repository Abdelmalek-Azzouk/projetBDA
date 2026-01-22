import streamlit as st
from views import doyen, admin, chef, student_prof
import os
import sqlite3

ACCOUNTS_DB = os.path.join("data", "accounts.db")

st.set_page_config(page_title="POETEU - Planning Examens", layout="wide", page_icon=None)

st.sidebar.title("ProjetBDA")
st.sidebar.markdown("*Plateforme d'Optimisation des Emplois du Temps*")
st.sidebar.markdown("---")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["rolepage"] = ""

def rerun():
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

ROLE_TABLES = {
    "doyen": ("doyen", "Vice-Doyen / Doyen"),
    "examgestionnaire": ("examgestionnaire", "Administrateur (Planif)"),
    "chef": ("chef", "Chef de Département"),
    "teacher": ("teacher", "Étudiant / Prof"),
    "student": ("student", "Étudiant / Prof"),
}
PAGE_TO_ROLE = {v[1]: k for k, v in ROLE_TABLES.items()}

def get_account_from_db(username):
    conn = sqlite3.connect(ACCOUNTS_DB)
    c = conn.cursor()
    for role, (table, page) in ROLE_TABLES.items():
        c.execute(f"SELECT username, password FROM {table} WHERE username=?", (username,))
        row = c.fetchone()
        if row:
            conn.close()
            return (role, row[0], row[1], page)
    conn.close()
    return None

def login_area():
    st.sidebar.subheader("Connexion Utilisateur")
    username = st.sidebar.text_input("Nom d'utilisateur", key="login_user")
    password = st.sidebar.text_input("Mot de passe", type="password", key="login_pass")
    login_btn = st.sidebar.button("Se connecter", type="primary", key="login_btn")
    error = ""
    if login_btn:
        res = get_account_from_db(username)
        if res and password == res[2]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["rolepage"] = res[3]
            import streamlit
            if hasattr(streamlit, 'rerun'):
                streamlit.rerun()
            else:
                rerun()
        else:
            error = "Identifiant ou mot de passe incorrect. Vérifiez vos informations."
    if not st.session_state["authenticated"] and error:
        st.sidebar.error(error)

def logout_area():
    st.sidebar.write(f"Utilisateur : `{st.session_state['username']}`")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["rolepage"] = ""
        import streamlit
        if hasattr(streamlit, 'rerun'):
            streamlit.rerun()
        else:
            rerun()

st.sidebar.markdown("---")
st.sidebar.info("Bases de données : Connectées")

if not st.session_state["authenticated"]:
    login_area()
    st.stop()
else:
    logout_area()
    page = st.session_state["rolepage"]
    if page == "Vice-Doyen / Doyen":
        doyen.show()
    elif page == "Administrateur (Planif)":
        admin.show()
    elif page == "Chef de Département":
        chef.show()
    elif page == "Étudiant / Prof":
        student_prof.show()