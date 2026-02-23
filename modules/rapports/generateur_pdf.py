"""
VOLTIX AUDIT - Générateur de rapports PDF
Génère des rapports PDF professionnels
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab non disponible - Installation recommandée : pip install reportlab")


class GenerateurPDF:
    """Générateur de rapports PDF"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.rapports_dir = Path(__file__).parent.parent.parent / 'rapports'
        self.rapports_dir.mkdir(exist_ok=True)

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def generer_rapport(self, projet_id):
        """
        Génère un rapport PDF complet

        Args:
            projet_id: ID du projet

        Returns:
            str: Chemin du fichier PDF généré
        """
        if not REPORTLAB_AVAILABLE:
            print("❌ ReportLab non installé - impossible de générer le PDF")
            return None

        print(f"\n📄 Génération du rapport PDF pour le projet {projet_id}...")

        try:
            # Récupérer les données
            print("   📊 Récupération des données...")
            donnees = self._recuperer_donnees(projet_id)

            if not donnees:
                print("❌ Impossible de récupérer les données")
                return None

            # Créer le fichier PDF
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            nom_fichier = f"Rapport_Audit_{projet_id}_{date_str}.pdf"
            chemin_pdf = self.rapports_dir / nom_fichier

            print("   📝 Création du document PDF...")
            doc = SimpleDocTemplate(
                str(chemin_pdf),
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm
            )

            # Construire le contenu
            story = []
            styles = getSampleStyleSheet()

            # Titre
            titre_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a5490'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            story.append(Paragraph("⚡ RAPPORT D'AUDIT ÉNERGÉTIQUE", titre_style))
            story.append(Spacer(1, 1 * cm))

            # Informations projet
            story.append(Paragraph(f"<b>Projet :</b> {donnees['projet']['nom_projet']}", styles['Normal']))
            story.append(Paragraph(f"<b>Client :</b> {donnees['projet']['client_nom']}", styles['Normal']))
            story.append(Paragraph(f"<b>Type de bâtiment :</b> {donnees['projet']['type_batiment']}", styles['Normal']))
            story.append(Paragraph(f"<b>Date du rapport :</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
            story.append(Spacer(1, 1 * cm))

            # Résultats principaux
            story.append(Paragraph("<b>RÉSULTATS DE L'AUDIT</b>", styles['Heading2']))
            story.append(Spacer(1, 0.5 * cm))

            resultats = donnees['resultats']

            data_resultats = [
                ['Indicateur', 'Valeur'],
                ['Classe énergétique', resultats['classe_energie']],
                ['Consommation annuelle', f"{resultats['consommation_totale_kwh_an']:,.0f} kWh/an"],
                ['Émissions CO2', f"{resultats['emissions_co2_kg_an']:,.0f} kg/an"],
                ['Coût annuel', f"{resultats['cout_annuel_fcfa']:,.0f} FCFA/an"],
                ['Score de performance', f"{resultats['score_performance']}/100"],
            ]

            table_resultats = Table(data_resultats, colWidths=[8 * cm, 8 * cm])
            table_resultats.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table_resultats)
            story.append(Spacer(1, 1 * cm))

            # Recommandations
            if donnees['recommandations']:
                story.append(Paragraph("<b>RECOMMANDATIONS D'AMÉLIORATION</b>", styles['Heading2']))
                story.append(Spacer(1, 0.5 * cm))

                for i, reco in enumerate(donnees['recommandations'][:5], 1):
                    story.append(Paragraph(f"<b>{i}. {reco['titre']}</b>", styles['Normal']))
                    story.append(Paragraph(reco['description'], styles['Normal']))
                    story.append(Paragraph(
                        f"Économie estimée : {reco['economie_estimee_fcfa']:,.0f} FCFA/an | "
                        f"Investissement : {reco['cout_investissement_fcfa']:,.0f} FCFA | "
                        f"Retour : {reco['temps_retour_annees']:.1f} ans",
                        styles['Normal']
                    ))
                    story.append(Spacer(1, 0.5 * cm))

            # Générer le PDF
            doc.build(story)

            print(f"   ✅ Rapport PDF généré : {chemin_pdf}")
            return str(chemin_pdf)

        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _recuperer_donnees(self, projet_id):
        """Récupère toutes les données nécessaires pour le rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Projet
            cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
            projet_row = cursor.fetchone()

            if not projet_row:
                return None

            projet = {
                'nom_projet': projet_row[2],
                'client_nom': projet_row[3],
                'type_batiment': projet_row[5]
            }

            print("   ✅ Données du projet récupérées")

            # Résultats
            cursor.execute("""
                SELECT * FROM resultats_audits 
                WHERE projet_id = ? 
                ORDER BY date_calcul DESC 
                LIMIT 1
            """, (projet_id,))

            resultats_row = cursor.fetchone()

            if not resultats_row:
                return None

            resultats = {
                'consommation_totale_kwh_an': resultats_row[2],
                'classe_energie': resultats_row[3],
                'emissions_co2_kg_an': resultats_row[4],
                'cout_annuel_fcfa': resultats_row[5],
                'score_performance': resultats_row[6]
            }

            print("   ✅ Résultats d'audit récupérés")

            # Recommandations
            cursor.execute("""
                SELECT * FROM recommandations 
                WHERE projet_id = ? 
                ORDER BY priorite, economie_estimee_fcfa DESC
            """, (projet_id,))

            recommandations_rows = cursor.fetchall()
            recommandations = []

            for row in recommandations_rows:
                recommandations.append({
                    'categorie': row[2],
                    'titre': row[3],
                    'description': row[4],
                    'priorite': row[5],
                    'economie_estimee_fcfa': row[6],
                    'cout_investissement_fcfa': row[7],
                    'temps_retour_annees': row[8]
                })

            conn.close()

            return {
                'projet': projet,
                'resultats': resultats,
                'recommandations': recommandations
            }

        except Exception as e:
            print(f"❌ Erreur récupération données: {e}")
            import traceback
            traceback.print_exc()
            return None
