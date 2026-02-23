"""
VOLTIX AUDIT - Moteur de calculs énergétiques
Effectue tous les calculs pour l'audit énergétique
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH, TARIFS_ELECTRICITE, FACTEUR_EMISSION_CO2


class MoteurCalculs:
    """Moteur de calculs énergétiques"""

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    # ========================================
    # CALCUL DE CONSOMMATION
    # ========================================

    def calculer_consommation_batiment(self, batiment_id):
        """
        Calcule la consommation totale d'un bâtiment

        Args:
            batiment_id: ID du bâtiment

        Returns:
            dict: Résultats des calculs
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer tous les équipements du bâtiment
            cursor.execute("""
                SELECT 
                    eq.puissance_w,
                    eq.quantite,
                    eq.heures_utilisation_jour,
                    eq.jours_utilisation_semaine,
                    p.surface_piece,
                    p.nb_occupants
                FROM equipements eq
                JOIN pieces p ON eq.piece_id = p.id
                JOIN etages e ON p.etage_id = e.id
                WHERE e.batiment_id = ?
            """, (batiment_id,))

            equipements = cursor.fetchall()

            if not equipements:
                print("⚠️  Aucun équipement trouvé pour le calcul")
                return None

            # Calcul de la consommation annuelle
            consommation_kwh_an = 0

            for eq in equipements:
                puissance_w, quantite, heures_jour, jours_semaine = eq[:4]

                # Consommation journalière en kWh
                conso_jour = (puissance_w * quantite * heures_jour) / 1000

                # Consommation hebdomadaire
                conso_semaine = conso_jour * jours_semaine

                # Consommation annuelle (52 semaines)
                conso_an = conso_semaine * 52

                consommation_kwh_an += conso_an

            conn.close()

            print(f"✅ Consommation calculée: {consommation_kwh_an:,.0f} kWh/an")

            return {
                'consommation_kwh_an': consommation_kwh_an,
                'nb_equipements': len(equipements)
            }

        except Exception as e:
            print(f"❌ Erreur calcul consommation bâtiment: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ========================================
    # CLASSE ÉNERGÉTIQUE
    # ========================================

    def determiner_classe_energie(self, consommation_kwh_m2_an):
        """
        Détermine la classe énergétique (A à G)

        Args:
            consommation_kwh_m2_an: Consommation en kWh/m²/an

        Returns:
            str: Classe énergétique (A, B, C, D, E, F, G)
        """
        if consommation_kwh_m2_an <= 50:
            return 'A'
        elif consommation_kwh_m2_an <= 90:
            return 'B'
        elif consommation_kwh_m2_an <= 150:
            return 'C'
        elif consommation_kwh_m2_an <= 230:
            return 'D'
        elif consommation_kwh_m2_an <= 330:
            return 'E'
        elif consommation_kwh_m2_an <= 450:
            return 'F'
        else:
            return 'G'

    # ========================================
    # CALCUL COMPLET DE L'AUDIT
    # ========================================

    def effectuer_audit_complet(self, projet_id, pays='BJ'):
        """
        Effectue un audit énergétique complet

        Args:
            projet_id: ID du projet
            pays: Code pays (BJ, CI, SN, etc.)

        Returns:
            dict: Résultats complets de l'audit
        """
        print(f"\n🔄 Calcul de l'audit pour le projet {projet_id}...")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer le bâtiment
            cursor.execute("""
                SELECT id, surface_totale FROM batiments WHERE projet_id = ?
            """, (projet_id,))

            batiment = cursor.fetchone()

            if not batiment:
                print("❌ Aucun bâtiment trouvé")
                conn.close()
                return None

            batiment_id = batiment[0]  # Premier élément = id
            surface_totale = batiment[1] if batiment[1] else 100  # Deuxième élément = surface_totale

            # Calculer la consommation
            print("   📊 Calcul des consommations...")
            resultats_conso = self.calculer_consommation_batiment(batiment_id)

            if not resultats_conso:
                print("❌ Erreur lors du calcul de consommation")
                return None

            consommation_kwh_an = resultats_conso['consommation_kwh_an']

            # Consommation par m²
            consommation_kwh_m2_an = consommation_kwh_an / surface_totale

            # Classe énergétique
            classe_energie = self.determiner_classe_energie(consommation_kwh_m2_an)

            # Score de performance (0-100)
            # A=100, B=85, C=70, D=55, E=40, F=25, G=10
            scores = {'A': 100, 'B': 85, 'C': 70, 'D': 55, 'E': 40, 'F': 25, 'G': 10}
            score_performance = scores.get(classe_energie, 50)

            # Émissions CO2
            emissions_co2_kg_an = consommation_kwh_an * FACTEUR_EMISSION_CO2.get(pays, 0.5)

            # Coût annuel
            tarif = TARIFS_ELECTRICITE.get(pays, 100)
            cout_annuel_fcfa = consommation_kwh_an * tarif

            # Enregistrer les résultats
            cursor.execute("""
                INSERT INTO resultats_audits (
                    projet_id, consommation_totale_kwh_an, classe_energie,
                    emissions_co2_kg_an, cout_annuel_fcfa, score_performance
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                projet_id,
                consommation_kwh_an,
                classe_energie,
                emissions_co2_kg_an,
                cout_annuel_fcfa,
                score_performance
            ))

            # Mettre à jour le statut du projet
            pourcentage = 100  # Audit terminé
            cursor.execute("""
                UPDATE projets 
                SET statut = 'termine', pourcentage_completion = ?
                WHERE id = ?
            """, (pourcentage, projet_id))

            conn.commit()
            conn.close()

            resultats = {
                'projet_id': projet_id,
                'consommation_totale_kwh_an': consommation_kwh_an,
                'consommation_kwh_m2_an': consommation_kwh_m2_an,
                'classe_energie': classe_energie,
                'score_performance': score_performance,
                'emissions_co2_kg_an': emissions_co2_kg_an,
                'cout_annuel_fcfa': cout_annuel_fcfa,
                'surface_totale': surface_totale
            }

            print(f"✅ Classe énergétique: {classe_energie}")
            print(f"✅ Score de performance: {score_performance}/100")
            print(f"✅ Audit calculé avec succès")

            return resultats

        except Exception as e:
            print(f"❌ Erreur lors du calcul de l'audit: {e}")
            import traceback
            traceback.print_exc()
            return None
