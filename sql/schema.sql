CREATE SCHEMA IF NOT EXISTS scolarite;

CREATE TABLE IF NOT EXISTS scolarite.enseignant (
    id_enseignant VARCHAR(10) PRIMARY KEY,
    nom_enseignant VARCHAR(100) NOT NULL,
    pren_enseignant VARCHAR(100) NOT NULL,
    email_enseignant VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS scolarite.etudiant (
    id_etudiant VARCHAR(10) PRIMARY KEY,
    civilite_etudiant VARCHAR(20) NOT NULL,
    nom_etudiant VARCHAR(100) NOT NULL,
    pren_etudiant VARCHAR(100) NOT NULL,
    cd_postal_etudiant VARCHAR(20) NOT NULL,
    ville_etudiant VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS scolarite.type_matiere (
    cd_type_matiere VARCHAR(10) PRIMARY KEY,
    lb_type_matiere VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS scolarite.type_evaluation (
    cd_type_evaluation VARCHAR(10) PRIMARY KEY,
    lb_type_evaluation VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS scolarite.matiere (
    cd_matiere VARCHAR(10) PRIMARY KEY,
    lb_matiere VARCHAR(150) NOT NULL,
    nb_coef INTEGER NOT NULL CHECK (nb_coef > 0),
    cd_type_matiere VARCHAR(10) NOT NULL,
    id_enseignant VARCHAR(10) NOT NULL,
    CONSTRAINT fk_matiere_type
        FOREIGN KEY (cd_type_matiere)
        REFERENCES scolarite.type_matiere (cd_type_matiere),
    CONSTRAINT fk_matiere_enseignant
        FOREIGN KEY (id_enseignant)
        REFERENCES scolarite.enseignant (id_enseignant)
);

CREATE TABLE IF NOT EXISTS scolarite.note (
    id_etudiant VARCHAR(10) NOT NULL,
    cd_matiere VARCHAR(10) NOT NULL,
    cd_type_evaluation VARCHAR(10) NOT NULL,
    annee_scolaire INTEGER NOT NULL,
    dt_note DATE NOT NULL,
    nb_note NUMERIC(5,2) NOT NULL CHECK (nb_note >= 0 AND nb_note <= 20),
    CONSTRAINT pk_note PRIMARY KEY (
        id_etudiant,
        cd_matiere,
        cd_type_evaluation,
        annee_scolaire
    ),
    CONSTRAINT fk_note_etudiant
        FOREIGN KEY (id_etudiant)
        REFERENCES scolarite.etudiant (id_etudiant),
    CONSTRAINT fk_note_matiere
        FOREIGN KEY (cd_matiere)
        REFERENCES scolarite.matiere (cd_matiere),
    CONSTRAINT fk_note_type_evaluation
        FOREIGN KEY (cd_type_evaluation)
        REFERENCES scolarite.type_evaluation (cd_type_evaluation)
);

CREATE INDEX IF NOT EXISTS idx_note_etudiant ON scolarite.note(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_note_matiere ON scolarite.note(cd_matiere);
CREATE INDEX IF NOT EXISTS idx_note_type_eval ON scolarite.note(cd_type_evaluation);