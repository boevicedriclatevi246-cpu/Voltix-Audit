"""
VOLTIX AUDIT - Gestionnaire d'Alertes
Système de notifications et rappels pour les utilisateurs
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH


class GestionnaireAlertes:
    """Gestionnaire des alertes et rappels"""

    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ========================================
    # CRÉATION DES ALERTES
    # ========================================

    def creer_alerte(self, projet_id, type_alerte, message, etage_id=None, piece_id=None):
        """
        Crée une nouvelle alerte

        Args:
            projet_id: ID du projet
            type_alerte: Type d'alerte
            message: Message de l'alerte
            etage_id: ID de l'étage (optionnel)
            piece_id: ID de la pièce (optionnel)

        Returns:
            int: ID de l'alerte créée
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO alertes_completion (
                    projet_id, etage_id, piece_id, type_alerte, message
                ) VALUES (?, ?, ?, ?, ?)
            """, (projet_id, etage_id, piece_id, type_alerte, message))

            alerte_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return alerte_id

        except sqlite3.Error as e:
            print(f"❌ Erreur création alerte: {e}")
            return None

    def verifier_et_creer_alertes_projet(self, projet_id):
        """
        Vérifie un projet et crée les alertes nécessaires

        Args:
            projet_id: ID du projet

        Returns:
            list: Liste des alertes créées
        """
        alertes_creees = []

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer le bâtiment
            cursor.execute("""
                SELECT id FROM batiments WHERE projet_id = ?
            """, (projet_id,))

            batiment = cursor.fetchone()

            if not batiment:
                print(f"⚠️  Aucun bâtiment trouvé pour le projet {projet_id}")
                conn.close()
                return alertes_creees

            batiment_id = batiment['id']

            # 1. Vérifier les étages vides
            cursor.execute("""
                SELECT e.id, e.nom_etage, e.pieces_count
                FROM etages e
                WHERE e.batiment_id = ? AND e.pieces_count = 0
            """, (batiment_id,))

            etages_vides = cursor.fetchall()

            for etage in etages_vides:
                message = f"⚠️ L'étage '{etage['nom_etage']}' ne contient aucune pièce. Ajoutez des pièces pour continuer."
                alerte_id = self.creer_alerte(
                    projet_id=projet_id,
                    type_alerte='etage_vide',
                    message=message,
                    etage_id=etage['id']
                )
                if alerte_id:
                    alertes_creees.append({
                        'id': alerte_id,
                        'type': 'etage_vide',
                        'message': message,
                        'etage': etage['nom_etage']
                    })

            # 2. Vérifier les pièces sans équipements
            cursor.execute("""
                SELECT p.id, p.nom_piece, e.nom_etage, p.equipements_count
                FROM pieces p
                JOIN etages e ON p.etage_id = e.id
                WHERE e.batiment_id = ? AND p.equipements_count = 0
            """, (batiment_id,))

            pieces_vides = cursor.fetchall()

            for piece in pieces_vides:
                message = f"⚠️ La pièce '{piece['nom_piece']}' ({piece['nom_etage']}) n'a aucun équipement. Ajoutez des équipements."
                alerte_id = self.creer_alerte(
                    projet_id=projet_id,
                    type_alerte='piece_sans_equipements',
                    message=message,
                    piece_id=piece['id']
                )
                if alerte_id:
                    alertes_creees.append({
                        'id': alerte_id,
                        'type': 'piece_sans_equipements',
                        'message': message,
                        'piece': piece['nom_piece']
                    })

            # 3. Vérifier si le bâtiment a des données manquantes
            cursor.execute("""
                SELECT surface_totale, annee_construction, puissance_souscrite
                FROM batiments
                WHERE id = ?
            """, (batiment_id,))

            batiment_data = cursor.fetchone()

            donnees_manquantes = []
            if not batiment_data['surface_totale']:
                donnees_manquantes.append('surface totale')
            if not batiment_data['annee_construction']:
                donnees_manquantes.append('année de construction')
            if not batiment_data['puissance_souscrite']:
                donnees_manquantes.append('puissance souscrite')

            if donnees_manquantes:
                message = f"⚠️ Données manquantes du bâtiment : {', '.join(donnees_manquantes)}."
                alerte_id = self.creer_alerte(
                    projet_id=projet_id,
                    type_alerte='donnees_manquantes',
                    message=message
                )
                if alerte_id:
                    alertes_creees.append({
                        'id': alerte_id,
                        'type': 'donnees_manquantes',
                        'message': message
                    })

            # 4. Vérifier si les solutions énergétiques sont renseignées
            cursor.execute("""
                SELECT id FROM solutions_actuelles WHERE projet_id = ?
            """, (projet_id,))

            solutions = cursor.fetchone()

            if not solutions:
                message = "ℹ️ Les solutions énergétiques actuelles ne sont pas renseignées. Cela permettra des recommandations plus précises."
                alerte_id = self.creer_alerte(
                    projet_id=projet_id,
                    type_alerte='solutions_non_renseignees',
                    message=message
                )
                if alerte_id:
                    alertes_creees.append({
                        'id': alerte_id,
                        'type': 'solutions_non_renseignees',
                        'message': message
                    })

            conn.close()

            return alertes_creees

        except sqlite3.Error as e:
            print(f"❌ Erreur vérification alertes: {e}")
            return alertes_creees

    # ========================================
    # RÉCUPÉRATION DES ALERTES
    # ========================================

    def obtenir_alertes_projet(self, projet_id, seulement_non_resolues=True):
        """
        Récupère toutes les alertes d'un projet

        Args:
            projet_id: ID du projet
            seulement_non_resolues: Ne récupérer que les alertes non résolues

        Returns:
            list: Liste des alertes
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT a.*, e.nom_etage, p.nom_piece
                FROM alertes_completion a
                LEFT JOIN etages e ON a.etage_id = e.id
                LEFT JOIN pieces p ON a.piece_id = p.id
                WHERE a.projet_id = ?
            """

            if seulement_non_resolues:
                query += " AND a.resolu = 0"

            query += " ORDER BY a.date_creation DESC"

            cursor.execute(query, (projet_id,))

            alertes = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return alertes

        except sqlite3.Error as e:
            print(f"❌ Erreur récupération alertes: {e}")
            return []

    def compter_alertes_non_resolues(self, projet_id):
        """Compte le nombre d'alertes non résolues pour un projet"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as nb_alertes
                FROM alertes_completion
                WHERE projet_id = ? AND resolu = 0
            """, (projet_id,))

            result = cursor.fetchone()
            conn.close()

            return result['nb_alertes']

        except sqlite3.Error as e:
            print(f"❌ Erreur comptage alertes: {e}")
            return 0

    # ========================================
    # RÉSOLUTION DES ALERTES
    # ========================================

    def resoudre_alerte(self, alerte_id):
        """
        Marque une alerte comme résolue

        Args:
            alerte_id: ID de l'alerte

        Returns:
            bool: True si résolue, False sinon
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE alertes_completion
                SET resolu = 1
                WHERE id = ?
            """, (alerte_id,))

            conn.commit()
            conn.close()

            return True

        except sqlite3.Error as e:
            print(f"❌ Erreur résolution alerte: {e}")
            return False

    def resoudre_alertes_type(self, projet_id, type_alerte):
        """
        Résout toutes les alertes d'un certain type pour un projet

        Args:
            projet_id: ID du projet
            type_alerte: Type d'alerte à résoudre

        Returns:
            int: Nombre d'alertes résolues
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE alertes_completion
                SET resolu = 1
                WHERE projet_id = ? AND type_alerte = ? AND resolu = 0
            """, (projet_id, type_alerte))

            nb_resolues = cursor.rowcount
            conn.commit()
            conn.close()

            return nb_resolues

        except sqlite3.Error as e:
            print(f"❌ Erreur résolution alertes: {e}")
            return 0

    def nettoyer_alertes_obsoletes(self, projet_id):
        """
        Nettoie les alertes obsolètes (ex: étage qui a maintenant des pièces)

        Returns:
            int: Nombre d'alertes nettoyées
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Résoudre les alertes "etage_vide" pour les étages qui ont maintenant des pièces
            cursor.execute("""
                UPDATE alertes_completion
                SET resolu = 1
                WHERE projet_id = ? 
                AND type_alerte = 'etage_vide'
                AND resolu = 0
                AND etage_id IN (
                    SELECT id FROM etages WHERE pieces_count > 0
                )
            """, (projet_id,))

            nb1 = cursor.rowcount

            # Résoudre les alertes "piece_sans_equipements" pour les pièces qui ont maintenant des équipements
            cursor.execute("""
                UPDATE alertes_completion
                SET resolu = 1
                WHERE projet_id = ?
                AND type_alerte = 'piece_sans_equipements'
                AND resolu = 0
                AND piece_id IN (
                    SELECT id FROM pieces WHERE equipements_count > 0
                )
            """, (projet_id,))

            nb2 = cursor.rowcount

            total = nb1 + nb2

            conn.commit()
            conn.close()

            if total > 0:
                print(f"🧹 {total} alerte(s) obsolète(s) résolue(s)")

            return total

        except sqlite3.Error as e:
            print(f"❌ Erreur nettoyage alertes: {e}")
            return 0

    # ========================================
    # VÉRIFICATION DE COMPLÉTION
    # ========================================

    def verifier_completion_projet(self, projet_id):
        """
        Vérifie si un projet est complet et prêt pour l'audit

        Returns:
            dict: Informations de complétion
        """
        try:
            # Nettoyer les alertes obsolètes
            self.nettoyer_alertes_obsoletes(projet_id)

            # Compter les alertes restantes
            nb_alertes = self.compter_alertes_non_resolues(projet_id)

            # Récupérer les détails
            alertes = self.obtenir_alertes_projet(projet_id, seulement_non_resolues=True)

            # Grouper par type
            par_type = {}
            for alerte in alertes:
                type_a = alerte['type_alerte']
                if type_a not in par_type:
                    par_type[type_a] = []
                par_type[type_a].append(alerte)

            # Déterminer si complet
            # Un projet est complet s'il n'y a pas d'alertes critiques
            types_critiques = ['etage_vide', 'piece_sans_equipements']
            alertes_critiques = sum(len(par_type.get(t, [])) for t in types_critiques)

            est_complet = alertes_critiques == 0

            return {
                'complet': est_complet,
                'nb_alertes_totales': nb_alertes,
                'nb_alertes_critiques': alertes_critiques,
                'alertes': alertes,
                'alertes_par_type': par_type,
                'message': 'Projet prêt pour l\'audit' if est_complet else f'{alertes_critiques} alerte(s) critique(s) à résoudre'
            }

        except Exception as e:
            print(f"❌ Erreur vérification complétion: {e}")
            return None


