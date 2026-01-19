import pandas as pd
import numpy as np
from database.db_manager import get_connection

def generate_schedule(start_date, num_days):
    
    conn = get_connection()
    print("Fetching data...")

    sql_modules = """
        SELECT m.id, m.nom, m.formation_id, COUNT(i.etudiant_id) as n_students
        FROM modules m
        JOIN inscriptions i ON m.id = i.module_id
        GROUP BY m.id
        ORDER BY n_students DESC
    """
    modules_df = pd.read_sql(sql_modules, conn)

    rooms_df = pd.read_sql("SELECT * FROM salles ORDER BY capacite DESC", conn)
    all_rooms = rooms_df.to_dict('records')
    
    dates = pd.date_range(start=start_date, periods=num_days)
    times = ['08:30', '11:00', '13:30', '16:00']
    
    room_occupancy = {} 
    daily_student_load = {str(d.date()): set() for d in dates}
    
    assignments = []
    modules_scheduled_count = 0
    
    print(f"Splitting {len(modules_df)} exams across available rooms...")

    for _, mod in modules_df.iterrows():
        is_scheduled = False
        students_needed = mod['n_students']
        studs = pd.read_sql(f"SELECT etudiant_id FROM inscriptions WHERE module_id={mod['id']}", conn)
        studs_set = set(studs['etudiant_id'].tolist())

        for d in dates:
            if is_scheduled:
                break
            date_str = str(d.date())
            if len(studs_set.intersection(daily_student_load[date_str])) > 0:
                continue 
            for t in times:
                if is_scheduled:
                    break
                free_rooms_at_slot = []
                for room in all_rooms:
                    if not room_occupancy.get((date_str, t, room['id']), False):
                        free_rooms_at_slot.append(room)
                total_free_cap = sum(r['capacite'] for r in free_rooms_at_slot)
                if total_free_cap >= students_needed:
                    selected_rooms = []
                    current_cap = 0
                    for room in free_rooms_at_slot:
                        selected_rooms.append(room)
                        current_cap += room['capacite']
                        if current_cap >= students_needed:
                            break
                    for r in selected_rooms:
                        assignments.append({
                            'module_id': mod['id'],
                            'room_id': r['id'],
                            'date': date_str,
                            'time': t
                        })
                        room_occupancy[(date_str, t, r['id'])] = True
                    daily_student_load[date_str].update(studs_set)
                    is_scheduled = True
                    modules_scheduled_count += 1
        if not is_scheduled:
            print(f"⚠️ Could not find enough rooms for Module {mod['nom']}")

    print(f"Scheduled {modules_scheduled_count} exams using {len(assignments)} rooms.")
    cur = conn.cursor()
    cur.execute("DELETE FROM examens")
    cur.execute("DELETE FROM surveillances")
    
    data_to_insert = [(x['module_id'], x['room_id'], x['date'], x['time']) for x in assignments]
    cur.executemany("INSERT INTO examens (module_id, salle_id, date_examen, heure_debut) VALUES (?, ?, ?, ?)", data_to_insert)
    
    conn.commit()
    profs = pd.read_sql("SELECT id FROM professeurs", conn)['id'].tolist()
    exam_ids = pd.read_sql("SELECT id FROM examens", conn)['id'].tolist()
    
    import itertools
    prof_cycle = itertools.cycle(profs)
    
    surv_data = []
    for eid in exam_ids:
        surv_data.append((eid, next(prof_cycle)))
        
    cur.executemany("INSERT INTO surveillances (examen_id, prof_id) VALUES (?, ?)", surv_data)
    
    conn.commit()
    conn.close()
    
    return modules_scheduled_count, len(assignments), len(modules_df)