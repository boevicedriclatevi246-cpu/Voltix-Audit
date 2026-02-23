"""
Gestionnaire de base de données - Support SQLite et PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_TYPE, DATABASE_URL, DATABASE_PATH


class DatabaseManager:
    """Gestionnaire unifié pour SQLite et PostgreSQL"""

    def __init__(self):
        self.db_type = DATABASE_TYPE

        if self.db_type == 'postgresql':
            self.db_url = DATABASE_URL
        else:
            self.db_path = DATABASE_PATH
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """Retourne une connexion selon le type de BDD"""
        if self.db_type == 'postgresql':
            conn = psycopg2.connect(self.db_url)
            conn.set_session(autocommit=False)
            return conn
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn

    def creer_toutes_les_tables(self):
        """Crée toutes les tables (compatible SQLite et PostgreSQL)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.db_type == 'postgresql':
            # Syntaxe PostgreSQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    mot_de_passe_hash VARCHAR(255) NOT NULL,
                    nom_complet VARCHAR(255) NOT NULL,
                    telephone VARCHAR(50),
                    plan VARCHAR(50) DEFAULT 'gratuit',
                    audits_max_mois INTEGER DEFAULT 3,
                    audits_utilises_ce_mois INTEGER DEFAULT 0,
                    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projets (
                    id SERIAL PRIMARY KEY,
                    utilisateur_id INTEGER NOT NULL,
                    nom_projet VARCHAR(255) NOT NULL,
                    client_nom VARCHAR(255) NOT NULL,
                    type_batiment VARCHAR(100) NOT NULL,
                    statut VARCHAR(50) DEFAULT 'en_cours',
                    pourcentage_completion INTEGER DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batiments (
                    id SERIAL PRIMARY KEY,
                    projet_id INTEGER NOT NULL,
                    surface_totale REAL NOT NULL,
                    annee_construction INTEGER NOT NULL,
                    FOREIGN KEY (projet_id) REFERENCES projets(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etages (
                    id SERIAL PRIMARY KEY,
                    batiment_id INTEGER NOT NULL,
                    numero_etage INTEGER NOT NULL,
                    nom_etage VARCHAR(255) NOT NULL,
                    surface_etage REAL NOT NULL,
                    hauteur_sous_plafond REAL DEFAULT 2.5,
                    pieces_count INTEGER DEFAULT 0,
                    equipements_count INTEGER DEFAULT 0,
                    puissance_totale_w REAL DEFAULT 0,
                    FOREIGN KEY (batiment_id) REFERENCES batiments(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pieces (
                    id SERIAL PRIMARY KEY,
                    etage_id INTEGER NOT NULL,
                    nom_piece VARCHAR(255) NOT NULL,
                    type_piece VARCHAR(100) NOT NULL,
                    surface_piece REAL NOT NULL,
                    longueur_piece REAL DEFAULT 0,
                    largeur_piece REAL DEFAULT 0,
                    hauteur_plafond REAL DEFAULT 2.5,
                    nb_occupants INTEGER DEFAULT 0,
                    equipements_count INTEGER DEFAULT 0,
                    puissance_totale_w REAL DEFAULT 0,
                    FOREIGN KEY (etage_id) REFERENCES etages(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipements (
                    id SERIAL PRIMARY KEY,
                    piece_id INTEGER NOT NULL,
                    nom_equipement VARCHAR(255) NOT NULL,
                    categorie VARCHAR(100) NOT NULL,
                    puissance_w REAL NOT NULL,
                    quantite INTEGER DEFAULT 1,
                    heures_utilisation_jour REAL DEFAULT 8,
                    jours_utilisation_semaine INTEGER DEFAULT 5,
                    FOREIGN KEY (piece_id) REFERENCES pieces(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resultats_audits (
                    id SERIAL PRIMARY KEY,
                    projet_id INTEGER NOT NULL,
                    classe_energetique VARCHAR(10) NOT NULL,
                    consommation_annuelle_kwh REAL NOT NULL,
                    emissions_co2_kg_an REAL NOT NULL,
                    cout_annuel_fcfa REAL NOT NULL,
                    score_performance INTEGER NOT NULL,
                    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (projet_id) REFERENCES projets(id)
                )
            """)

        else:
            # Syntaxe SQLite (ton code actuel)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    mot_de_passe_hash TEXT NOT NULL,
                    nom_complet TEXT NOT NULL,
                    telephone TEXT,
                    plan TEXT DEFAULT 'gratuit',
                    audits_max_mois INTEGER DEFAULT 3,
                    audits_utilises_ce_mois INTEGER DEFAULT 0,
                    date_inscription TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    utilisateur_id INTEGER NOT NULL,
                    nom_projet TEXT NOT NULL,
                    client_nom TEXT NOT NULL,
                    type_batiment TEXT NOT NULL,
                    statut TEXT DEFAULT 'en_cours',
                    pourcentage_completion INTEGER DEFAULT 0,
                    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS batiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projet_id INTEGER NOT NULL,
                    surface_totale REAL NOT NULL,
                    annee_construction INTEGER NOT NULL,
                    FOREIGN KEY (projet_id) REFERENCES projets(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batiment_id INTEGER NOT NULL,
                    numero_etage INTEGER NOT NULL,
                    nom_etage TEXT NOT NULL,
                    surface_etage REAL NOT NULL,
                    hauteur_sous_plafond REAL DEFAULT 2.5,
                    pieces_count INTEGER DEFAULT 0,
                    equipements_count INTEGER DEFAULT 0,
                    puissance_totale_w REAL DEFAULT 0,
                    FOREIGN KEY (batiment_id) REFERENCES batiments(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pieces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    etage_id INTEGER NOT NULL,
                    nom_piece TEXT NOT NULL,
                    type_piece TEXT NOT NULL,
                    surface_piece REAL NOT NULL,
                    longueur_piece REAL DEFAULT 0,
                    largeur_piece REAL DEFAULT 0,
                    hauteur_plafond REAL DEFAULT 2.5,
                    nb_occupants INTEGER DEFAULT 0,
                    equipements_count INTEGER DEFAULT 0,
                    puissance_totale_w REAL DEFAULT 0,
                    FOREIGN KEY (etage_id) REFERENCES etages(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equipements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    piece_id INTEGER NOT NULL,
                    nom_equipement TEXT NOT NULL,
                    categorie TEXT NOT NULL,
                    puissance_w REAL NOT NULL,
                    quantite INTEGER DEFAULT 1,
                    heures_utilisation_jour REAL DEFAULT 8,
                    jours_utilisation_semaine INTEGER DEFAULT 5,
                    FOREIGN KEY (piece_id) REFERENCES pieces(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resultats_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projet_id INTEGER NOT NULL,
                    classe_energetique TEXT NOT NULL,
                    consommation_annuelle_kwh REAL NOT NULL,
                    emissions_co2_kg_an REAL NOT NULL,
                    cout_annuel_fcfa REAL NOT NULL,
                    score_performance INTEGER NOT NULL,
                    date_calcul TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (projet_id) REFERENCES projets(id)
                )
            """)

        conn.commit()
        conn.close()
        print(f"✅ Toutes les tables créées avec succès ({self.db_type})")
