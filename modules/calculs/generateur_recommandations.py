"""
VOLTIX AUDIT - Générateur de recommandations
Génère des recommandations d'amélioration énergétique
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH


class GenerateurRecommandations:
    """Générateur de recommandations d'amélioration"""

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def generer_toutes_recommandations(self, projet_id):
        """
        Génère toutes les recommandations pour un projet

        Args:
            projet_id: ID du projet

        Returns:
            list: Liste des recommandations générées
        """
        print(f"\n💡 Génération des recommandations pour le projet {projet_id}...")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer les résultats de l'audit
            cursor.execute("""
                SELECT * FROM resultats_audits 
                WHERE projet_id = ? 
                ORDER BY date_calcul DESC 
                LIMIT 1
            """, (projet_id,))

            resultat = cursor.fetchone()

            if not resultat:
                print("⚠️  Aucun résultat d'audit trouvé")
                return []

            # Convertir en dictionnaire
            resultat_dict = {
                'classe_energie': resultat[3],  # Index de la colonne classe_energie
                'consommation_totale_kwh_an': resultat[2],
                'cout_annuel_fcfa': resultat[5]
            }

            classe = resultat_dict['classe_energie']
            consommation = resultat_dict['consommation_totale_kwh_an']
            cout = resultat_dict['cout_annuel_fcfa']

            # Liste des recommandations à générer
            recommandations = []

            # Recommandation 1 : Éclairage LED
            recommandations.append({
                'categorie': 'Éclairage',
                'titre': 'Remplacer les lampes par des LED',
                'description': 'Remplacer toutes les lampes fluorescentes et halogènes par des LED économiques. Les LED consomment jusqu\'à 80% moins d\'énergie et durent 10 fois plus longtemps.',
                'priorite': 'haute' if classe in ['E', 'F', 'G'] else 'moyenne',
                'economie_estimee_fcfa': cout * 0.25,  # 25% d'économie
                'cout_investissement_fcfa': consommation * 50,  # Estimation
                'temps_retour_annees': 2.0,
                'impact_co2_kg': consommation * 0.25 * 0.5
            })

            # Recommandation 2 : Climatisation efficace
            if classe in ['D', 'E', 'F', 'G']:
                recommandations.append({
                    'categorie': 'Climatisation',
                    'titre': 'Installer des climatiseurs inverter A+++',
                    'description': 'Remplacer les anciens climatiseurs par des modèles inverter haute efficacité énergétique. Économie de 40% sur la consommation de climatisation.',
                    'priorite': 'haute',
                    'economie_estimee_fcfa': cout * 0.30,
                    'cout_investissement_fcfa': 1500000,
                    'temps_retour_annees': 3.5,
                    'impact_co2_kg': consommation * 0.30 * 0.5
                })

            # Recommandation 3 : Isolation
            if classe in ['E', 'F', 'G']:
                recommandations.append({
                    'categorie': 'Isolation',
                    'titre': 'Améliorer l\'isolation thermique',
                    'description': 'Renforcer l\'isolation des murs et du toit pour réduire les besoins en climatisation. Installation de films solaires sur les vitres.',
                    'priorite': 'haute',
                    'economie_estimee_fcfa': cout * 0.20,
                    'cout_investissement_fcfa': 800000,
                    'temps_retour_annees': 4.0,
                    'impact_co2_kg': consommation * 0.20 * 0.5
                })

            # Recommandation 4 : Panneaux solaires
            if cout > 500000:  # Si coût annuel > 500k FCFA
                recommandations.append({
                    'categorie': 'Énergie renouvelable',
                    'titre': 'Installer des panneaux solaires photovoltaïques',
                    'description': 'Installation d\'un système solaire pour couvrir 30-50% des besoins électriques. Réduction significative de la facture électrique.',
                    'priorite': 'moyenne',
                    'economie_estimee_fcfa': cout * 0.40,
                    'cout_investissement_fcfa': 3000000,
                    'temps_retour_annees': 7.5,
                    'impact_co2_kg': consommation * 0.40 * 0.5
                })

            # Recommandation 5 : Gestion intelligente
            recommandations.append({
                'categorie': 'Automatisation',
                'titre': 'Installer un système de gestion énergétique',
                'description': 'Mise en place de détecteurs de présence, thermostats programmables et système de coupure automatique. Optimisation de la consommation.',
                'priorite': 'moyenne',
                'economie_estimee_fcfa': cout * 0.15,
                'cout_investissement_fcfa': 500000,
                'temps_retour_annees': 3.3,
                'impact_co2_kg': consommation * 0.15 * 0.5
            })

            # Enregistrer les recommandations
            for reco in recommandations:
                cursor.execute("""
                    INSERT INTO recommandations (
                        projet_id, categorie, titre, description, priorite,
                        economie_estimee_fcfa, cout_investissement_fcfa, 
                        temps_retour_annees, impact_co2_kg
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    projet_id,
                    reco['categorie'],
                    reco['titre'],
                    reco['description'],
                    reco['priorite'],
                    reco['economie_estimee_fcfa'],
                    reco['cout_investissement_fcfa'],
                    reco['temps_retour_annees'],
                    reco['impact_co2_kg']
                ))

            conn.commit()
            conn.close()

            print(f"✅ {len(recommandations)} recommandation(s) générée(s)")
            return recommandations

        except Exception as e:
            print(f"❌ Erreur génération recommandations: {e}")
            import traceback
            traceback.print_exc()
            return []
