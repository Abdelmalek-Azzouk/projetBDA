import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import init_db, get_connection
from faker import Faker
import random

fake = Faker('fr_FR')

def random_password(length=8):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_dataset():
    print("Initializing Database...")
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO doyens (id, nom, role, username, password) VALUES
        (1, 'Default Doyen', 'Doyen', 'doyen', 'doyenpw')
        ON CONFLICT(id) DO NOTHING
    """)
    cur.execute("""
        INSERT INTO gestionnaire (id, nom, username, password) VALUES
        (1, 'Gestionnaire Principal', 'gest', 'gestpw')
        ON CONFLICT(id) DO NOTHING
    """)
    cur.execute("""
        INSERT INTO professeurs (id, nom, dept_id, username, password)
        VALUES (1, 'Professeur Principal', 1, 'teacher', 'teacherpw')
        ON CONFLICT(id) DO NOTHING
    """)
    temp_form_id = 1
    cur.execute("""
        INSERT INTO etudiants (id, nom, prenom, formation_id, username, password)
        VALUES (1, 'EtudiantPrincipal', 'Test', ?, 'student', 'studentpw')
        ON CONFLICT(id) DO NOTHING
    """, (temp_form_id,))

    print("Generating Departments & Rooms...")
    depts = ['Informatique', 'Biologie', 'Droit', 'Économie', 'Mécanique', 'Génie Civil', 'Anglais']
    for i, d in enumerate(depts):
        if i == 0:
            chefuser = 'chef'
            chefpassword = 'chefpw'
        else:
            chefuser = f'chef{i+1}'
            chefpassword = random_password()
        cur.execute(
            "INSERT INTO departements (id, nom, chefuser, chefpassword) VALUES (?, ?, ?, ?)",
            (i + 1, d, chefuser, chefpassword))

    for i in range(1, 11):
        cur.execute("INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", (f"Amphi {i}", random.choice([200, 300, 400]), 'AMPHI'))
    for i in range(1, 51):
        cur.execute("INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", (f"Salle {i}", 20, 'SALLE'))

    print("Generating Formations, Modules & Profs...")
    form_id_counter = 1
    mod_id_counter = 1
    prof_id_counter = 2
    formations_list = []
    prof_usernames_set = set(['teacher'])
    for dept_id in range(1, 8):
        for j in range(30):
            while True:
                uname = f"prof{dept_id}_{j+1}"
                if uname not in prof_usernames_set:
                    prof_usernames_set.add(uname)
                    break
            passwd = random_password()
            cur.execute(
                "INSERT INTO professeurs (id, nom, dept_id, username, password) VALUES (?, ?, ?, ?, ?)", 
                (prof_id_counter, fake.name(), dept_id, uname, passwd)
            )
            prof_id_counter += 1
        for _ in range(30):
            f_name = f"Licence {fake.word()} - {fake.word()}"
            cur.execute("INSERT INTO formations (id, nom, dept_id) VALUES (?, ?, ?)", (form_id_counter, f_name, dept_id))
            for m in range(6):
                mod_name = f"Module {fake.job()} {m+1}"
                cur.execute("INSERT INTO modules (id, nom, formation_id) VALUES (?, ?, ?)", (mod_id_counter, mod_name, form_id_counter))
                mod_id_counter += 1
            formations_list.append(form_id_counter)
            form_id_counter += 1

    if formations_list:
        real_first_form = formations_list[0]
        cur.execute("UPDATE etudiants SET formation_id = ? WHERE id = 1", (real_first_form,))

    print("Generating Students & Inscriptions (Heavy Step - ~13k students)...")
    student_id = 2
    inscriptions = []
    student_usernames_set = set(['student'])
    for _ in range(13000):
        fmt_id = random.choice(formations_list)
        while True:
            uname = f"etu{student_id:05d}"
            if uname not in student_usernames_set:
                student_usernames_set.add(uname)
                break
        passwd = random_password()
        cur.execute(
            "INSERT INTO etudiants (id, nom, prenom, formation_id, username, password) VALUES (?, ?, ?, ?, ?, ?)", 
            (student_id, fake.last_name(), fake.first_name(), fmt_id, uname, passwd)
        )
        cur.execute("SELECT id FROM modules WHERE formation_id = ?", (fmt_id,))
        mods = [row[0] for row in cur.fetchall()]
        for m_id in mods:
            inscriptions.append((student_id, m_id))
        student_id += 1
        if student_id % 1000 == 0:
            print(f"  > {student_id} students created...")

    cur.execute("SELECT id FROM modules WHERE formation_id = ?", (real_first_form,))
    mods = [row[0] for row in cur.fetchall()]
    for m_id in mods:
        inscriptions.append((1, m_id))

    print("Inserting 130k+ Inscriptions...")
    cur.executemany("INSERT INTO inscriptions (etudiant_id, module_id) VALUES (?, ?)", inscriptions)

    print("Generating Examens & Surveillances...")
    import datetime
    cur.execute('SELECT id FROM modules')
    all_module_ids = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT id FROM salles WHERE type="AMPHI"')
    amphi_ids = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT id FROM salles WHERE type="SALLE"')
    salle_ids = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT id FROM professeurs')
    all_prof_ids = [row[0] for row in cur.fetchall()]

    exam_dates = [datetime.date.today() + datetime.timedelta(days=delta) for delta in range(10)]
    exam_hours = ['08:30', '10:45', '13:30', '16:00']
    exam_rows = []
    surveillances_rows = []
    exam_id_counter = 1
    random.shuffle(all_module_ids)
    exam_idx = 0
    for day in exam_dates:
        for time in exam_hours:
            for _ in range(5):
                if exam_idx >= len(all_module_ids):
                    break
                mid = all_module_ids[exam_idx]
                salle_id = random.choice(amphi_ids + salle_ids)
                duree = random.choice([90, 120, 180])
                exam_rows.append((exam_id_counter, mid, salle_id, str(day), time, duree))
                profs = random.sample(all_prof_ids, 2)
                for pid in profs:
                    surveillances_rows.append((exam_id_counter, pid))
                exam_id_counter += 1
                exam_idx += 1
    cur.executemany("INSERT INTO examens (id, module_id, salle_id, date_examen, heure_debut, duree_minutes) VALUES (?, ?, ?, ?, ?, ?)", exam_rows)
    cur.executemany("INSERT INTO surveillances (examen_id, prof_id) VALUES (?, ?)", surveillances_rows)

    conn.commit()
    conn.close()
    print("Dataset Generation Complete!")

if __name__ == "__main__":
    generate_dataset()