import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "school_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_SCHEMA = os.getenv("DB_SCHEMA", "scolarite")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def read_csv(file_name: str) -> pd.DataFrame:
    path = DATA_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    return pd.read_csv(path, sep="|").apply(lambda col: col.str.strip() if col.dtype == "object" else col)


def create_schema_and_tables(engine) -> None:
    schema_path = SQL_DIR / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Schéma et tables créés avec succès.")


def prepare_data():
    enseignant = read_csv("TB_ENSEIGNANT.csv")
    etudiant = read_csv("TB_ETUDIANT.csv")
    type_matiere = read_csv("TB_TYPE_MATIERE.csv")
    type_evaluation = read_csv("TB_TYPE_EVALUATION.csv")
    matiere = read_csv("TB_MATIERE.csv")
    note = read_csv("TB_NOTE.csv")

    # Harmonisation des types
    etudiant["CD_POSTAL_ETUDIANT"] = etudiant["CD_POSTAL_ETUDIANT"].astype(str)
    matiere["NB_COEF"] = pd.to_numeric(matiere["NB_COEF"], errors="raise").astype(int)
    note["ANNEE_SCOLAIRE"] = pd.to_numeric(note["ANNEE_SCOLAIRE"], errors="raise").astype(int)
    note["NB_NOTE"] = pd.to_numeric(note["NB_NOTE"], errors="raise")
    note["DT_NOTE"] = pd.to_datetime(note["DT_NOTE"], format="%d/%m/%Y", errors="raise").dt.date

    return {
        "enseignant": enseignant,
        "etudiant": etudiant,
        "type_matiere": type_matiere,
        "type_evaluation": type_evaluation,
        "matiere": matiere,
        "note": note,
    }


def validate_data(data: dict) -> None:
    assert data["enseignant"]["ID_ENSEIGNANT"].is_unique, "Doublons dans enseignant"
    assert data["etudiant"]["ID_ETUDIANT"].is_unique, "Doublons dans etudiant"
    assert data["type_matiere"]["CD_TYPE_MATIERE"].is_unique, "Doublons dans type_matiere"
    assert data["type_evaluation"]["CD_TYPE_EVALUATION"].is_unique, "Doublons dans type_evaluation"
    assert data["matiere"]["CD_MATIERE"].is_unique, "Doublons dans matiere"

    duplicate_note = data["note"].duplicated(
        subset=["ID_ETUDIANT", "CD_MATIERE", "CD_TYPE_EVALUATION", "ANNEE_SCOLAIRE"]
    ).any()
    assert not duplicate_note, "Doublons dans la clé primaire composite de note"

    fk_matiere_enseignant = set(data["matiere"]["ID_ENSEIGNANT"]) - set(data["enseignant"]["ID_ENSEIGNANT"])
    fk_matiere_type = set(data["matiere"]["CD_TYPE_MATIERE"]) - set(data["type_matiere"]["CD_TYPE_MATIERE"])
    fk_note_etudiant = set(data["note"]["ID_ETUDIANT"]) - set(data["etudiant"]["ID_ETUDIANT"])
    fk_note_matiere = set(data["note"]["CD_MATIERE"]) - set(data["matiere"]["CD_MATIERE"])
    fk_note_eval = set(data["note"]["CD_TYPE_EVALUATION"]) - set(data["type_evaluation"]["CD_TYPE_EVALUATION"])

    assert not fk_matiere_enseignant, f"Références enseignant manquantes: {fk_matiere_enseignant}"
    assert not fk_matiere_type, f"Références type_matiere manquantes: {fk_matiere_type}"
    assert not fk_note_etudiant, f"Références etudiant manquantes: {fk_note_etudiant}"
    assert not fk_note_matiere, f"Références matiere manquantes: {fk_note_matiere}"
    assert not fk_note_eval, f"Références type_evaluation manquantes: {fk_note_eval}"

    print("Validation terminée avec succès.")


def truncate_tables(engine) -> None:
    order = [
        "note",
        "matiere",
        "type_evaluation",
        "type_matiere",
        "etudiant",
        "enseignant",
    ]
    with engine.begin() as conn:
        for table in order:
            conn.execute(text(f"TRUNCATE TABLE {DB_SCHEMA}.{table} CASCADE;"))
    print("Tables vidées.")


def load_tables(engine, data: dict) -> None:
    mapping = {
        "enseignant": ("enseignant", {
            "ID_ENSEIGNANT": "id_enseignant",
            "NOM_ENSEIGNANT": "nom_enseignant",
            "PREN_ENSEIGNANT": "pren_enseignant",
            "EMAIL_ENSEIGNANT": "email_enseignant",
        }),
        "etudiant": ("etudiant", {
            "ID_ETUDIANT": "id_etudiant",
            "CIVILITE_ETUDIANT": "civilite_etudiant",
            "NOM_ETUDIANT": "nom_etudiant",
            "PREN_ETUDIANT": "pren_etudiant",
            "CD_POSTAL_ETUDIANT": "cd_postal_etudiant",
            "VILLE_ETUDIANT": "ville_etudiant",
        }),
        "type_matiere": ("type_matiere", {
            "CD_TYPE_MATIERE": "cd_type_matiere",
            "LB_TYPE_MATIERE": "lb_type_matiere",
        }),
        "type_evaluation": ("type_evaluation", {
            "CD_TYPE_EVALUATION": "cd_type_evaluation",
            "LB_TYPE_EVALUATION": "lb_type_evaluation",
        }),
        "matiere": ("matiere", {
            "CD_MATIERE": "cd_matiere",
            "LB_MATIERE": "lb_matiere",
            "NB_COEF": "nb_coef",
            "CD_TYPE_MATIERE": "cd_type_matiere",
            "ID_ENSEIGNANT": "id_enseignant",
        }),
        "note": ("note", {
            "ID_ETUDIANT": "id_etudiant",
            "CD_MATIERE": "cd_matiere",
            "CD_TYPE_EVALUATION": "cd_type_evaluation",
            "ANNEE_SCOLAIRE": "annee_scolaire",
            "DT_NOTE": "dt_note",
            "NB_NOTE": "nb_note",
        }),
    }

    load_order = ["enseignant", "etudiant", "type_matiere", "type_evaluation", "matiere", "note"]

    for key in load_order:
        table_name, rename_map = mapping[key]
        df = data[key].rename(columns=rename_map)
        df.to_sql(
            name=table_name,
            con=engine,
            schema=DB_SCHEMA,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )
        print(f"Table chargée : {DB_SCHEMA}.{table_name} ({len(df)} lignes)")


def run_quality_checks(engine) -> None:
    queries = {
        "enseignant": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.enseignant",
        "etudiant": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.etudiant",
        "matiere": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.matiere",
        "type_matiere": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.type_matiere",
        "type_evaluation": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.type_evaluation",
        "note": f"SELECT COUNT(*) AS n FROM {DB_SCHEMA}.note",
    }
    with engine.connect() as conn:
        for name, sql in queries.items():
            n = conn.execute(text(sql)).scalar()
            print(f"{name}: {n} lignes")


def main() -> None:
    engine = create_engine(DATABASE_URL, future=True)

    print("Connexion à PostgreSQL...")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("Connexion réussie.")

    create_schema_and_tables(engine)
    data = prepare_data()
    validate_data(data)
    truncate_tables(engine)
    load_tables(engine, data)
    run_quality_checks(engine)

    print("Chargement terminé avec succès.")


if __name__ == "__main__":
    main()