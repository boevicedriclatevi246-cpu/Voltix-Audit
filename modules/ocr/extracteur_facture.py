"""
VOLTIX AUDIT - Extracteur de Facture OCR
Extraction automatique des données de factures d'électricité
Fonctionnalité PREMIUM (Plan Entreprise uniquement)
"""

import re
from pathlib import Path
import sys
from PIL import Image
import pytesseract
import json

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH


class ExtracteurFacture:
    """Extracteur OCR pour factures d'électricité"""

    def __init__(self):
        # Configuration de Tesseract
        # Sur Windows, il faut installer Tesseract et indiquer le chemin
        # Télécharger ici : https://github.com/UB-Mannheim/tesseract/wiki

        # Décommenter et adapter selon ton installation :
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        print("✅ Extracteur OCR initialisé")

    def extraire_texte_image(self, chemin_image):
        """
        Extrait le texte d'une images de facture

        Args:
            chemin_image: Chemin vers l'images de la facture

        Returns:
            str: Texte extrait
        """
        try:
            print(f"\n📸 Extraction du texte de l'images...")
            print(f"   Fichier: {chemin_image}")

            # Ouvrir l'images
            image = Image.open(chemin_image)

            # Prétraitement de l'images (améliore la précision)
            # Convertir en niveaux de gris
            image = image.convert('L')

            # Extraction du texte avec Tesseract
            # lang='fra' pour français
            texte = pytesseract.image_to_string(image, lang='fra')

            print(f"✅ Texte extrait ({len(texte)} caractères)")

            return texte

        except FileNotFoundError:
            print(f"❌ Fichier introuvable: {chemin_image}")
            return None
        except pytesseract.TesseractNotFoundError:
            print("❌ Tesseract OCR n'est pas installé !")
            print("💡 Téléchargez Tesseract depuis :")
            print("   https://github.com/UB-Mannheim/tesseract/wiki")
            return None
        except Exception as e:
            print(f"❌ Erreur extraction texte: {e}")
            import traceback
            traceback.print_exc()
            return None

    def analyser_facture_electricite(self, texte):
        """
        Analyse le texte extrait pour identifier les données clés

        Args:
            texte: Texte extrait de la facture

        Returns:
            dict: Données extraites
        """
        try:
            print("\n🔍 Analyse de la facture...")

            donnees = {
                'consommation_kwh': None,
                'montant_fcfa': None,
                'periode': None,
                'numero_compteur': None,
                'fournisseur': None,
                'confiance': 0  # Score de confiance (0-100)
            }

            # Normaliser le texte (minuscules, espaces)
            texte_clean = ' '.join(texte.lower().split())

            # 1. EXTRACTION DE LA CONSOMMATION (kWh)
            # Patterns possibles :
            # - "consommation : 1234 kwh"
            # - "énergie consommée : 1234 kwh"
            # - "1234 kwh"
            patterns_kwh = [
                r'consommation[:\s]+(\d+[\s,.]?\d*)\s*kwh',
                r'énergie\s+consommée[:\s]+(\d+[\s,.]?\d*)\s*kwh',
                r'energie\s+consommee[:\s]+(\d+[\s,.]?\d*)\s*kwh',
                r'(\d+[\s,.]?\d*)\s*kwh',
                r'kwh[:\s]+(\d+[\s,.]?\d*)',
            ]

            for pattern in patterns_kwh:
                match = re.search(pattern, texte_clean)
                if match:
                    valeur = match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        donnees['consommation_kwh'] = float(valeur)
                        print(f"   ✅ Consommation: {donnees['consommation_kwh']} kWh")
                        break
                    except ValueError:
                        continue

            # 2. EXTRACTION DU MONTANT (FCFA)
            # Patterns possibles :
            # - "montant à payer : 12 345 fcfa"
            # - "total : 12345 fcfa"
            # - "12 345 f cfa"
            patterns_montant = [
                r'montant[:\s]+(\d+[\s,.]?\d*)\s*f?cfa',
                r'total[:\s]+(\d+[\s,.]?\d*)\s*f?cfa',
                r'à\s+payer[:\s]+(\d+[\s,.]?\d*)\s*f?cfa',
                r'a\s+payer[:\s]+(\d+[\s,.]?\d*)\s*f?cfa',
                r'(\d+[\s,.]?\d*)\s*f?cfa',
            ]

            for pattern in patterns_montant:
                match = re.search(pattern, texte_clean)
                if match:
                    valeur = match.group(1).replace(' ', '').replace(',', '').replace('.', '')
                    try:
                        donnees['montant_fcfa'] = float(valeur)
                        print(f"   ✅ Montant: {donnees['montant_fcfa']:,.0f} FCFA")
                        break
                    except ValueError:
                        continue

            # 3. EXTRACTION DE LA PÉRIODE
            # Patterns possibles :
            # - "période : janvier 2025"
            # - "du 01/01/2025 au 31/01/2025"
            patterns_periode = [
                r'période[:\s]+([a-zéû]+\s+\d{4})',
                r'periode[:\s]+([a-zéû]+\s+\d{4})',
                r'du\s+(\d{2}/\d{2}/\d{4})\s+au\s+(\d{2}/\d{2}/\d{4})',
            ]

            for pattern in patterns_periode:
                match = re.search(pattern, texte_clean)
                if match:
                    if len(match.groups()) == 2:
                        donnees['periode'] = f"{match.group(1)} au {match.group(2)}"
                    else:
                        donnees['periode'] = match.group(1)
                    print(f"   ✅ Période: {donnees['periode']}")
                    break

            # 4. EXTRACTION DU NUMÉRO DE COMPTEUR
            patterns_compteur = [
                r'compteur[:\s]+(\d+)',
                r'n°\s*compteur[:\s]+(\d+)',
                r'no\s*compteur[:\s]+(\d+)',
            ]

            for pattern in patterns_compteur:
                match = re.search(pattern, texte_clean)
                if match:
                    donnees['numero_compteur'] = match.group(1)
                    print(f"   ✅ Compteur: {donnees['numero_compteur']}")
                    break

            # 5. IDENTIFICATION DU FOURNISSEUR
            fournisseurs = {
                'sbee': ['sbee', 'société béninoise'],
                'cie': ['cie', 'compagnie ivoirienne'],
                'senelec': ['senelec', 'sénégalaise'],
                'eneo': ['eneo', 'cameroun'],
                'sonabel': ['sonabel', 'burkina'],
            }

            for code, keywords in fournisseurs.items():
                for keyword in keywords:
                    if keyword in texte_clean:
                        donnees['fournisseur'] = code.upper()
                        print(f"   ✅ Fournisseur: {donnees['fournisseur']}")
                        break
                if donnees['fournisseur']:
                    break

            # 6. CALCUL DU SCORE DE CONFIANCE
            score = 0
            if donnees['consommation_kwh']:
                score += 40  # Donnée la plus importante
            if donnees['montant_fcfa']:
                score += 30
            if donnees['periode']:
                score += 15
            if donnees['numero_compteur']:
                score += 10
            if donnees['fournisseur']:
                score += 5

            donnees['confiance'] = score

            print(f"\n   📊 Score de confiance: {score}%")

            if score < 40:
                print("   ⚠️  Confiance faible - Vérification manuelle recommandée")
            elif score < 70:
                print("   ⚠️  Confiance moyenne - Vérifier les données extraites")
            else:
                print("   ✅ Confiance élevée - Données fiables")

            return donnees

        except Exception as e:
            print(f"❌ Erreur analyse facture: {e}")
            return None

    def traiter_facture(self, chemin_image):
        """
        Traite une facture complète (extraction + analyse)

        Args:
            chemin_image: Chemin vers l'images de la facture

        Returns:
            dict: Données extraites et analysées
        """
        print("=" * 70)
        print("🔬 TRAITEMENT OCR DE LA FACTURE")
        print("=" * 70)

        # Étape 1 : Extraction du texte
        texte = self.extraire_texte_image(chemin_image)

        if not texte:
            return {
                'success': False,
                'message': 'Impossible d\'extraire le texte de l\'images',
                'donnees': None
            }

        # Étape 2 : Analyse du texte
        donnees = self.analyser_facture_electricite(texte)

        if not donnees:
            return {
                'success': False,
                'message': 'Impossible d\'analyser la facture',
                'donnees': None
            }

        # Étape 3 : Vérification de la qualité
        if donnees['confiance'] < 40:
            return {
                'success': False,
                'message': 'Confiance trop faible - Image de mauvaise qualité ou facture non reconnue',
                'donnees': donnees,
                'texte_brut': texte
            }

        return {
            'success': True,
            'message': f'Extraction réussie (confiance: {donnees["confiance"]}%)',
            'donnees': donnees,
            'texte_brut': texte
        }

    def sauvegarder_donnees_facture(self, batiment_id, donnees_ocr, chemin_image):
        """
        Sauvegarde les données extraites dans la base de données

        Args:
            batiment_id: ID du bâtiment
            donnees_ocr: Données extraites par OCR
            chemin_image: Chemin de l'images de la facture

        Returns:
            bool: True si sauvegardé, False sinon
        """
        try:
            import sqlite3

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE batiments
                SET facture_electricite_path = ?,
                    facture_consommation_kwh = ?,
                    facture_montant_fcfa = ?,
                    facture_ocr_data = ?
                WHERE id = ?
            """, (
                str(chemin_image),
                donnees_ocr.get('consommation_kwh'),
                donnees_ocr.get('montant_fcfa'),
                json.dumps(donnees_ocr, ensure_ascii=False),
                batiment_id
            ))

            conn.commit()
            conn.close()

            print(f"\n✅ Données sauvegardées dans le bâtiment {batiment_id}")
            return True

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False


# ========================================
# TEST DU MODULE
# ========================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DE L'EXTRACTEUR OCR - VOLTIX AUDIT")
    print("=" * 70)

    print("\n⚠️  IMPORTANT - PRÉREQUIS:")
    print("   1. Installer Tesseract OCR")
    print("      Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("      Linux: sudo apt-get install tesseract-ocr")
    print("      Mac: brew install tesseract")
    print()
    print("   2. Installer les packs de langue française")
    print("      Télécharger fra.traineddata et le placer dans tessdata/")
    print()
    print("   3. Configurer le chemin dans le code (ligne 31)")
    print()

    # Créer un extracteur
    extracteur = ExtracteurFacture()

    print("\n" + "=" * 70)
    print("💡 COMMENT TESTER:")
    print("=" * 70)
    print("""
    1. Prends une photo d'une facture d'électricité (claire, bien éclairée)
    2. Sauvegarde-la dans le dossier du projet (ex: test_facture.jpg)
    3. Modifie la ligne ci-dessous pour pointer vers ton images
    4. Lance ce script

    Exemple de code pour tester:

    resultat = extracteur.traiter_facture('test_facture.jpg')

    if resultat['success']:
        print("✅ Extraction réussie!")
        print(f"   Consommation: {resultat['donnees']['consommation_kwh']} kWh")
        print(f"   Montant: {resultat['donnees']['montant_fcfa']} FCFA")
    else:
        print(f"❌ {resultat['message']}")
    """)

    print("\n" + "=" * 70)
    print("📚 RESSOURCES:")
    print("=" * 70)
    print("""
    - Documentation Tesseract: https://tesseract-ocr.github.io/
    - Améliorer la précision: https://nanonets.com/blog/ocr-with-tesseract/
    - Packs de langues: https://github.com/tesseract-ocr/tessdata
    """)

    print("\n" + "=" * 70)
    print("✅ MODULE OCR PRÊT")
    print("=" * 70)
    print("\n💎 Cette fonctionnalité PREMIUM est réservée au plan Entreprise")
    print("   Elle justifie pleinement le tarif de 50 000 FCFA/mois !")