# ========================================
# TEST DU MODULE
# ========================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU GESTIONNAIRE D'ALERTES - VOLTIX AUDIT")
    print("=" * 70)

    ga = GestionnaireAlertes()

    # Tester avec le projet 1
    projet_id = 1

    print(f"\n1️⃣  Vérification et création des alertes pour le projet {projet_id}...")
    alertes = ga.verifier_et_creer_alertes_projet(projet_id)

    if alertes:
        print(f"\n⚠️  {len(alertes)} alerte(s) détectée(s):")
        for i, alerte in enumerate(alertes, 1):
            print(f"   {i}. [{alerte['type']}] {alerte['message']}")
    else:
        print("\n✅ Aucune alerte détectée - Projet complet !")

    print(f"\n2️⃣  Récupération de toutes les alertes non résolues...")
    toutes_alertes = ga.obtenir_alertes_projet(projet_id)
    print(f"   Total: {len(toutes_alertes)} alerte(s)")

    print(f"\n3️⃣  Vérification de la complétion du projet...")
    completion = ga.verifier_completion_projet(projet_id)

    if completion:
        print(f"\n   {'✅' if completion['complet'] else '⚠️'} {completion['message']}")
        print(f"   Alertes totales: {completion['nb_alertes_totales']}")
        print(f"   Alertes critiques: {completion['nb_alertes_critiques']}")

        if completion['alertes_par_type']:
            print("\n   Répartition par type:")
            for type_a, liste in completion['alertes_par_type'].items():
                print(f"      • {type_a}: {len(liste)}")

    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70)
    print("\n💡 Le système d'alertes aide l'utilisateur à:")
    print("   - Compléter tous les étages")
    print("   - Ajouter des équipements dans toutes les pièces")
    print("   - Renseigner toutes les données nécessaires")
    print("   - Savoir quand l'audit est prêt à être calculé")
