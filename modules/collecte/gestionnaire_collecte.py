"""
VOLTIX AUDIT - Gestionnaire de collecte de données
Gère la création et la manipulation des projets, bâtiments, étages, pièces et équipements
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH


class GestionnaireCollecte:
    """Gestionnaire de collecte de données pour les audits énergétiques"""

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    # ========================================
    # PROJETS
    # ========================================

    def creer_projet(self, utilisateur_id, nom_projet, client_nom, type_batiment,
                     adresse_complete, ville, pays):
        """
        Crée un nouveau projet d'audit énergétique

        Args:
            utilisateur_id: ID de l'utilisateur
            nom_projet: Nom du projet
            client_nom: Nom du client
            type_batiment: Type de bâtiment
            adresse_complete: Adresse (optionnel)
            ville: Ville (optionnel)
            pays: Code pays

        Returns:
            int: ID du projet créé ou None si erreur
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # VERSION SIMPLIFIÉE - Seulement les colonnes de base
            cursor.execute("""
                INSERT INTO projets (
                    utilisateur_id, nom_projet, client_nom, type_batiment,
                    statut, pourcentage_completion
                ) VALUES (?, ?, ?, ?, 'en_cours', 0)
            """, (utilisateur_id, nom_projet, client_nom, type_batiment))

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

    # ========================================
    # BÂTIMENTS
    # ========================================

    def creer_batiment(self, projet_id, surface_totale, annee_construction, nb_etages_prevu):
        """
        Crée un bâtiment pour un projet
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # VERSION SIMPLIFIÉE - Sans nb_etages_prevu
            cursor.execute("""
                INSERT INTO batiments (
                    projet_id, surface_totale, annee_construction
                ) VALUES (?, ?, ?)
            """, (projet_id, surface_totale, annee_construction))

            batiment_id = cursor.lastrowid

            conn.commit()
            conn.close()

            print(f"✅ Bâtiment créé avec ID: {batiment_id}")
            return batiment_id

        except Exception as e:
            print(f"❌ Erreur création bâtiment: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================
    # ÉTAGES
    # ========================================

    def creer_etage(self, batiment_id, numero_etage, nom_etage, surface_etage, hauteur_sous_plafond):
        """
        Crée un étage pour un bâtiment

        Args:
            batiment_id: ID du bâtiment
            numero_etage: Numéro de l'étage
            nom_etage: Nom de l'étage
            surface_etage: Surface en m²
            hauteur_sous_plafond: Hauteur en m

        Returns:
            int: ID de l'étage créé ou None si erreur
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO etages (
                    batiment_id, numero_etage, nom_etage, surface_etage, 
                    hauteur_sous_plafond, pieces_count, equipements_count, puissance_totale_w
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0)
            """, (batiment_id, numero_etage, nom_etage, surface_etage, hauteur_sous_plafond))

            etage_id = cursor.lastrowid

            conn.commit()
            conn.close()

            print(f"✅ Étage créé avec ID: {etage_id}")
            return etage_id

        except Exception as e:
            print(f"❌ Erreur création étage: {e}")
            import traceback
            traceback.print_exc()
            return None

    def supprimer_etage(self, etage_id):
        """
        Supprime un étage et tout son contenu (pièces + équipements)

        Args:
            etage_id: ID de l'étage à supprimer

        Returns:
            bool: True si succès, False sinon
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer toutes les pièces de l'étage
            cursor.execute("SELECT id FROM pieces WHERE etage_id = ?", (etage_id,))
            pieces = cursor.fetchall()

            # Supprimer les équipements de chaque pièce
            for piece in pieces:
                cursor.execute("DELETE FROM equipements WHERE piece_id = ?", (piece[0],))

            # Supprimer les pièces
            cursor.execute("DELETE FROM pieces WHERE etage_id = ?", (etage_id,))

            # Supprimer l'étage
            cursor.execute("DELETE FROM etages WHERE id = ?", (etage_id,))

            conn.commit()
            conn.close()

            print(f"✅ Étage {etage_id} supprimé avec succès")
            return True

        except Exception as e:
            print(f"❌ Erreur suppression étage: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================
    # PIÈCES
    # ========================================

    def creer_piece(self, etage_id, nom_piece, type_piece, surface_piece,
                    longueur_piece, largeur_piece, hauteur_plafond, nb_occupants):
        """
        Crée une pièce pour un étage

        Args:
            etage_id: ID de l'étage
            nom_piece: Nom de la pièce
            type_piece: Type de pièce
            surface_piece: Surface en m²
            longueur_piece: Longueur en m (peut être 0)
            largeur_piece: Largeur en m (peut être 0)
            hauteur_plafond: Hauteur en m
            nb_occupants: Nombre d'occupants

        Returns:
            int: ID de la pièce créée ou None si erreur
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO pieces (
                    etage_id, nom_piece, type_piece, surface_piece,
                    longueur_piece, largeur_piece, hauteur_plafond,
                    nb_occupants, equipements_count, puissance_totale_w
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            """, (etage_id, nom_piece, type_piece, surface_piece,
                  longueur_piece, largeur_piece, hauteur_plafond, nb_occupants))

            piece_id = cursor.lastrowid

            # Mettre à jour le compteur de pièces de l'étage
            cursor.execute("""
                UPDATE etages 
                SET pieces_count = pieces_count + 1
                WHERE id = ?
            """, (etage_id,))

            conn.commit()
            conn.close()

            print(f"✅ Pièce créée avec ID: {piece_id}")
            return piece_id

        except Exception as e:
            print(f"❌ Erreur création pièce: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================
    # ÉQUIPEMENTS
    # ========================================

    def ajouter_equipement_piece(self, piece_id, nom_equipement, categorie,
                                 puissance_w, quantite, heures_utilisation_jour,
                                 jours_utilisation_semaine):
        """
        Ajoute un équipement à une pièce

        Args:
            piece_id: ID de la pièce
            nom_equipement: Nom de l'équipement
            categorie: Catégorie
            puissance_w: Puissance en Watts
            quantite: Quantité
            heures_utilisation_jour: Heures par jour
            jours_utilisation_semaine: Jours par semaine

        Returns:
            int: ID de l'équipement créé ou None si erreur
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO equipements (
                    piece_id, nom_equipement, categorie, puissance_w,
                    quantite, heures_utilisation_jour, jours_utilisation_semaine
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (piece_id, nom_equipement, categorie, puissance_w,
                  quantite, heures_utilisation_jour, jours_utilisation_semaine))

            equipement_id = cursor.lastrowid

            # Calculer la puissance totale de cet équipement
            puissance_totale = puissance_w * quantite

            # Mettre à jour les compteurs de la pièce
            cursor.execute("""
                UPDATE pieces 
                SET equipements_count = equipements_count + ?,
                    puissance_totale_w = puissance_totale_w + ?
                WHERE id = ?
            """, (quantite, puissance_totale, piece_id))

            # Mettre à jour les compteurs de l'étage
            cursor.execute("""
                UPDATE etages 
                SET equipements_count = equipements_count + ?,
                    puissance_totale_w = puissance_totale_w + ?
                WHERE id = (SELECT etage_id FROM pieces WHERE id = ?)
            """, (quantite, puissance_totale, piece_id))

            conn.commit()
            conn.close()

            print(f"✅ Équipement ajouté avec ID: {equipement_id}")
            return equipement_id

        except Exception as e:
            print(f"❌ Erreur ajout équipement: {e}")
            import traceback
            traceback.print_exc()
            return None

    def supprimer_equipement(self, equipement_id, piece_id):
        """
        Supprime un équipement et met à jour les compteurs

        Args:
            equipement_id: ID de l'équipement à supprimer
            piece_id: ID de la pièce

        Returns:
            bool: True si succès, False sinon
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer l'équipement pour calculer la puissance
            cursor.execute("SELECT puissance_w, quantite FROM equipements WHERE id = ?", (equipement_id,))
            eq = cursor.fetchone()

            if not eq:
                conn.close()
                return False

            puissance_totale = eq[0] * eq[1]

            # Supprimer l'équipement
            cursor.execute("DELETE FROM equipements WHERE id = ?", (equipement_id,))

            # Mettre à jour les compteurs de la pièce
            cursor.execute("""
                UPDATE pieces 
                SET equipements_count = equipements_count - ?,
                    puissance_totale_w = puissance_totale_w - ?
                WHERE id = ?
            """, (eq[1], puissance_totale, piece_id))

            # Mettre à jour les compteurs de l'étage
            cursor.execute("""
                UPDATE etages 
                SET equipements_count = equipements_count - ?,
                    puissance_totale_w = puissance_totale_w - ?
                WHERE id = (SELECT etage_id FROM pieces WHERE id = ?)
            """, (eq[1], puissance_totale, piece_id))

            conn.commit()
            conn.close()

            print(f"✅ Équipement {equipement_id} supprimé")
            return True

        except Exception as e:
            print(f"❌ Erreur suppression équipement: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================
    # STATISTIQUES
    # ========================================

    def get_statistiques_projet(self, projet_id):
        """
        Récupère les statistiques d'un projet

        Returns:
            dict: Statistiques du projet
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Compter les étages
            cursor.execute("""
                SELECT COUNT(*) FROM etages e
                JOIN batiments b ON e.batiment_id = b.id
                WHERE b.projet_id = ?
            """, (projet_id,))
            nb_etages = cursor.fetchone()[0]

            # Compter les pièces
            cursor.execute("""
                SELECT COUNT(*) FROM pieces p
                JOIN etages e ON p.etage_id = e.id
                JOIN batiments b ON e.batiment_id = b.id
                WHERE b.projet_id = ?
            """, (projet_id,))
            nb_pieces = cursor.fetchone()[0]

            # Compter les équipements
            cursor.execute("""
                SELECT COUNT(*) FROM equipements eq
                JOIN pieces p ON eq.piece_id = p.id
                JOIN etages e ON p.etage_id = e.id
                JOIN batiments b ON e.batiment_id = b.id
                WHERE b.projet_id = ?
            """, (projet_id,))
            nb_equipements = cursor.fetchone()[0]

            conn.close()

            return {
                'nb_etages': nb_etages,
                'nb_pieces': nb_pieces,
                'nb_equipements': nb_equipements
            }

        except Exception as e:
            print(f"❌ Erreur récupération stats: {e}")
            return {
                'nb_etages': 0,
                'nb_pieces': 0,
                'nb_equipements': 0
            }
