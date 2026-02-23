"""
VOLTIX AUDIT - Générateur de rapports PDF PROFESSIONNEL
Génère des rapports PDF de 10-20 pages avec graphiques
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import io

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib

    matplotlib.use('Agg')  # Backend sans interface graphique
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class GenerateurPDFPro:
    """Générateur de rapports PDF professionnels"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.rapports_dir = Path(__file__).parent.parent.parent / 'rapports'
        self.rapports_dir.mkdir(exist_ok=True)

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)


    def generer_rapport(self, projet_id, user_plan='gratuit'):
        """
        Génère un rapport PDF professionnel de 10-20 pages

        Args:
            projet_id: ID du projet

        Returns:
            str: Chemin du fichier PDF généré
        """
        if not REPORTLAB_AVAILABLE:
            print("❌ ReportLab non installé")
            return None

        print(f"\n📄 Génération du rapport PDF PROFESSIONNEL pour le projet {projet_id}...")

        try:
            # Récupérer toutes les données
            print("   📊 Récupération des données...")
            donnees = self._recuperer_donnees_completes(projet_id)

            if not donnees:
                print("❌ Données insuffisantes")
                return None

            # Créer le fichier PDF
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            nom_fichier = f"Rapport_Audit_Pro_{projet_id}_{date_str}.pdf"
            chemin_pdf = self.rapports_dir / nom_fichier

            print("   📝 Création du document PDF...")
            doc = SimpleDocTemplate(
                str(chemin_pdf),
                pagesize=A4,
                rightMargin=1.5 * cm,
                leftMargin=1.5 * cm,
                topMargin=1.5 * cm,
                bottomMargin=1.5 * cm
            )

            # Construire le contenu
            story = []
            styles = self._creer_styles()

            # PAGE 1 : Page de garde
            story.extend(self._creer_page_garde(donnees, styles, user_plan))
            story.append(PageBreak())

            # PAGE 2 : Sommaire
            story.extend(self._creer_sommaire(styles))
            story.append(PageBreak())

            # PAGES 3-4 : Synthèse exécutive
            story.extend(self._creer_synthese_executive(donnees, styles))
            story.append(PageBreak())

            # PAGES 5-6 : Caractéristiques du bâtiment
            story.extend(self._creer_caracteristiques_batiment(donnees, styles))
            story.append(PageBreak())

            # PAGES 7-9 : Inventaire des équipements
            story.extend(self._creer_inventaire_equipements(donnees, styles))
            story.append(PageBreak())

            # PAGES 10-11 : Résultats de l'audit
            story.extend(self._creer_resultats_audit(donnees, styles))
            story.append(PageBreak())

            # PAGES 12-17 : Recommandations (1 page par reco)
            story.extend(self._creer_recommandations_detaillees(donnees, styles))

            # PAGES 18-19 : Plan d'action et aides
            story.extend(self._creer_plan_action(donnees, styles))
            story.append(PageBreak())

            # PAGE 20 : Annex
            story.extend(self._creer_annexes(styles))

            # Générer le PDF
            doc.build(story)

            print(f"   ✅ Rapport PDF PROFESSIONNEL généré : {chemin_pdf}")
            print(f"   📄 Nombre de pages : ~15-20 pages")

            return str(chemin_pdf)

        except Exception as e:
            print(f"❌ Erreur génération PDF Pro: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _creer_styles(self):
        """Crée les styles personnalisés"""
        styles = getSampleStyleSheet()

        # Titre principal
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Sous-titre
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#555555'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        # Titre de section
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=15,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Sous-titre de section
        styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#27ae60'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        return styles

    def _creer_page_garde(self, donnees, styles, user_plan='gratuit'):
        """Crée la page de garde avec badge PRO ou filigrane GRATUIT"""
        elements = []

        # Badge PRO en haut à droite (si Pro)
        if user_plan == 'pro':
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors

            badge_data = [['⭐ VOLTIX PRO ⭐']]
            badge_table = Table(badge_data, colWidths=[6 * cm])
            badge_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#58cc02')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 16),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(badge_table)
            elements.append(Spacer(1, 1 * cm))

        # Filigrane pour version gratuite
        if user_plan == 'gratuit':
            elements.append(Paragraph(
                "<para align=center textColor='#cccccc' fontSize=10><i>Version Gratuite</i></para>",
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.5 * cm))

        elements.append(Spacer(1, 3 * cm))

        # Logo images
        import os
        logo_path = 'static/images/logo.png'
        if os.path.exists(logo_path):
            from reportlab.platypus import Image as RLImage
            logo = RLImage(logo_path, width=3 * cm, height=3 * cm)
            elements.append(logo)
            elements.append(Spacer(1, 0.5 * cm))

        elements.append(Paragraph("VOLTIX AUDIT", styles['CustomTitle']))

        elements.append(Spacer(1, 2 * cm))

        # Titre du rapport
        elements.append(Paragraph("RAPPORT D'AUDIT ÉNERGÉTIQUE", styles['SectionTitle']))
        elements.append(Paragraph("Analyse de performance et recommandations", styles['CustomSubtitle']))

        elements.append(Spacer(1, 3 * cm))

        # Informations projet
        projet = donnees['projet']
        info_projet = f"""
        <para align=center>
        <b>Projet :</b> {projet['nom_projet']}<br/>
        <b>Client :</b> {projet['client_nom']}<br/>
        <b>Type de bâtiment :</b> {projet['type_batiment']}<br/>
        <br/>
        <b>Date du rapport :</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Référence :</b> VLTX-{projet['id']}-2026<br/>
        <b>Validité :</b> 5 ans
        </para>
        """

        elements.append(Paragraph(info_projet, styles['Normal']))

        elements.append(Spacer(1, 3 * cm))

        # Pied de page
        footer_text = "Voltix Audit - Expert en efficacité énergétique<br/>www.voltixaudit.com"
        if user_plan == 'gratuit':
            footer_text += "<br/><i style='color: #999999; font-size: 8px;'>Rapport généré avec la version gratuite</i>"

        elements.append(Paragraph(
            f"<para align=center><i>{footer_text}</i></para>",
            styles['Normal']
        ))

        return elements

    def _creer_sommaire(self, styles):
        """Crée le sommaire"""
        elements = []

        elements.append(Paragraph("SOMMAIRE", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        sommaire_data = [
            ['1.', 'Synthèse exécutive', '3'],
            ['2.', 'Caractéristiques du bâtiment', '5'],
            ['3.', 'Inventaire des équipements', '7'],
            ['4.', 'Résultats de l\'audit énergétique', '10'],
            ['5.', 'Recommandations d\'amélioration', '12'],
            ['6.', 'Plan d\'action et financement', '18'],
            ['7.', 'Annexes et mentions légales', '20'],
        ]

        table = Table(sommaire_data, colWidths=[1 * cm, 14 * cm, 2 * cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(table)

        return elements

    def _creer_synthese_executive(self, donnees, styles):
        """Crée la synthèse exécutive"""
        elements = []

        elements.append(Paragraph("1. SYNTHÈSE EXÉCUTIVE", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        resultats = donnees['resultats']

        # Grande étiquette énergétique
        classe = resultats['classe_energie']
        couleurs_classes = {
            'A': '#27ae60', 'B': '#2ecc71', 'C': '#f1c40f',
            'D': '#f39c12', 'E': '#e67e22', 'F': '#e74c3c', 'G': '#c0392b'
        }

        etiquette_html = f"""
        <para align=center fontSize=48 textColor='{couleurs_classes.get(classe, "#999999")}'>
        <b>CLASSE {classe}</b>
        </para>
        """

        elements.append(Paragraph(etiquette_html, styles['Normal']))
        elements.append(Spacer(1, 1 * cm))

        # Tableau récapitulatif
        recap_data = [
            ['INDICATEUR', 'VALEUR'],
            ['Consommation annuelle', f"{resultats['consommation_totale_kwh_an']:,.0f} kWh/an".replace(',', ' ')],
            ['Coût annuel', f"{resultats['cout_annuel_fcfa']:,.0f} FCFA/an".replace(',', ' ')],
            ['Émissions ', f"{resultats['emissions_co2_kg_an']:,.0f} kg C02/an".replace(',', ' ')],
            ['Score de performance', f"{resultats['score_performance']}/100"],
        ]

        table_recap = Table(recap_data, colWidths=[9 * cm, 9 * cm])
        table_recap.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
        ]))

        elements.append(table_recap)
        elements.append(Spacer(1, 1 * cm))

        # Top 3 recommandations
        elements.append(Paragraph("Top 3 des recommandations prioritaires", styles['SubsectionTitle']))
        elements.append(Spacer(1, 0.3 * cm))

        recos = donnees['recommandations'][:3]
        for i, reco in enumerate(recos, 1):
            priorite_color = {'haute': '#e74c3c', 'moyenne': '#f39c12', 'basse': '#3498db'}

            reco_html = f"""
            <para>
            <b>{i}. {reco['titre']}</b><br/>
            Économie estimée : <b>{reco['economie_estimee_fcfa']:,.0f} FCFA/an</b>  |  
            Investissement : {reco['cout_investissement_fcfa']:,.0f} FCFA  |  
            ROI : {reco['temps_retour_annees']:.1f} ans
            </para>
            """.replace(',', ' ')

            elements.append(Paragraph(reco_html, styles['Normal']))
            elements.append(Spacer(1, 0.3 * cm))

        # Économies totales
        economie_totale = sum(r['economie_estimee_fcfa'] for r in donnees['recommandations'])

        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(
            f"<para align=center fontSize=14><b>Potentiel d'économies total : {economie_totale:,.0f} FCFA/an</b></para>".replace(
                ',', ' '),
            styles['Normal']
        ))

        return elements

    def _creer_caracteristiques_batiment(self, donnees, styles):
        """Crée la section caractéristiques"""
        elements = []

        elements.append(Paragraph("2. CARACTÉRISTIQUES DU BÂTIMENT", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        projet = donnees['projet']
        batiment = donnees['batiment']

        # Tableau informations générales
        info_data = [
            ['CARACTÉRISTIQUE', 'VALEUR'],
            ['Nom du projet', projet['nom_projet']],
            ['Client', projet['client_nom']],
            ['Type de bâtiment', projet['type_batiment']],
            ['Surface totale', f"{batiment['surface_totale']} m²"],
            ['Année de construction', str(batiment['annee_construction'] or 'Non renseignée')],
            ['Nombre d\'étages', str(len(donnees['etages']))],
            ['Nombre de pièces', str(len(donnees['pieces']))],
        ]

        table_info = Table(info_data, colWidths=[9 * cm, 9 * cm])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        elements.append(table_info)
        elements.append(Spacer(1, 1 * cm))

        # Répartition des surfaces par étage
        elements.append(Paragraph("Répartition des surfaces par étage", styles['SubsectionTitle']))
        elements.append(Spacer(1, 0.3 * cm))

        etages_data = [['ÉTAGE', 'SURFACE (m²)', 'NOMBRE DE PIÈCES']]

        for etage in donnees['etages']:
            etages_data.append([
                etage['nom_etage'],
                f"{etage['surface_etage']} m²",
                str(etage['pieces_count'])
            ])

        table_etages = Table(etages_data, colWidths=[8 * cm, 5 * cm, 5 * cm])
        table_etages.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))

        elements.append(table_etages)

        return elements

    def _creer_inventaire_equipements(self, donnees, styles):
        """Crée l'inventaire des équipements"""
        elements = []

        elements.append(Paragraph("3. INVENTAIRE DES ÉQUIPEMENTS", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        # Regrouper par catégorie
        equipements_par_cat = {}
        for eq in donnees['equipements']:
            cat = eq['categorie']
            if cat not in equipements_par_cat:
                equipements_par_cat[cat] = []
            equipements_par_cat[cat].append(eq)

        # Tableau pour chaque catégorie
        for categorie, equipements in equipements_par_cat.items():
            elements.append(Paragraph(f"Catégorie : {categorie}", styles['SubsectionTitle']))
            elements.append(Spacer(1, 0.2 * cm))

            eq_data = [['ÉQUIPEMENT', 'QTÉ', 'PUISSANCE', 'LOCALISATION']]

            for eq in equipements:
                eq_data.append([
                    eq['nom_equipement'],
                    str(eq['quantite']),
                    f"{eq['puissance_w']} W",
                    eq['piece_nom'][:20] + '...' if len(eq['piece_nom']) > 20 else eq['piece_nom']
                ])

            table_eq = Table(eq_data, colWidths=[7 * cm, 2 * cm, 3 * cm, 6 * cm])
            table_eq.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))

            elements.append(table_eq)
            elements.append(Spacer(1, 0.5 * cm))

        return elements

    def _creer_resultats_audit(self, donnees, styles):
        """Crée la section résultats"""
        elements = []

        elements.append(Paragraph("4. RÉSULTATS DE L'AUDIT ÉNERGÉTIQUE", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        resultats = donnees['resultats']

        # Grande étiquette
        classe = resultats['classe_energie']
        couleurs = {
            'A': '#27ae60', 'B': '#2ecc71', 'C': '#f1c40f',
            'D': '#f39c12', 'E': '#e67e22', 'F': '#e74c3c', 'G': '#c0392b'
        }

        etiquette = f"""
        <para align=center fontSize=60 textColor='{couleurs.get(classe, "#999")}'>
        <b>{classe}</b>
        </para>
        """

        elements.append(Paragraph(etiquette, styles['Normal']))
        elements.append(Spacer(1, 0.5 * cm))

        # Tableau détaillé
        detail_data = [
            ['INDICATEUR', 'VALEUR', 'UNITÉ'],
            ['Consommation totale', f"{resultats['consommation_totale_kwh_an']:,.0f}".replace(',', ' '), 'kWh/an'],
            ['Coût annuel', f"{resultats['cout_annuel_fcfa']:,.0f}".replace(',', ' '), 'FCFA/an'],
            ['Émissions C02', f"{resultats['emissions_co2_kg_an']:,.0f}".replace(',', ' '), 'kg/an'],
            ['Score performance', str(resultats['score_performance']), '/100'],
        ]

        table_detail = Table(detail_data, colWidths=[7 * cm, 7 * cm, 4 * cm])
        table_detail.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))

        elements.append(table_detail)

        return elements

    def _creer_recommandations_detaillees(self, donnees, styles):
        """Crée les recommandations détaillées"""
        elements = []

        elements.append(Paragraph("5. RECOMMANDATIONS D'AMÉLIORATION", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        for i, reco in enumerate(donnees['recommandations'][:5], 1):
            # Titre avec priorité
            priorite_colors = {'haute': '#e74c3c', 'moyenne': '#f39c12', 'basse': '#3498db'}

            titre_html = f"""
            <para fontSize=14>
            <b>Recommandation {i} : {reco['titre']}</b>
            </para>
            """

            elements.append(Paragraph(titre_html, styles['Normal']))
            elements.append(Paragraph(f"<i>Priorité : {reco['priorite'].upper()}</i>", styles['Normal']))
            elements.append(Spacer(1, 0.3 * cm))

            # Description
            elements.append(Paragraph(reco['description'], styles['Normal']))
            elements.append(Spacer(1, 0.3 * cm))

            # Tableau financier
            finance_data = [
                ['CRITÈRE', 'VALEUR'],
                ['Investissement initial', f"{reco['cout_investissement_fcfa']:,.0f} FCFA".replace(',', ' ')],
                ['Économies annuelles', f"{reco['economie_estimee_fcfa']:,.0f} FCFA/an".replace(',', ' ')],
                ['Temps de retour', f"{reco['temps_retour_annees']:.1f} ans"],
                ['Réduction C02', f"{reco['impact_co2_kg']:,.0f} kg/an".replace(',', ' ')],
            ]

            table_finance = Table(finance_data, colWidths=[9 * cm, 9 * cm])
            table_finance.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(priorite_colors.get(reco['priorite'], '#999'))),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]))

            elements.append(table_finance)
            elements.append(Spacer(1, 0.8 * cm))

            if i < len(donnees['recommandations'][:5]):
                elements.append(PageBreak())

        return elements

    def _creer_plan_action(self, donnees, styles):
        """Crée le plan d'action"""
        elements = []

        elements.append(Paragraph("6. PLAN D'ACTION ET FINANCEMENT", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        # Tableau récapitulatif
        recap_data = [['RECOMMANDATION', 'INVESTISSEMENT', 'ÉCONOMIES/AN', 'ROI']]

        total_invest = 0
        total_eco = 0

        for reco in donnees['recommandations']:
            recap_data.append([
                reco['titre'][:30] + '...' if len(reco['titre']) > 30 else reco['titre'],
                f"{reco['cout_investissement_fcfa']:,.0f}".replace(',', ' '),
                f"{reco['economie_estimee_fcfa']:,.0f}".replace(',', ' '),
                f"{reco['temps_retour_annees']:.1f} ans"
            ])
            total_invest += reco['cout_investissement_fcfa']
            total_eco += reco['economie_estimee_fcfa']

        recap_data.append([
            'TOTAL',
            f"{total_invest:,.0f}".replace(',', ' '),
            f"{total_eco:,.0f}".replace(',', ' '),
            f"{(total_invest / total_eco if total_eco > 0 else 0):.1f} ans"
        ])

        table_recap = Table(recap_data, colWidths=[7 * cm, 4 * cm, 4 * cm, 3 * cm])
        table_recap.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f39c12')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        elements.append(table_recap)
        elements.append(Spacer(1, 1 * cm))

        # Aides financières
        elements.append(Paragraph("Aides financières disponibles", styles['SubsectionTitle']))
        elements.append(Spacer(1, 0.3 * cm))

        aides_html = """
        <para>
        • <b>MaPrimeRénov'</b> : Aide de l'État pour la rénovation énergétique<br/>
        • <b>CEE</b> : Certificats d'Économies d'Énergie<br/>
        • <b>Éco-PTZ</b> : Prêt à taux zéro pour la rénovation énergétique<br/>
        • <b>TVA réduite 5,5%</b> : Sur les travaux de rénovation énergétique<br/>
        • <b>Aides locales</b> : Région, département, commune
        </para>
        """

        elements.append(Paragraph(aides_html, styles['Normal']))

        return elements

    def _creer_annexes(self, styles):
        """Crée les annexes"""
        elements = []

        elements.append(Paragraph("7. ANNEXES ET MENTIONS LÉGALES", styles['SectionTitle']))
        elements.append(Spacer(1, 0.5 * cm))

        # Méthodologie
        elements.append(Paragraph("Méthodologie de calcul", styles['SubsectionTitle']))
        methodo_html = """
        <para>
        Cet audit énergétique a été réalisé selon les normes et méthodologies suivantes :<br/>
        • Calcul des consommations basé sur les caractéristiques des équipements<br/>
        • Classification énergétique selon le référentiel DPE<br/>
        • Facteurs d'émission C02 selon les données régionales<br/>
        • Tarifs électricité basés sur les tarifs nationaux en vigueur
        </para>
        """
        elements.append(Paragraph(methodo_html, styles['Normal']))
        elements.append(Spacer(1, 0.5 * cm))

        # Validité
        elements.append(Paragraph("Validité du rapport", styles['SubsectionTitle']))
        elements.append(Paragraph("Ce rapport est valable 5 ans à compter de sa date d'émission.", styles['Normal']))
        elements.append(Spacer(1, 0.5 * cm))

        # Contact
        elements.append(Paragraph("Contact", styles['SubsectionTitle']))
        contact_html = """
        <para>
        <b>Voltix Audit</b><br/>
        Expert en efficacité énergétique<br/>
        Email : contact@voltixaudit.com<br/>
        Web : www.voltixaudit.com
        </para>
        """
        elements.append(Paragraph(contact_html, styles['Normal']))

        return elements

    def _recuperer_donnees_completes(self, projet_id):
        """Récupère toutes les données nécessaires"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Projet
            cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
            projet_row = cursor.fetchone()

            if not projet_row:
                return None

            projet = {
                'id': projet_row[0],
                'nom_projet': projet_row[2],
                'client_nom': projet_row[3],
                'type_batiment': projet_row[5]
            }

            # Bâtiment
            cursor.execute("SELECT * FROM batiments WHERE projet_id = ?", (projet_id,))
            batiment_row = cursor.fetchone()

            batiment = {
                'id': batiment_row[0],
                'surface_totale': batiment_row[2] or 100,
                'annee_construction': batiment_row[3]
            }

            # Étages
            cursor.execute("""
                SELECT * FROM etages WHERE batiment_id = ? ORDER BY numero_etage
            """, (batiment['id'],))

            etages = []
            for row in cursor.fetchall():
                etages.append({
                    'id': row[0],
                    'nom_etage': row[3],
                    'surface_etage': row[4] or 0,
                    'pieces_count': row[6] or 0
                })

            # Pièces
            cursor.execute("""
                SELECT p.*, e.nom_etage 
                FROM pieces p 
                JOIN etages e ON p.etage_id = e.id 
                WHERE e.batiment_id = ?
            """, (batiment['id'],))

            pieces = []
            for row in cursor.fetchall():
                pieces.append({
                    'id': row[0],
                    'nom_piece': row[2],
                    'type_piece': row[3],
                    'surface_piece': row[4] or 0,
                    'nom_etage': row[-1]
                })

            # Équipements
            cursor.execute("""
                SELECT eq.*, p.nom_piece 
                FROM equipements eq 
                JOIN pieces p ON eq.piece_id = p.id 
                JOIN etages e ON p.etage_id = e.id 
                WHERE e.batiment_id = ?
            """, (batiment['id'],))

            equipements = []
            for row in cursor.fetchall():
                equipements.append({
                    'nom_equipement': row[2],
                    'categorie': row[3],
                    'puissance_w': row[4] or 0,
                    'quantite': row[5] or 1,
                    'piece_nom': row[-1]
                })

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
                'consommation_totale_kwh_an': resultats_row[2] or 0,
                'classe_energie': resultats_row[3] or 'G',
                'emissions_co2_kg_an': resultats_row[4] or 0,
                'cout_annuel_fcfa': resultats_row[5] or 0,
                'score_performance': resultats_row[6] or 0
            }

            # Recommandations
            cursor.execute("""
                SELECT * FROM recommandations 
                WHERE projet_id = ? 
                ORDER BY priorite, economie_estimee_fcfa DESC
            """, (projet_id,))

            recommandations = []
            for row in cursor.fetchall():
                recommandations.append({
                    'categorie': row[2],
                    'titre': row[3],
                    'description': row[4],
                    'priorite': row[5],
                    'economie_estimee_fcfa': row[6] or 0,
                    'cout_investissement_fcfa': row[7] or 0,
                    'temps_retour_annees': row[8] or 0,
                    'impact_co2_kg': row[9] or 0
                })

            conn.close()

            return {
                'projet': projet,
                'batiment': batiment,
                'etages': etages,
                'pieces': pieces,
                'equipements': equipements,
                'resultats': resultats,
                'recommandations': recommandations
            }

        except Exception as e:
            print(f"❌ Erreur récupération données complètes: {e}")
            import traceback
            traceback.print_exc()
            return None
