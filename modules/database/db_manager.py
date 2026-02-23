"""
VOLTIX AUDIT - Gestionnaire de Base de Données
Gestion de toutes les opérations sur la BDD SQLite
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json
import sys

# Ajouter le chemin parent pour importer config
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH
from modules.database.models import ALL_TABLES, SQL_CREATE_INDEXES


class DatabaseManager:
    """Gestionnaire principal de la base de données Voltix Audit"""

    def __init__(self, db_path=None):
        """Initialise le gestionnaire de base de données"""
        self.db_path = db_path or DATABASE_PATH

        # Créer le dossier data s'il n'existe pas
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Créer les tables si la base n'existe pas
        if not Path(self.db_path).exists():
            print(f"🔧 Création de la base de données : {self.db_path}")
            self.creer_toutes_les_tables()
        else:
            print(f"✅ Base de données existante : {self.db_path}")

    def get_connection(self):
        """Crée et retourne une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        return conn

    def create_database(self):
        """
        Crée toutes les tables de la base de données

        Returns:
            bool: True si succès, False sinon
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Activer les contraintes de clés étrangères
            cursor.execute("PRAGMA foreign_keys = ON")

            # Créer toutes les tables
            for table_sql in ALL_TABLES:
                cursor.execute(table_sql)

            # Créer les index
            for index_sql in SQL_CREATE_INDEXES:
                cursor.execute(index_sql)

            conn.commit()
            conn.close()

            print("✅ Base de données Voltix Audit créée avec succès!")
            return True

        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création de la base de données: {e}")
            return False

    def verifier_tables(self):
        """
        Vérifie que toutes les tables existent

        Returns:
            list: Liste des tables présentes
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)

            tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            return tables

        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la vérification des tables: {e}")
            return []

    def reset_database(self):
        """
        ATTENTION : Supprime et recrée toute la base de données
        À utiliser uniquement en développement !
        """
        try:
            # Supprimer le fichier de base de données s'il existe
            if Path(self.db_path).exists():
                Path(self.db_path).unlink()
                print("🗑️ Ancienne base de données supprimée")

            # Recréer la base de données
            self.create_database()
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation: {e}")
            return False

    # ========================================
    # MÉTHODES POUR LES UTILISATEURS
    # ========================================

    def creer_utilisateur(self, email, mot_de_passe_hash, nom_complet=None,
                          telephone=None, pays='BJ', plan='gratuit'):
        """
        Crée un nouvel utilisateur

        Args:
            email: Email de l'utilisateur
            mot_de_passe_hash: Hash du mot de passe (déjà hashé avec bcrypt)
            nom_complet: Nom complet
            telephone: Numéro de téléphone
            pays: Code pays (BJ, CI, SN, etc.)
            plan: Plan d'abonnement (gratuit, pro, entreprise)

        Returns:
            int: ID de l'utilisateur créé ou None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Déterminer le nombre d'audits max selon le plan
            from config.config import PLANS
            audits_max = PLANS.get(plan, PLANS['gratuit'])['audits_max_mois']

            cursor.execute("""
                INSERT INTO utilisateurs (
                    email, mot_de_passe_hash, nom_complet, telephone, pays, 
                    plan, audits_max_mois, audits_utilises_ce_mois
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (email, mot_de_passe_hash, nom_complet, telephone, pays, plan, audits_max))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return user_id

        except sqlite3.IntegrityError:
            print(f"❌ Erreur: Email {email} déjà utilisé")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la création utilisateur: {e}")
            return None

    def get_utilisateur_by_email(self, email):
        """
        Récupère un utilisateur par son email

        Args:
            email: Email de l'utilisateur

        Returns:
            dict: Données de l'utilisateur ou None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM utilisateurs WHERE email = ?
            """, (email,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            print(f"❌ Erreur récupération utilisateur: {e}")
            return None

    def update_derniere_connexion(self, user_id):
        """Met à jour la date de dernière connexion"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE utilisateurs 
                SET derniere_connexion = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (user_id,))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"❌ Erreur mise à jour connexion: {e}")
            return False

    # ========================================
    # MÉTHODES POUR LES PROJETS
    # ========================================

    def creer_projet(self, utilisateur_id, nom_projet, client_nom=None,
                     client_contact=None, type_batiment=None):
        """
        Crée un nouveau projet

        Args:
            utilisateur_id: ID de l'utilisateur
            nom_projet: Nom du projet
            client_nom: Nom du client
            client_contact: Contact du client
            type_batiment: Type de bâtiment

        Returns:
            int: ID du projet créé ou None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO projets (
                    utilisateur_id, nom_projet, client_nom, client_contact, type_batiment,
                    statut, pourcentage_completion
                ) VALUES (?, ?, ?, ?, ?, 'en_cours', 0)
            """, (utilisateur_id, nom_projet, client_nom, client_contact, type_batiment))

            projet_id = cursor.lastrowid
            conn.commit()
            conn.close()

            print(f"✅ Projet créé avec ID: {projet_id}")
            return projet_id

        except Exception as e:
            print(f"❌ Erreur création projet: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_projets_utilisateur(self, utilisateur_id):
        """
        Récupère tous les projets d'un utilisateur

        Args:
            utilisateur_id: ID de l'utilisateur

        Returns:
            list: Liste des projets
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM projets 
                WHERE utilisateur_id = ? 
                ORDER BY date_creation DESC
            """, (utilisateur_id,))

            projets = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return projets

        except Exception as e:
            print(f"❌ Erreur récupération projets: {e}")
            import traceback
            traceback.print_exc()
            return []

    def update_pourcentage_completion(self, projet_id, pourcentage):
        """Met à jour le pourcentage de complétion d'un projet"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            statut = 'termine' if pourcentage >= 100 else 'en_cours'

            cursor.execute("""
                UPDATE projets_audit 
                SET pourcentage_completion = ?,
                    statut = ?,
                    date_derniere_modification = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (pourcentage, statut, projet_id))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            print(f"❌ Erreur mise à jour complétion: {e}")
            return False

    # ========================================
    # FERMETURE
    # ========================================

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("🔒 Connexion à la base de données fermée")


# ========================================
# TEST DU MODULE
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU GESTIONNAIRE DE BASE DE DONNÉES - VOLTIX AUDIT")
    print("=" * 60)

    # Créer le gestionnaire
    db = DatabaseManager()

    # Créer la base de données
    print("\n1. Création de la base de données...")
    db.create_database()

    # Vérifier les tables
    print("\n2. Vérification des tables créées...")
    tables = db.verifier_tables()
    print(f"✅ {len(tables)} tables créées:")
    for table in tables:
        print(f"   - {table}")

    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ - Base de données prête!")
    print("=" * 60)
