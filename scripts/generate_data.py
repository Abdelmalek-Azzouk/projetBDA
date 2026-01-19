import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import init_db, get_connection
from faker import Faker
import random

fake = Faker('fr_FR')

def generate_dataset():
    print("Initializing Database...")
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    print("Generating Departments & Rooms...")
    depts = ['Informatique', 'Biologie', 'Droit', 'Économie', 'Mécanique', 'Génie Civil', 'Anglais']
    for i, d in enumerate(depts):
        cur.execute("INSERT INTO departements (id, nom) VALUES (?, ?)", (i+1, d))

    # Rooms (10 Amphis, 50 Salles)
    for i in range(1, 11):
        cur.execute("INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", (f"Amphi {i}", random.choice([200, 300, 400]), 'AMPHI'))
    for i in range(1, 51):
        cur.execute("INSERT INTO salles (nom, capacite, type) VALUES (?, ?, ?)", (f"Salle {i}", 20, 'SALLE'))

    print("Generating Formations, Modules & Profs...")
    form_id_counter = 1
    mod_id_counter = 1
    prof_id_counter = 1
    
    formations_list = []
    
    for dept_id in range(1, 8):
        # 30 Professors per dept
        for _ in range(30):
            cur.execute("INSERT INTO professeurs (id, nom, dept_id) VALUES (?, ?, ?)", 
                        (prof_id_counter, fake.name(), dept_id))
            prof_id_counter += 1
            
        # ~30 Formations per dept
        for _ in range(30):
            f_name = f"Licence {fake.word()} - {fake.word()}"
            cur.execute("INSERT INTO formations (id, nom, dept_id) VALUES (?, ?, ?)", (form_id_counter, f_name, dept_id))
            
            # 6 Modules per formation
            for m in range(6):
                mod_name = f"Module {fake.job()} {m+1}"
                cur.execute("INSERT INTO modules (id, nom, formation_id) VALUES (?, ?, ?)", (mod_id_counter, mod_name, form_id_counter))
                mod_id_counter += 1
            
            formations_list.append(form_id_counter)
            form_id_counter += 1

    print("Generating Students & Inscriptions (Heavy Step - ~13k students)...")
    student_id = 1
    inscriptions = []
    
    # 13,000 Students
    for _ in range(13000):
        fmt_id = random.choice(formations_list)
        cur.execute("INSERT INTO etudiants (id, nom, prenom, formation_id, promo) VALUES (?, ?, ?, ?, ?)", 
                    (student_id, fake.last_name(), fake.first_name(), fmt_id, '2024'))
        
        # Get modules for this formation
        cur.execute("SELECT id FROM modules WHERE formation_id = ?", (fmt_id,))
        mods = [row[0] for row in cur.fetchall()]
        
        for m_id in mods:
            inscriptions.append((student_id, m_id))
        
        student_id += 1
        if student_id % 1000 == 0:
            print(f"  > {student_id} students created...")

    print("Inserting 130k+ Inscriptions...")
    cur.executemany("INSERT INTO inscriptions (etudiant_id, module_id) VALUES (?, ?)", inscriptions)
    
    conn.commit()
    conn.close()
    print("Dataset Generation Complete!")

if __name__ == "__main__":
    generate_dataset()