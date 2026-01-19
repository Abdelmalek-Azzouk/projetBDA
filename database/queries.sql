-- This file contains analytical queries used in the Dashboard

-- 1. DETECT STUDENT CONFLICTS (Etudiants avec > 1 examen par jour)
-- Used in: Dashboard -> Analyse des Conflits
SELECT 
    e.date_examen, 
    i.etudiant_id, 
    et.nom, 
    et.prenom,
    COUNT(*) as nombre_examens
FROM examens e
JOIN inscriptions i ON e.module_id = i.module_id
JOIN etudiants et ON i.etudiant_id = et.id
GROUP BY e.date_examen, i.etudiant_id
HAVING nombre_examens > 1;

-- 2. TEACHER WORKLOAD (Charge horaire des surveillances)
-- Used in: Dashboard -> Équité Professeurs
SELECT 
    p.nom, 
    p.dept_id,
    COUNT(s.examen_id) as nb_surveillances,
    SUM(e.duree_minutes) / 60.0 as heures_totales
FROM professeurs p
LEFT JOIN surveillances s ON p.id = s.prof_id
LEFT JOIN examens e ON s.examen_id = e.id
GROUP BY p.id
ORDER BY nb_surveillances DESC;

-- 3. ROOM OCCUPATION RATE (Taux d'occupation des salles)
-- Used in: Dashboard -> Gestion des Salles
SELECT 
    s.nom,
    s.capacite,
    COUNT(e.id) as examens_accueillis,
    ROUND(AVG(
        (SELECT COUNT(*) FROM inscriptions i WHERE i.module_id = e.module_id) * 100.0 / s.capacite
    ), 2) as taux_remplissage_moyen
FROM salles s
LEFT JOIN examens e ON s.id = e.salle_id
GROUP BY s.id
ORDER BY examens_accueillis DESC;

-- 4. DEPARTMENT CONFLICT RATE
-- Calculates how many exams overlap within the same department at the same time
SELECT 
    d.nom as departement,
    e.date_examen,
    e.heure_debut,
    COUNT(*) as examens_simultanes
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
GROUP BY d.nom, e.date_examen, e.heure_debut
HAVING examens_simultanes > 1;