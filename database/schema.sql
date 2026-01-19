-- Clean up
DROP TABLE IF EXISTS surveillances;
DROP TABLE IF EXISTS examens;
DROP TABLE IF EXISTS inscriptions;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS etudiants;
DROP TABLE IF EXISTS professeurs;
DROP TABLE IF EXISTS salles;
DROP TABLE IF EXISTS formations;
DROP TABLE IF EXISTS departements;

-- 1. Infrastructure
CREATE TABLE departements (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL
);

CREATE TABLE salles (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    capacite INTEGER NOT NULL,
    type TEXT CHECK(type IN ('AMPHI', 'SALLE')), -- AMPHI or SALLE
    batiment TEXT
);

-- 2. Academics
CREATE TABLE formations (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    dept_id INTEGER,
    FOREIGN KEY(dept_id) REFERENCES departements(id)
);

CREATE TABLE modules (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    formation_id INTEGER,
    FOREIGN KEY(formation_id) REFERENCES formations(id)
);

CREATE TABLE professeurs (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    dept_id INTEGER,
    FOREIGN KEY(dept_id) REFERENCES departements(id)
);

CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    prenom TEXT,
    formation_id INTEGER,
    promo TEXT, -- e.g., 'L1', 'M1'
    FOREIGN KEY(formation_id) REFERENCES formations(id)
);

-- 3. Relationships
CREATE TABLE inscriptions (
    etudiant_id INTEGER,
    module_id INTEGER,
    PRIMARY KEY (etudiant_id, module_id),
    FOREIGN KEY(etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY(module_id) REFERENCES modules(id)
);

-- 4. Scheduling (Output Tables)
CREATE TABLE examens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER,
    salle_id INTEGER,
    date_examen DATE,
    heure_debut TIME, -- e.g., '08:30'
    duree_minutes INTEGER DEFAULT 90,
    FOREIGN KEY(module_id) REFERENCES modules(id),
    FOREIGN KEY(salle_id) REFERENCES salles(id)
);

CREATE TABLE surveillances (
    examen_id INTEGER,
    prof_id INTEGER,
    PRIMARY KEY(examen_id, prof_id),
    FOREIGN KEY(examen_id) REFERENCES examens(id),
    FOREIGN KEY(prof_id) REFERENCES professeurs(id)
);

-- 5. Optimization Indices (Crucial for performance)
CREATE INDEX idx_insc_module ON inscriptions(module_id);
CREATE INDEX idx_insc_etud ON inscriptions(etudiant_id);
CREATE INDEX idx_exam_date ON examens(date_examen);