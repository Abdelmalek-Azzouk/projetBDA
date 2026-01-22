import streamlit as st
from views import doyen, admin, chef, student_prof
import os
import sqlite3

# Use university.db instead of accounts.db
ACCOUNTS_DB = os.path.join("data", "university.db")

st.set_page_config(page_title="POETEU - Planning Examens", layout="wide", page_icon=None)

st.sidebar.title("ProjetBDA")
st.sidebar.markdown("*Plateforme d'Optimisation des Emplois du Temps*")
st.sidebar.markdown("---")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["rolepage"] = ""
    st.session_state["user_id"] = None  # will hold the id

def rerun():
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

# Mapping of roles to their (table, page label)
ROLE_TABLES = {
    "doyen": ("doyens", "Vice-Doyen / Doyen"),
    "examgestionnaire": ("gestionnaire", "Administrateur (Planif)"),
    "chef": ("departements", "Chef de Département"),
    "teacher": ("professeurs", "Étudiant / Prof"),
    "student": ("etudiants", "Étudiant / Prof"),
}
PAGE_TO_ROLE = {v[1]: k for k, v in ROLE_TABLES.items()}

def get_account_from_db(username):
    """
    Return (role, username, password, page, id)
    For 'chef', check departements with chefuser/chefpassword (special case for password).
    For each other: look up in their respective table.
    """
    conn = sqlite3.connect(ACCOUNTS_DB)
    c = conn.cursor()
    for role, (table, page) in ROLE_TABLES.items():
        if role == "chef":
            # For chef, username is chefuser
            c.execute(f"SELECT id, chefuser, chefpassword FROM departements WHERE chefuser = ?", (username,))
            row = c.fetchone()
            if row:
                conn.close()
                return (role, row[1], row[2], page, row[0])
        else:
            if role == "doyen":
                c.execute(f"SELECT id, username, password FROM doyens WHERE username = ?", (username,))
            elif role == "examgestionnaire":
                c.execute(f"SELECT id, username, password FROM gestionnaire WHERE username = ?", (username,))
            elif role == "teacher":
                c.execute(f"SELECT id, username, password FROM professeurs WHERE username = ?", (username,))
            elif role == "student":
                c.execute(f"SELECT id, username, password FROM etudiants WHERE username = ?", (username,))
            else:
                continue
            row = c.fetchone()
            if row:
                conn.close()
                return (role, row[1], row[2], page, row[0])
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
        if res:
            role, _, correct_password, page, user_id = res
            # For chef, match chefpassword, for others: password
            if role == "chef":
                if password == correct_password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["rolepage"] = page
                    st.session_state["user_id"] = user_id
                    import streamlit
                    if hasattr(streamlit, 'rerun'):
                        streamlit.rerun()
                    else:
                        rerun()
                else:
                    error = "Identifiant ou mot de passe incorrect. Vérifiez vos informations."
            else:
                if password == correct_password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["rolepage"] = page
                    st.session_state["user_id"] = user_id
                    import streamlit
                    if hasattr(streamlit, 'rerun'):
                        streamlit.rerun()
                    else:
                        rerun()
                else:
                    error = "Identifiant ou mot de passe incorrect. Vérifiez vos informations."
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
        st.session_state["user_id"] = None  # clear it
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