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
DROP TABLE IF EXISTS doyens;
DROP TABLE IF EXISTS gestionnaire;

-- 0. Admin Tables

CREATE TABLE doyens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    role TEXT CHECK(role IN ('Doyen', 'Vice-Doyen')) NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- 5 example doyens, 5 vice-doyens, first doyen = doyen/doyenpw
INSERT INTO doyens (nom, role, username, password) VALUES
    ('Jean Martin', 'Doyen', 'doyen', 'doyenpw'),
    ('Paul Dubois', 'Doyen', 'doyen2', 'doyen2pw'),
    ('Claire Durand', 'Doyen', 'doyen3', 'doyen3pw'),
    ('Yves Petit', 'Doyen', 'doyen4', 'doyen4pw'),
    ('Elise Bernard', 'Doyen', 'doyen5', 'doyen5pw'),
    ('Sophie Lefevre', 'Vice-Doyen', 'vicedoyen1', 'vicedoyen1pw'),
    ('Antoine Leroy', 'Vice-Doyen', 'vicedoyen2', 'vicedoyen2pw'),
    ('Marie Simon', 'Vice-Doyen', 'vicedoyen3', 'vicedoyen3pw'),
    ('Luc Girard', 'Vice-Doyen', 'vicedoyen4', 'vicedoyen4pw'),
    ('Nathalie Moulin', 'Vice-Doyen', 'vicedoyen5', 'vicedoyen5pw');

CREATE TABLE gestionnaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- First gestionnaire is gest/gestpw
INSERT INTO gestionnaire (nom, username, password) VALUES
    ('Gestionnaire Principal', 'gest', 'gestpw');

-- 1. Infrastructure
CREATE TABLE departements (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    chefuser TEXT,
    chefpassword TEXT
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
    username TEXT,
    password TEXT,
    FOREIGN KEY(dept_id) REFERENCES departements(id)
);

CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY,
    nom TEXT,
    prenom TEXT,
    formation_id INTEGER,
    username TEXT,
    password TEXT,
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

-- Exemple d'insertion pour chefuser/chefpassword département Informatique :
-- INSERT INTO departements (id, nom, chefuser, chefpassword) VALUES (1, 'Informatique', 'chef', 'chefpw');
-- Pour les autres départements, chefuser/chefpassword peuvent être NULL ou quelconques.
