"""
VOLTIX AUDIT - Générateur de recommandations
Génère des recommandations d'amélioration énergétique
"""

import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH
from modules.calculs.verification_uemoa import verificateur_uemoa

class GenerateurRecommandations:
    """Générateur de recommandations d'amélioration"""

    def __init__(self):
        self.db_path = DATABASE_PATH

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def generer_recommandations_uemoa(self, projet_id):
            """
            Génère recommandations conformes directives UEMOA
            PRIORITÉ ABSOLUE - Ces recommandations passent avant toutes les autres

            Args:
                projet_id: ID du projet

            Returns:
                list: Liste des recommandations de conformité UEMOA
            """
            print(f"   🏷️ Génération recommandations conformité UEMOA...")

            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer les résultats de l'audit
            cursor.execute("""
                SELECT 
                    consommation_kwh_m2_an,
                    classe_energie,
                    conforme_uemoa_04,
                    conforme_uemoa_05,
                    taux_conformite_equipements,
                    surface_totale
                FROM resultats_audits 
                WHERE projet_id = ? 
                ORDER BY date_calcul DESC 
                LIMIT 1
            """, (projet_id,))

            audit_row = cursor.fetchone()

            if not audit_row:
                conn.close()
                return []

            conso_m2, classe, conf_04, conf_05, taux_conf, surface = audit_row

            recos_uemoa = []

            # ========================================
            # DIRECTIVE 04/2020 - ÉQUIPEMENTS
            # ========================================

            if not conf_04 or taux_conf < 80:

                # Analyser les équipements non conformes
                analyse = verificateur_uemoa.analyser_equipements_projet(projet_id)

                # Recommandation 1 : Éclairage LED
                equipements_eclairage_nc = [
                    eq for eq in analyse['equipements_non_conformes']
                    if eq['categorie'] == 'Éclairage'
                ]

                if equipements_eclairage_nc:
                    nb_equipements = sum(eq['quantite'] for eq in equipements_eclairage_nc)
                    economie_totale = sum(eq['economie_kwh_an'] for eq in equipements_eclairage_nc)
                    cout_total = nb_equipements * 5000  # 5000 FCFA par LED

                    recos_uemoa.append({
                        'projet_id': projet_id,
                        'categorie': '🏷️ Conformité UEMOA',
                        'titre': 'OBLIGATOIRE - Passage intégral à l\'éclairage LED',
                        'description': f"""
    📋 DIRECTIVE UEMOA N°04/2020 - ÉTIQUETAGE ÉNERGÉTIQUE

    La Directive UEMOA impose l'utilisation d'équipements performants avec étiquetage énergétique classe A minimum.

    🔍 SITUATION ACTUELLE :
    - {nb_equipements} équipements d'éclairage NON CONFORMES
    - Technologies obsolètes détectées : halogène, incandescent, fluorescent
    - Taux de conformité actuel : {taux_conf:.0f}% (objectif : 80% minimum)

    ⚡ ACTION REQUISE :
    - Remplacer TOUS les éclairages par des LED certifiées classe A+ ou A++
    - Vérifier présence de l'étiquette énergétique sur chaque équipement
    - Privilégier LED avec détecteurs de présence pour les zones de passage

    📊 IMPACT :
    - Réduction consommation éclairage : 70-80%
    - Durée de vie LED : 25 000 à 50 000 heures (vs 1 000h halogène)
    - Réduction maintenance et remplacement

    ⚖️ CONFORMITÉ RÉGLEMENTAIRE :
    Cette action est OBLIGATOIRE pour respecter la Directive UEMOA N°04/2020 
    applicable dans les 8 pays de l'espace UEMOA (Bénin, Burkina Faso, Côte d'Ivoire, 
    Guinée-Bissau, Mali, Niger, Sénégal, Togo).
                        """.strip(),
                        'priorite': 'haute',
                        'economie_estimee_fcfa': economie_totale * 100,  # 100 FCFA/kWh
                        'cout_investissement_fcfa': cout_total,
                        'temps_retour_annees': cout_total / (economie_totale * 100) if economie_totale > 0 else 1.0,
                        'impact_co2_kg': economie_totale * 0.5,
                        'type_recommandation': 'reglementaire_obligatoire',
                        'directive_reference': 'UEMOA 04/2020 Art. 5'
                    })

                # Recommandation 2 : Climatisation performante
                equipements_clim_nc = [
                    eq for eq in analyse['equipements_non_conformes']
                    if eq['categorie'] == 'Climatisation'
                ]

                if equipements_clim_nc:
                    nb_clim = sum(eq['quantite'] for eq in equipements_clim_nc)
                    economie_clim = sum(eq['economie_kwh_an'] for eq in equipements_clim_nc)

                    recos_uemoa.append({
                        'projet_id': projet_id,
                        'categorie': '🏷️ Conformité UEMOA',
                        'titre': 'Climatiseurs haute performance SEER ≥ 3.2',
                        'description': f"""
    📋 DIRECTIVE UEMOA N°05/2020 - EFFICACITÉ ÉNERGÉTIQUE BÂTIMENTS

    La Directive impose un rendement énergétique minimum pour les systèmes de climatisation.

    🔍 SITUATION ACTUELLE :
    - {nb_clim} climatiseur(s) ne respectent pas le seuil SEER 3.2
    - Technologies standard détectées (rendement estimé : SEER 2.5-2.8)

    ⚡ ACTION REQUISE :
    - Remplacer par climatiseurs INVERTER classe A+ minimum
    - Vérifier SEER (Seasonal Energy Efficiency Ratio) ≥ 3.2 sur l'étiquette
    - Installation avec thermostat programmable recommandée

    📊 BÉNÉFICES :
    - Réduction consommation climatisation : 30-40%
    - Confort thermique amélioré (température plus stable)
    - Réduction nuisances sonores (technologie inverter plus silencieuse)

    💡 TECHNOLOGIES RECOMMANDÉES :
    - Climatiseurs split inverter DC
    - Gaz réfrigérant R32 (écologique)
    - Fonction "économie d'énergie" automatique

    ⚖️ CONFORMITÉ :
    Exigence Directive UEMOA N°05/2020 Annexe 2 - Systèmes énergétiques performants
                        """.strip(),
                        'priorite': 'haute',
                        'economie_estimee_fcfa': economie_clim * 100,
                        'cout_investissement_fcfa': nb_clim * 250000,
                        'temps_retour_annees': (nb_clim * 250000) / (economie_clim * 100) if economie_clim > 0 else 4.5,
                        'impact_co2_kg': economie_clim * 0.5,
                        'type_recommandation': 'reglementaire_recommandee',
                        'directive_reference': 'UEMOA 05/2020 Annexe 2'
                    })

            # ========================================
            # DIRECTIVE 05/2020 - BÂTIMENT
            # ========================================

            if not conf_05 or classe in ['D', 'E', 'F', 'G']:

                # Recommandation 3 : Isolation toiture
                if surface:
                    economie_isolation = surface * 50  # 50 kWh/m²/an économisés

                    recos_uemoa.append({
                        'projet_id': projet_id,
                        'categorie': '🏷️ Conformité UEMOA',
                        'titre': 'Isolation thermique de la toiture - Priorité climat tropical',
                        'description': f"""
    📋 DIRECTIVE UEMOA N°05/2020 - PERFORMANCE ÉNERGÉTIQUE BÂTIMENTS

    La Directive fixe des exigences d'isolation adaptées au climat tropical.

    🔍 SITUATION ACTUELLE :
    - Classe énergétique bâtiment : {classe} ({conso_m2:.1f} kWh/m²/an)
    - {'❌ NON CONFORME' if not conf_05 else '⚠️ AMÉLIORATION POSSIBLE'} - Objectif : Classe A, B ou C
    - Surface concernée : {surface:.0f} m²

    ⚡ EXIGENCE UEMOA :
    - Coefficient transmission thermique toiture : U ≤ 0,50 W/m²·K
    - Objectif : Limiter les gains de chaleur par rayonnement solaire

    🏗️ SOLUTIONS RECOMMANDÉES :
    1. Isolation sous toiture :
       • Laine de roche (résistance thermique R ≥ 4 m²·K/W)
       • Polyuréthane projeté (haute performance)
       • Panneaux sandwich isolants

    2. Solutions naturelles adaptées :
       • Fibres végétales locales (paille, bambou traité)
       • Toiture végétalisée (excellent pour climat tropical)

    3. Protection solaire :
       • Peinture réfléchissante claire (cool roof)
       • Débord de toiture augmenté (protection murs)

    📊 IMPACT ATTENDU :
    - Réduction température intérieure : -3 à -5°C
    - Réduction besoin climatisation : -30% minimum
    - Passage classe énergétique : {classe} → B ou C
    - Confort thermique amélioré toute l'année

    💰 FINANCEMENT :
    - Coût moyen : 15 000 FCFA/m²
    - Aides possibles : Programmes efficacité énergétique nationaux
    - Retour sur investissement : 3-4 ans

    ⚖️ CONFORMITÉ :
    Directive UEMOA N°05/2020 Art. 8 - Enveloppe thermique performante
                        """.strip(),
                        'priorite': 'haute',
                        'economie_estimee_fcfa': economie_isolation * 100,
                        'cout_investissement_fcfa': surface * 15000,
                        'temps_retour_annees': (surface * 15000) / (
                                    economie_isolation * 100) if economie_isolation > 0 else 3.0,
                        'impact_co2_kg': economie_isolation * 0.5,
                        'type_recommandation': 'reglementaire_recommandee',
                        'directive_reference': 'UEMOA 05/2020 Art. 8'
                    })

                # Recommandation 4 : Ventilation naturelle
                recos_uemoa.append({
                    'projet_id': projet_id,
                    'categorie': '🏷️ Conformité UEMOA',
                    'titre': 'Optimisation ventilation naturelle - Conception bioclimatique',
                    'description': f"""
    📋 DIRECTIVE UEMOA N°05/2020 - CONCEPTION BIOCLIMATIQUE

    La Directive encourage la conception adaptée au climat tropical pour réduire 
    la dépendance à la climatisation mécanique.

    🌬️ PRINCIPES DIRECTEURS :
    - Favoriser la circulation d'air naturelle (effet venturi)
    - Orientation du bâtiment selon vents dominants
    - Ouvertures opposées pour ventilation traversante

    🏗️ AMÉLIORATIONS RECOMMANDÉES :

    1. Architecture :
       • Augmenter hauteur sous plafond (minimum 3m)
       • Créer ouvertures hautes pour évacuation air chaud
       • Installer claustras/moucharabiehs (ventilation + ombrage)

    2. Équipements passifs :
       • Brises-soleil orientables sur façades Est/Ouest
       • Pergolas végétalisées (ombrage + fraîcheur)
       • Cheminées solaires (aspiration air chaud)

    3. Solutions low-tech :
       • Ventilateurs plafond (brassage d'air = -3°C ressenti)
       • Puits canadien tropical (rafraîchissement air entrant)
       • Végétalisation périphérie (évapotranspiration)

    📊 IMPACT :
    - Réduction température ressentie : -2 à -4°C
    - Réduction utilisation climatisation : 40-50%
    - Amélioration qualité air intérieur
    - Confort naturel sans consommation électrique

    💡 BONUS :
    Ces solutions améliorent aussi la classe énergétique du bâtiment 
    et valorisent le patrimoine immobilier.

    ⚖️ CONFORMITÉ :
    Directive UEMOA N°05/2020 Art. 6 - Conception bioclimatique adaptée au climat
                        """.strip(),
                    'priorite': 'moyenne',
                    'economie_estimee_fcfa': 150000,  # Estimation
                    'cout_investissement_fcfa': 500000,  # Travaux architecturaux
                    'temps_retour_annees': 3.5,
                    'impact_co2_kg': 1500,
                    'type_recommandation': 'reglementaire_recommandee',
                    'directive_reference': 'UEMOA 05/2020 Art. 6'
                })

            # Insérer les recommandations dans la BDD
            for reco in recos_uemoa:
                try:
                    cursor.execute("""
                        INSERT INTO recommandations (
                            projet_id, categorie, titre, description, priorite,
                            economie_estimee_fcfa, cout_investissement_fcfa,
                            temps_retour_annees, impact_co2_kg
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        reco['projet_id'],
                        reco['categorie'],
                        reco['titre'],
                        reco['description'],
                        reco['priorite'],
                        reco['economie_estimee_fcfa'],
                        reco['cout_investissement_fcfa'],
                        reco['temps_retour_annees'],
                        reco['impact_co2_kg']
                    ))
                except Exception as e:
                    print(f"      ⚠️ Erreur insertion recommandation UEMOA: {e}")

            conn.commit()
            conn.close()

            print(f"      ✅ {len(recos_uemoa)} recommandations UEMOA générées")

            return recos_uemoa

    def generer_toutes_recommandations(self, projet_id):
                """
                Génère toutes les recommandations pour un projet
                PRIORITÉ 1 : Recommandations conformité UEMOA

                Args:
                    projet_id: ID du projet

                Returns:
                    list: Liste des recommandations générées
                """
                print(f"\n💡 Génération des recommandations pour le projet {projet_id}...")

                try:
                    # ========================================
                    # PRIORITÉ 1 : CONFORMITÉ UEMOA
                    # ========================================
                    recos_uemoa = self.generer_recommandations_uemoa(projet_id)

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
                        'classe_energie': resultat[4] if len(resultat) > 10 else resultat[3],
                        # Ajusté pour nouvelles colonnes
                        'consommation_totale_kwh_an': resultat[2],
                        'cout_annuel_fcfa': resultat[6] if len(resultat) > 10 else resultat[5]
                    }

                    classe = resultat_dict['classe_energie']
                    consommation = resultat_dict['consommation_totale_kwh_an']
                    cout = resultat_dict['cout_annuel_fcfa']

                    # Liste des recommandations complémentaires (après UEMOA)
                    recommandations = []

                    # ========================================
                    # RECOMMANDATIONS COMPLÉMENTAIRES
                    # ========================================

                    # Recommandation : Panneaux solaires (si économiquement viable)
                    if cout > 500000:  # Si coût annuel > 500k FCFA
                        recommandations.append({
                            'categorie': 'Énergie renouvelable',
                            'titre': 'Installer des panneaux solaires photovoltaïques',
                            'description': """
        Installation d'un système solaire pour couvrir 30-50% des besoins électriques.

        🌞 AVANTAGES :
        - Réduction facture électrique : 30-40%
        - Indépendance énergétique partielle
        - Protection contre hausses tarifs électricité
        - Valorisation du patrimoine immobilier

        📊 DIMENSIONNEMENT RECOMMANDÉ :
        - Puissance crête : 5-10 kWc selon besoins
        - Production estimée : 6 000-12 000 kWh/an
        - Batteries optionnelles (autonomie nocturne)

        💰 FINANCEMENT :
        - Subventions possibles (programmes nationaux)
        - Crédit bancaire "énergie verte"
        - Retour sur investissement : 7-8 ans

        🔧 INSTALLATION :
        - Toiture orientée Sud (optimal)
        - Ombrage minimal requis
        - Entretien : nettoyage panneaux 2 fois/an
                            """.strip(),
                            'priorite': 'moyenne',
                            'economie_estimee_fcfa': cout * 0.40,
                            'cout_investissement_fcfa': 3000000,
                            'temps_retour_annees': 7.5,
                            'impact_co2_kg': consommation * 0.40 * 0.5
                        })

                    # Recommandation : Gestion intelligente de l'énergie
                    recommandations.append({
                        'categorie': 'Automatisation',
                        'titre': 'Système de gestion énergétique intelligent (BMS)',
                        'description': """
        Installation d'un Building Management System (BMS) pour optimiser la consommation.

        🎛️ ÉQUIPEMENTS INCLUS :
        - Détecteurs de présence (éclairage automatique)
        - Thermostats programmables (climatisation optimisée)
        - Contacteurs jour/nuit (appareils non prioritaires)
        - Monitoring temps réel (application mobile)

        📊 FONCTIONNALITÉS :
        - Extinction automatique zones inoccupées
        - Programmation horaires par zone
        - Alertes surconsommation
        - Rapports mensuels automatiques

        💡 ÉCONOMIES TYPIQUES :
        - Éclairage : -20% (extinction automatique)
        - Climatisation : -25% (régulation optimisée)
        - Veille équipements : -100% (coupure complète)

        🔧 INSTALLATION :
        - Compatible installations existantes
        - Configuration personnalisée par zone
        - Formation utilisateurs incluse
                        """.strip(),
                        'priorite': 'moyenne',
                        'economie_estimee_fcfa': cout * 0.15,
                        'cout_investissement_fcfa': 500000,
                        'temps_retour_annees': 3.3,
                        'impact_co2_kg': consommation * 0.15 * 0.5
                    })

                    # Recommandation : Audit thermique détaillé (si classe très mauvaise)
                    if classe in ['F', 'G']:
                        recommandations.append({
                            'categorie': 'Diagnostic',
                            'titre': 'Audit thermique approfondi avec caméra infrarouge',
                            'description': """
        Réaliser un diagnostic thermique complet pour identifier précisément les déperditions.

        🔍 CONTENU DE L'AUDIT :
        - Thermographie infrarouge complète du bâtiment
        - Mesure étanchéité à l'air (test infiltrométrie)
        - Analyse ponts thermiques
        - Mesure températures par zone

        📋 LIVRABLES :
        - Rapport thermique avec images IR
        - Cartographie déperditions thermiques
        - Préconisations priorisées par ROI
        - Simulation gains après travaux

        💰 INVESTISSEMENT :
        - Coût audit : 150 000 - 300 000 FCFA
        - Subventions audit possibles
        - Permet cibler travaux prioritaires

        🎯 BÉNÉFICE :
        Évite travaux inutiles en identifiant précisément les zones à traiter en priorité.
        Optimise le budget rénovation énergétique.
                            """.strip(),
                            'priorite': 'haute',
                            'economie_estimee_fcfa': 0,  # Pas d'économie directe (c'est un diagnostic)
                            'cout_investissement_fcfa': 200000,
                            'temps_retour_annees': 0,  # N/A pour diagnostic
                            'impact_co2_kg': 0
                        })

                    # Recommandation : Chauffe-eau solaire (si usage eau chaude)
                    recommandations.append({
                        'categorie': 'Énergie renouvelable',
                        'titre': 'Chauffe-eau solaire thermique',
                        'description': """
        Installation de panneaux solaires thermiques pour production d'eau chaude sanitaire.

        ☀️ PRINCIPE :
        - Capteurs solaires thermiques sur toiture
        - Ballon stockage eau chaude 200-300L
        - Appoint électrique pour jours nuageux
        - Couverture besoins : 60-80% annuels

        📊 PERFORMANCE :
        - Énergie gratuite et renouvelable
        - Réduction consommation électrique eau chaude : 70%
        - Durée de vie : 20-25 ans
        - Entretien minimal

        💰 ÉCONOMIE :
        - Économie annuelle : 100 000 - 200 000 FCFA
        - Retour sur investissement : 5-6 ans
        - Aides possibles selon pays

        🌍 ENVIRONNEMENT :
        - Réduction CO2 significative
        - Technologie éprouvée et fiable
        - Valorisation patrimoine immobilier

        🔧 DIMENSIONNEMENT :
        - 1m² capteur pour 50L eau chaude/jour
        - Installation 4-6m² selon besoins famille
                        """.strip(),
                        'priorite': 'moyenne',
                        'economie_estimee_fcfa': 150000,
                        'cout_investissement_fcfa': 800000,
                        'temps_retour_annees': 5.3,
                        'impact_co2_kg': 800
                    })

                    # Enregistrer les recommandations complémentaires
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

                    total_recos = len(recos_uemoa) + len(recommandations)
                    print(f"✅ {total_recos} recommandation(s) générée(s)")
                    print(f"   • {len(recos_uemoa)} recommandations conformité UEMOA (priorité)")
                    print(f"   • {len(recommandations)} recommandations complémentaires")

                    return recos_uemoa + recommandations

                except Exception as e:
                    print(f"❌ Erreur génération recommandations: {e}")
                    import traceback
                    traceback.print_exc()
                    return []

