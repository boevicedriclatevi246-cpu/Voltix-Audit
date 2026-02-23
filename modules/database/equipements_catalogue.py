"""
VOLTIX AUDIT - Catalogue d'Équipements Prédéfinis
Remplissage automatique du catalogue
"""

import sqlite3
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import DATABASE_PATH


class EquipementsCatalogue:
    """Gestionnaire du catalogue d'équipements prédéfinis"""

    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH

    def remplir_catalogue(self):
        """Remplit le catalogue avec tous les équipements prédéfinis"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Vérifier si déjà rempli
            cursor.execute("SELECT COUNT(*) FROM equipements_catalogue")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"ℹ️  Catalogue déjà rempli ({count} équipements)")
                conn.close()
                return True

            print("📦 Remplissage du catalogue d'équipements...")

            # LAMPES
            lampes = self._get_lampes()
            self._inserer_equipements(cursor, lampes)

            # CLIMATISEURS
            climatiseurs = self._get_climatiseurs()
            self._inserer_equipements(cursor, climatiseurs)

            # VENTILATEURS
            ventilateurs = self._get_ventilateurs()
            self._inserer_equipements(cursor, ventilateurs)

            # BUREAUTIQUE
            bureautique = self._get_bureautique()
            self._inserer_equipements(cursor, bureautique)

            conn.commit()

            # Compter le total
            cursor.execute("SELECT COUNT(*) FROM equipements_catalogue")
            total = cursor.fetchone()[0]

            conn.close()

            print(f"✅ Catalogue rempli avec {total} équipements!")
            return True

        except sqlite3.Error as e:
            print(f"❌ Erreur remplissage catalogue: {e}")
            return False

    def _inserer_equipements(self, cursor, equipements):
        """Insère une liste d'équipements"""
        for eq in equipements:
            cursor.execute("""
                INSERT INTO equipements_catalogue (
                    categorie, type_specifique, designation, 
                    puissance_unitaire, caracteristiques_json
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                eq['categorie'],
                eq['type_specifique'],
                eq['designation'],
                eq['puissance'],
                json.dumps(eq.get('caracteristiques', {}))
            ))

    def _get_lampes(self):
        """Retourne la liste des lampes"""
        return [
            # LED
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 5W', 'puissance': 5},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 7W', 'puissance': 7},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 9W', 'puissance': 9},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 12W', 'puissance': 12},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 15W', 'puissance': 15},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 18W', 'puissance': 18},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 20W', 'puissance': 20},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 36W', 'puissance': 36},
            {'categorie': 'lampe', 'type_specifique': 'LED',
             'designation': 'Ampoule LED 50W', 'puissance': 50},

            # Tubes LED
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 1x9W', 'puissance': 9},
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 2x9W', 'puissance': 18},
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 1x18W', 'puissance': 18},
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 2x18W', 'puissance': 36},
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 1x20W', 'puissance': 20},
            {'categorie': 'lampe', 'type_specifique': 'Tube LED T8',
             'designation': 'Tube LED T8 2x20W', 'puissance': 40},

            # Panneaux LED
            {'categorie': 'lampe', 'type_specifique': 'Panneau LED',
             'designation': 'Panneau LED 40W (60x60)', 'puissance': 40},
            {'categorie': 'lampe', 'type_specifique': 'Panneau LED',
             'designation': 'Panneau LED 50W (60x60)', 'puissance': 50},
            {'categorie': 'lampe', 'type_specifique': 'Panneau LED',
             'designation': 'Panneau LED 60W (120x30)', 'puissance': 60},

            # Fluocompact (CFL)
            {'categorie': 'lampe', 'type_specifique': 'Fluocompact',
             'designation': 'CFL 9W', 'puissance': 9},
            {'categorie': 'lampe', 'type_specifique': 'Fluocompact',
             'designation': 'CFL 11W', 'puissance': 11},
            {'categorie': 'lampe', 'type_specifique': 'Fluocompact',
             'designation': 'CFL 15W', 'puissance': 15},
            {'categorie': 'lampe', 'type_specifique': 'Fluocompact',
             'designation': 'CFL 18W', 'puissance': 18},
            {'categorie': 'lampe', 'type_specifique': 'Fluocompact',
             'designation': 'CFL 23W', 'puissance': 23},

            # Tubes Fluo
            {'categorie': 'lampe', 'type_specifique': 'Tube Fluo',
             'designation': 'Tube Fluo 1x18W', 'puissance': 18},
            {'categorie': 'lampe', 'type_specifique': 'Tube Fluo',
             'designation': 'Tube Fluo 2x18W', 'puissance': 36},
            {'categorie': 'lampe', 'type_specifique': 'Tube Fluo',
             'designation': 'Tube Fluo 1x36W', 'puissance': 36},
            {'categorie': 'lampe', 'type_specifique': 'Tube Fluo',
             'designation': 'Tube Fluo 2x36W', 'puissance': 72},
            {'categorie': 'lampe', 'type_specifique': 'Tube Fluo',
             'designation': 'Tube Fluo 4x18W', 'puissance': 72},

            # Halogène
            {'categorie': 'lampe', 'type_specifique': 'Halogène',
             'designation': 'Halogène 35W', 'puissance': 35},
            {'categorie': 'lampe', 'type_specifique': 'Halogène',
             'designation': 'Halogène 50W', 'puissance': 50},
            {'categorie': 'lampe', 'type_specifique': 'Halogène',
             'designation': 'Halogène 75W', 'puissance': 75},
            {'categorie': 'lampe', 'type_specifique': 'Halogène',
             'designation': 'Halogène 100W', 'puissance': 100},
        ]

    def _get_climatiseurs(self):
        """Retourne la liste des climatiseurs"""
        return [
            {'categorie': 'climatiseur', 'type_specifique': 'Split',
             'designation': 'Split 9000 BTU (0.75 CV)', 'puissance': 800,
             'caracteristiques': {'btu': 9000, 'cop': 3.0, 'cv': 0.75}},

            {'categorie': 'climatiseur', 'type_specifique': 'Split',
             'designation': 'Split 12000 BTU (1 CV)', 'puissance': 1100,
             'caracteristiques': {'btu': 12000, 'cop': 3.0, 'cv': 1.0}},

            {'categorie': 'climatiseur', 'type_specifique': 'Split',
             'designation': 'Split 18000 BTU (1.5 CV)', 'puissance': 1600,
             'caracteristiques': {'btu': 18000, 'cop': 2.8, 'cv': 1.5}},

            {'categorie': 'climatiseur', 'type_specifique': 'Split',
             'designation': 'Split 24000 BTU (2 CV)', 'puissance': 2200,
             'caracteristiques': {'btu': 24000, 'cop': 2.8, 'cv': 2.0}},

            {'categorie': 'climatiseur', 'type_specifique': 'Armoire',
             'designation': 'Armoire 30000 BTU (2.5 CV)', 'puissance': 2800,
             'caracteristiques': {'btu': 30000, 'cop': 2.5, 'cv': 2.5}},

            {'categorie': 'climatiseur', 'type_specifique': 'Armoire',
             'designation': 'Armoire 36000 BTU (3 CV)', 'puissance': 3300,
             'caracteristiques': {'btu': 36000, 'cop': 2.5, 'cv': 3.0}},

            {'categorie': 'climatiseur', 'type_specifique': 'Armoire',
             'designation': 'Armoire 48000 BTU (4 CV)', 'puissance': 4400,
             'caracteristiques': {'btu': 48000, 'cop': 2.3, 'cv': 4.0}},
        ]

    def _get_ventilateurs(self):
        """Retourne la liste des ventilateurs"""
        return [
            {'categorie': 'ventilateur', 'type_specifique': 'Brasseur',
             'designation': 'Brasseur sur pied 60W', 'puissance': 60},

            {'categorie': 'ventilateur', 'type_specifique': 'Plafond',
             'designation': 'Ventilateur plafond 75W', 'puissance': 75},

            {'categorie': 'ventilateur', 'type_specifique': 'Mural',
             'designation': 'Ventilateur mural 45W', 'puissance': 45},

            {'categorie': 'ventilateur', 'type_specifique': 'Extracteur',
             'designation': 'Extracteur d\'air 30W', 'puissance': 30},
        ]

    def _get_bureautique(self):
        """Retourne la liste des équipements bureautiques"""
        return [
            {'categorie': 'bureautique', 'type_specifique': 'Ordinateur',
             'designation': 'Ordinateur fixe', 'puissance': 200},

            {'categorie': 'bureautique', 'type_specifique': 'Ordinateur',
             'designation': 'Ordinateur portable', 'puissance': 65},

            {'categorie': 'bureautique', 'type_specifique': 'Écran',
             'designation': 'Écran 22-24"', 'puissance': 30},

            {'categorie': 'bureautique', 'type_specifique': 'Imprimante',
             'designation': 'Imprimante jet d\'encre', 'puissance': 30},

            {'categorie': 'bureautique', 'type_specifique': 'Imprimante',
             'designation': 'Imprimante laser', 'puissance': 50},

            {'categorie': 'bureautique', 'type_specifique': 'Photocopieur',
             'designation': 'Photocopieur standard', 'puissance': 1500},

            {'categorie': 'bureautique', 'type_specifique': 'Scanner',
             'designation': 'Scanner', 'puissance': 20},
        ]


if __name__ == "__main__":
    print("=" * 60)
    print("REMPLISSAGE DU CATALOGUE - VOLTIX AUDIT")
    print("=" * 60)

    catalogue = EquipementsCatalogue()
    catalogue.remplir_catalogue()

