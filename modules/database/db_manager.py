"""
Gestionnaire de base de données - Support SQLite et PostgreSQL
"""

import sqlite3
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

# Import conditionnel de psycopg2 (seulement si disponible)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

# Import de la config avec gestion d'erreur
try:
    from config.config import DATABASE_TYPE, DATABASE_URL, DATABASE_PATH
except (ImportError, AttributeError) as e:
    print(f"⚠️ Erreur import config: {e}")
    # Valeurs par défaut
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')
    DATABASE_URL = os.environ.get('DATABASE_URL', None)
    DATABASE_PATH = os.path.join(Path(__file__).parent.parent.parent, 'data', 'voltix_audit.db')


class DatabaseManager:
    """Gestionnaire unifié pour SQLite et PostgreSQL"""

    def __init__(self):
        self.db_type = DATABASE_TYPE

        if self.db_type == 'postgresql':
            if not POSTGRESQL_AVAILABLE:
                raise ImportError("psycopg2 n'est pas installé. Installez-le avec: pip install psycopg2-binary")
            self.db_url = DATABASE_URL
            if not self.db_url:
                raise ValueError("DATABASE_URL n'est pas défini pour PostgreSQL")
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

    def dict_factory(self, cursor, row):
        """Convertit les résultats en dictionnaire (pour SQLite)"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def creer_toutes_les_tables(self):
        """Crée toutes les tables (compatible SQLite et PostgreSQL)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
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
                # Syntaxe SQLite
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
            print(f"✅ Toutes les tables créées avec succès ({self.db_type})")

        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur création tables: {e}")
            raise
        finally:
            conn.close()

    def obtenir_utilisateur_par_email(self, email):
        """Récupère un utilisateur par son email"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.db_type == 'postgresql':
            cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                user = dict(zip(columns, result))
            else:
                user = None
        else:
            cursor.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
            result = cursor.fetchone()
            user = dict(result) if result else None

        conn.close()
        return user

    def obtenir_utilisateur_par_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.db_type == 'postgresql':
            cursor.execute("SELECT * FROM utilisateurs WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                user = dict(zip(columns, result))
            else:
                user = None
        else:
            cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            user = dict(result) if result else None

        conn.close()
        return user

    def creer_utilisateur(self, email, mot_de_passe_hash, nom_complet, telephone):
        """Crée un nouvel utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if self.db_type == 'postgresql':
                cursor.execute("""
                    INSERT INTO utilisateurs (email, mot_de_passe_hash, nom_complet, telephone)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (email, mot_de_passe_hash, nom_complet, telephone))
                user_id = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    INSERT INTO utilisateurs (email, mot_de_passe_hash, nom_complet, telephone)
                    VALUES (?, ?, ?, ?)
                """, (email, mot_de_passe_hash, nom_complet, telephone))
                user_id = cursor.lastrowid

            conn.commit()
            print(f"✅ Utilisateur créé avec ID: {user_id}")
            return user_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur création utilisateur: {e}")
            return None
        finally:
            conn.close()

    def mettre_a_jour_plan_utilisateur(self, user_id, nouveau_plan):
        """Met à jour le plan d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            audits_max = 20 if nouveau_plan == 'pro' else 3

            if self.db_type == 'postgresql':
                cursor.execute("""
                    UPDATE utilisateurs 
                    SET plan = %s, audits_max_mois = %s
                    WHERE id = %s
                """, (nouveau_plan, audits_max, user_id))
            else:
                cursor.execute("""
                    UPDATE utilisateurs 
                    SET plan = ?, audits_max_mois = ?
                    WHERE id = ?
                """, (nouveau_plan, audits_max, user_id))

            conn.commit()
            print(f"✅ Plan mis à jour: {nouveau_plan} pour utilisateur {user_id}")
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur mise à jour plan: {e}")
            return False
        finally:
            conn.close()

    def get_projets_utilisateur(self, utilisateur_id):
        """Récupère tous les projets d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.db_type == 'postgresql':
            cursor.execute("""
                SELECT * FROM projets 
                WHERE utilisateur_id = %s 
                ORDER BY date_creation DESC
            """, (utilisateur_id,))
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            projets = [dict(zip(columns, row)) for row in results]
        else:
            cursor.execute("""
                SELECT * FROM projets 
                WHERE utilisateur_id = ? 
                ORDER BY date_creation DESC
            """, (utilisateur_id,))
            projets = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return projets

    def get_projet_by_id(self, projet_id):
        """Récupère un projet par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.db_type == 'postgresql':
            cursor.execute("SELECT * FROM projets WHERE id = %s", (projet_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                projet = dict(zip(columns, result))
            else:
                projet = None
        else:
            cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
            result = cursor.fetchone()
            projet = dict(result) if result else None

        conn.close()
        return projet

    def supprimer_projet(self, projet_id):
        """Supprime un projet et toutes ses données associées"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Récupérer les bâtiments du projet
            if self.db_type == 'postgresql':
                cursor.execute("SELECT id FROM batiments WHERE projet_id = %s", (projet_id,))
            else:
                cursor.execute("SELECT id FROM batiments WHERE projet_id = ?", (projet_id,))

            batiments = cursor.fetchall()

            for batiment in batiments:
                batiment_id = batiment[0]

                # Récupérer les étages
                if self.db_type == 'postgresql':
                    cursor.execute("SELECT id FROM etages WHERE batiment_id = %s", (batiment_id,))
                else:
                    cursor.execute("SELECT id FROM etages WHERE batiment_id = ?", (batiment_id,))

                etages = cursor.fetchall()

                for etage in etages:
                    etage_id = etage[0]

                    # Récupérer les pièces
                    if self.db_type == 'postgresql':
                        cursor.execute("SELECT id FROM pieces WHERE etage_id = %s", (etage_id,))
                    else:
                        cursor.execute("SELECT id FROM pieces WHERE etage_id = ?", (etage_id,))

                    pieces = cursor.fetchall()

                    for piece in pieces:
                        piece_id = piece[0]

                        # Supprimer les équipements
                        if self.db_type == 'postgresql':
                            cursor.execute("DELETE FROM equipements WHERE piece_id = %s", (piece_id,))
                        else:
                            cursor.execute("DELETE FROM equipements WHERE piece_id = ?", (piece_id,))

                    # Supprimer les pièces
                    if self.db_type == 'postgresql':
                        cursor.execute("DELETE FROM pieces WHERE etage_id = %s", (etage_id,))
                    else:
                        cursor.execute("DELETE FROM pieces WHERE etage_id = ?", (etage_id,))

                # Supprimer les étages
                if self.db_type == 'postgresql':
                    cursor.execute("DELETE FROM etages WHERE batiment_id = %s", (batiment_id,))
                else:
                    cursor.execute("DELETE FROM etages WHERE batiment_id = ?", (batiment_id,))

            # Supprimer les bâtiments
            if self.db_type == 'postgresql':
                cursor.execute("DELETE FROM batiments WHERE projet_id = %s", (projet_id,))
                cursor.execute("DELETE FROM resultats_audits WHERE projet_id = %s", (projet_id,))
                cursor.execute("DELETE FROM projets WHERE id = %s", (projet_id,))
            else:
                cursor.execute("DELETE FROM batiments WHERE projet_id = ?", (projet_id,))
                cursor.execute("DELETE FROM resultats_audits WHERE projet_id = ?", (projet_id,))
                cursor.execute("DELETE FROM projets WHERE id = ?", (projet_id,))

            conn.commit()
            print(f"✅ Projet {projet_id} supprimé avec succès")
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Erreur suppression projet: {e}")
            return False
        finally:
            conn.close()

    def get_statistiques_utilisateur(self, utilisateur_id):
        """Récupère les statistiques d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {
            'nb_projets': 0,
            'nb_audits': 0,
            'dernier_projet': None
        }

        try:
            # Nombre de projets
            if self.db_type == 'postgresql':
                cursor.execute("SELECT COUNT(*) FROM projets WHERE utilisateur_id = %s", (utilisateur_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM projets WHERE utilisateur_id = ?", (utilisateur_id,))
            stats['nb_projets'] = cursor.fetchone()[0]

            # Nombre d'audits
            if self.db_type == 'postgresql':
                cursor.execute("""
                    SELECT COUNT(*) FROM resultats_audits r
                    JOIN projets p ON r.projet_id = p.id
                    WHERE p.utilisateur_id = %s
                """, (utilisateur_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM resultats_audits r
                    JOIN projets p ON r.projet_id = p.id
                    WHERE p.utilisateur_id = ?
                """, (utilisateur_id,))
            stats['nb_audits'] = cursor.fetchone()[0]

            # Dernier projet
            if self.db_type == 'postgresql':
                cursor.execute("""
                    SELECT nom_projet FROM projets 
                    WHERE utilisateur_id = %s 
                    ORDER BY date_creation DESC 
                    LIMIT 1
                """, (utilisateur_id,))
            else:
                cursor.execute("""
                    SELECT nom_projet FROM projets 
                    WHERE utilisateur_id = ? 
                    ORDER BY date_creation DESC 
                    LIMIT 1
                """, (utilisateur_id,))

            result = cursor.fetchone()
            if result:
                stats['dernier_projet'] = result[0]

        except Exception as e:
            print(f"❌ Erreur récupération stats: {e}")

        finally:
            conn.close()

        return stats

# Instance globale
db_manager = DatabaseManager()
