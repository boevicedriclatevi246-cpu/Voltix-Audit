"""
VOLTIX AUDIT - Vérification conformité UEMOA
Directives 04/2020 et 05/2020
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH


class VerificateurUEMOA:
    """Vérificateur de conformité aux directives UEMOA"""

    # Classes énergétiques UEMOA pour équipements (Directive 04/2020)
    CLASSES_EQUIPEMENTS = {
        'Éclairage': {
            'LED': 'A++',
            'Fluorescent': 'B',
            'Halogène': 'E',
            'Incandescent': 'G'
        },
        'Climatisation': {
            'inverter': 'A+',
            'standard': 'C',
            'window': 'D'
        }
    }

    # Seuils classe énergétique bâtiment (Directive 05/2020)
    SEUILS_BATIMENT = {
        'A': {'min': 0, 'max': 50, 'conforme': True},
        'B': {'min': 51, 'max': 90, 'conforme': True},
        'C': {'min': 91, 'max': 150, 'conforme': True},
        'D': {'min': 151, 'max': 230, 'conforme': False},
        'E': {'min': 231, 'max': 330, 'conforme': False},
        'F': {'min': 331, 'max': 450, 'conforme': False},
        'G': {'min': 451, 'max': 9999, 'conforme': False}
    }

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    # ========================================
    # DIRECTIVE 04/2020 - ÉQUIPEMENTS
    # ========================================

    def verifier_equipement(self, nom_equipement, categorie, puissance_w):
        """
        Vérifie la conformité d'un équipement à la Directive 04/2020

        Args:
            nom_equipement: Nom de l'équipement
            categorie: Catégorie (Éclairage, Climatisation, etc.)
            puissance_w: Puissance en watts

        Returns:
            dict: Résultat de la vérification
        """

        # ÉCLAIRAGE - LED obligatoire
        if categorie == 'Éclairage':
            if 'LED' in nom_equipement:
                return {
                    'conforme': True,
                    'classe_energetique': 'A+',
                    'directive': 'UEMOA 04/2020',
                    'recommandation': 'Conforme - LED recommandé',
                    'economie_potentielle_kwh_an': 0,
                    'priorite': 'aucune'
                }
            else:
                # Équipement non conforme
                puissance_led_equivalente = puissance_w * 0.2  # LED = 20% de l'ancienne techno
                economie_w = puissance_w - puissance_led_equivalente
                economie_kwh_an = (economie_w * 8 * 365) / 1000  # 8h/jour, 365 jours

                return {
                    'conforme': False,
                    'classe_energetique': 'E' if 'Halogène' in nom_equipement else 'G',
                    'directive': 'UEMOA 04/2020 Art. 5',
                    'recommandation': f'⚠️ REMPLACER par LED {int(puissance_led_equivalente)}W (Directive UEMOA)',
                    'economie_potentielle_kwh_an': economie_kwh_an,
                    'cout_remplacement_fcfa': 5000,
                    'priorite': 'haute'
                }

        # CLIMATISATION - SEER ≥ 3.2
        elif categorie == 'Climatisation':
            if 'inverter' in nom_equipement.lower() or 'split' in nom_equipement.lower():
                return {
                    'conforme': True,
                    'classe_energetique': 'A+',
                    'seer_estime': 3.5,
                    'directive': 'UEMOA 05/2020 Annexe 2',
                    'recommandation': 'Conforme - Climatisation performante',
                    'economie_potentielle_kwh_an': 0,
                    'priorite': 'aucune'
                }
            else:
                # Climatisation non performante
                economie_kwh_an = (puissance_w * 0.30 * 8 * 250) / 1000  # 30% économie avec inverter

                return {
                    'conforme': False,
                    'classe_energetique': 'C',
                    'seer_estime': 2.8,
                    'directive': 'UEMOA 05/2020 Annexe 2',
                    'recommandation': '⚠️ Remplacer par climatiseur inverter SEER ≥ 3.2',
                    'economie_potentielle_kwh_an': economie_kwh_an,
                    'cout_remplacement_fcfa': 250000,
                    'priorite': 'moyenne'
                }

        # AUTRES ÉQUIPEMENTS - Vérification générale
        else:
            return {
                'conforme': True,
                'classe_energetique': 'B',
                'directive': 'UEMOA 04/2020',
                'recommandation': 'Vérifier étiquette énergétique classe A minimum',
                'economie_potentielle_kwh_an': 0,
                'priorite': 'basse'
            }

    def analyser_equipements_projet(self, projet_id):
        """
        Analyse tous les équipements d'un projet pour la conformité UEMOA

        Args:
            projet_id: ID du projet

        Returns:
            dict: Résultat complet de l'analyse
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Récupérer tous les équipements du projet
        cursor.execute("""
            SELECT 
                eq.id,
                eq.nom_equipement,
                eq.categorie,
                eq.puissance_w,
                eq.quantite,
                p.nom_piece
            FROM equipements eq
            JOIN pieces p ON eq.piece_id = p.id
            JOIN etages e ON p.etage_id = e.id
            JOIN batiments b ON e.batiment_id = b.id
            WHERE b.projet_id = ?
        """, (projet_id,))

        equipements = cursor.fetchall()
        conn.close()

        if not equipements:
            return {
                'nb_equipements': 0,
                'nb_conformes': 0,
                'nb_non_conformes': 0,
                'taux_conformite': 0,
                'economie_totale_potentielle_kwh_an': 0,
                'equipements_non_conformes': []
            }

        # Analyser chaque équipement
        nb_conformes = 0
        nb_non_conformes = 0
        economie_totale = 0
        equipements_non_conformes = []

        stats_par_categorie = {
            'Éclairage': {'conformes': 0, 'non_conformes': 0},
            'Climatisation': {'conformes': 0, 'non_conformes': 0},
            'Réfrigération': {'conformes': 0, 'non_conformes': 0},
            'Autres': {'conformes': 0, 'non_conformes': 0}
        }

        for eq in equipements:
            eq_id, nom, categorie, puissance, quantite, piece = eq

            # Vérifier conformité
            verif = self.verifier_equipement(nom, categorie, puissance)

            if verif['conforme']:
                nb_conformes += quantite
                cat_key = categorie if categorie in stats_par_categorie else 'Autres'
                stats_par_categorie[cat_key]['conformes'] += quantite
            else:
                nb_non_conformes += quantite
                economie_totale += verif['economie_potentielle_kwh_an'] * quantite

                cat_key = categorie if categorie in stats_par_categorie else 'Autres'
                stats_par_categorie[cat_key]['non_conformes'] += quantite

                equipements_non_conformes.append({
                    'nom': nom,
                    'categorie': categorie,
                    'piece': piece,
                    'quantite': quantite,
                    'classe': verif['classe_energetique'],
                    'recommandation': verif['recommandation'],
                    'economie_kwh_an': verif['economie_potentielle_kwh_an'] * quantite,
                    'priorite': verif['priorite']
                })

        total = nb_conformes + nb_non_conformes
        taux_conformite = (nb_conformes / total * 100) if total > 0 else 0

        return {
            'nb_equipements': total,
            'nb_conformes': nb_conformes,
            'nb_non_conformes': nb_non_conformes,
            'taux_conformite': taux_conformite,
            'economie_totale_potentielle_kwh_an': economie_totale,
            'equipements_non_conformes': equipements_non_conformes,
            'stats_par_categorie': stats_par_categorie,
            'conforme_directive_04': taux_conformite >= 80  # Seuil 80% pour conformité
        }

    # ========================================
    # DIRECTIVE 05/2020 - BÂTIMENT
    # ========================================

    def verifier_batiment(self, consommation_kwh_m2_an):
        """
        Vérifie la conformité du bâtiment à la Directive 05/2020

        Args:
            consommation_kwh_m2_an: Consommation en kWh/m²/an

        Returns:
            dict: Résultat de la vérification
        """

        # Déterminer la classe
        classe = 'G'
        for c, seuils in self.SEUILS_BATIMENT.items():
            if seuils['min'] <= consommation_kwh_m2_an <= seuils['max']:
                classe = c
                break

        infos_classe = self.SEUILS_BATIMENT.get(classe, self.SEUILS_BATIMENT['G'])

        return {
            'classe_energie': classe,
            'consommation_kwh_m2_an': consommation_kwh_m2_an,
            'seuil_min': infos_classe['min'],
            'seuil_max': infos_classe['max'],
            'conforme_directive_05': infos_classe['conforme'],
            'directive': 'UEMOA 05/2020',
            'description': self._get_description_classe(classe, infos_classe['conforme'])
        }

    def _get_description_classe(self, classe, conforme):
        """Retourne la description d'une classe énergétique"""
        descriptions = {
            'A': '✅ Excellente performance - Conforme UEMOA',
            'B': '✅ Bonne performance - Conforme UEMOA',
            'C': '✅ Performance moyenne - Conforme UEMOA',
            'D': '⚠️ Performance passable - Amélioration recommandée',
            'E': '❌ Performance insuffisante - Non conforme UEMOA',
            'F': '❌ Mauvaise performance - Non conforme UEMOA',
            'G': '❌ Très mauvaise performance - Non conforme UEMOA'
        }
        return descriptions.get(classe, 'Performance non évaluée')

    def generer_rapport_conformite(self, projet_id, consommation_kwh_m2_an):
        """
        Génère un rapport complet de conformité UEMOA

        Args:
            projet_id: ID du projet
            consommation_kwh_m2_an: Consommation du bâtiment

        Returns:
            dict: Rapport complet
        """

        # Analyser équipements (Directive 04/2020)
        analyse_equipements = self.analyser_equipements_projet(projet_id)

        # Vérifier bâtiment (Directive 05/2020)
        verif_batiment = self.verifier_batiment(consommation_kwh_m2_an)

        # Conformité globale
        conforme_global = (
                analyse_equipements['conforme_directive_04'] and
                verif_batiment['conforme_directive_05']
        )

        return {
            'conforme_global': conforme_global,
            'directive_04': {
                'conforme': analyse_equipements['conforme_directive_04'],
                'taux_conformite': analyse_equipements['taux_conformite'],
                'nb_equipements': analyse_equipements['nb_equipements'],
                'nb_conformes': analyse_equipements['nb_conformes'],
                'nb_non_conformes': analyse_equipements['nb_non_conformes'],
                'stats_categorie': analyse_equipements['stats_par_categorie'],
                'economie_potentielle': analyse_equipements['economie_totale_potentielle_kwh_an']
            },
            'directive_05': {
                'conforme': verif_batiment['conforme_directive_05'],
                'classe_energie': verif_batiment['classe_energie'],
                'consommation_kwh_m2_an': verif_batiment['consommation_kwh_m2_an'],
                'description': verif_batiment['description']
            },
            'recommandations_prioritaires': analyse_equipements['equipements_non_conformes'][:5]
        }


# Instance globale
verificateur_uemoa = VerificateurUEMOA()
