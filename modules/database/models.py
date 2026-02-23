"""
VOLTIX AUDIT - Modèles de Base de Données
Définition de toutes les tables SQL
"""

# ========================================
# SCHÉMA COMPLET DE LA BASE DE DONNÉES
# ========================================

# Table 1 : UTILISATEURS
SQL_CREATE_UTILISATEURS = """
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    nom_complet TEXT NOT NULL,
    telephone TEXT,
    pays TEXT DEFAULT 'BJ',
    plan TEXT DEFAULT 'gratuit',
    audits_utilises_ce_mois INTEGER DEFAULT 0,
    audits_max_mois INTEGER DEFAULT 3,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_expiration_plan TIMESTAMP,
    statut_paiement TEXT DEFAULT 'actif',
    derniere_connexion TIMESTAMP,
    token_reset_password TEXT,
    CONSTRAINT chk_plan CHECK (plan IN ('gratuit', 'pro', 'entreprise')),
    CONSTRAINT chk_statut CHECK (statut_paiement IN ('actif', 'suspendu', 'expire'))
)
"""

# Table 2 : PROJETS AUDIT
SQL_CREATE_PROJETS = """
CREATE TABLE IF NOT EXISTS projets_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom_projet TEXT NOT NULL,
    client_nom TEXT NOT NULL,
    client_contact TEXT,
    type_batiment TEXT NOT NULL,
    statut TEXT DEFAULT 'en_cours',
    pourcentage_completion INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_derniere_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT chk_statut CHECK (statut IN ('en_cours', 'incomplet', 'termine'))
)
"""

# Table 3 : BÂTIMENTS
SQL_CREATE_BATIMENTS = """
CREATE TABLE IF NOT EXISTS batiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    surface_totale REAL,
    surface_plancher_utile REAL,
    surface_couloirs REAL,
    nombre_paliers INTEGER,
    annee_construction INTEGER,
    latitude REAL,
    longitude REAL,
    orientation_facade TEXT,
    puissance_souscrite REAL,
    puissance_transformateur REAL,
    puissance_groupe_electrogene REAL,
    puissance_onduleur REAL,
    banc_condensateur REAL,
    facture_electricite_path TEXT,
    facture_consommation_kwh REAL,
    facture_montant_fcfa REAL,
    facture_ocr_data TEXT,
    commentaires TEXT,
    FOREIGN KEY (projet_id) REFERENCES projets_audit(id) ON DELETE CASCADE
)
"""

# Table 4 : ÉTAGES
SQL_CREATE_ETAGES = """
CREATE TABLE IF NOT EXISTS etages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batiment_id INTEGER NOT NULL,
    numero_etage INTEGER NOT NULL,
    nom_etage TEXT NOT NULL,
    surface_etage REAL,
    hauteur_sous_plafond REAL DEFAULT 2.8,
    completion_status TEXT DEFAULT 'incomplet',
    pieces_count INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batiment_id) REFERENCES batiments(id) ON DELETE CASCADE,
    CONSTRAINT chk_completion CHECK (completion_status IN ('incomplet', 'complet')),
    UNIQUE (batiment_id, numero_etage)
)
"""

# Table 5 : PIÈCES
SQL_CREATE_PIECES = """
CREATE TABLE IF NOT EXISTS pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etage_id INTEGER NOT NULL,
    type_piece TEXT NOT NULL,
    nom_piece TEXT NOT NULL,
    surface REAL NOT NULL,
    hauteur REAL DEFAULT 2.8,
    longueur REAL,
    largeur REAL,
    volume REAL,
    responsable TEXT,
    nombre_occupants INTEGER DEFAULT 0,
    temperature_consigne REAL,
    temperature_ambiante REAL,
    humidite_relative REAL,
    vitesse_air REAL,
    type_vitrage TEXT DEFAULT 'Simple',
    surface_vitree REAL,
    taux_vitrage REAL,
    niveau_isolation TEXT DEFAULT 'Moyen',
    couleur_murs TEXT,
    a_rideau INTEGER DEFAULT 0,
    a_store INTEGER DEFAULT 0,
    facade_est_temp REAL,
    facade_ouest_temp REAL,
    facade_nord_temp REAL,
    facade_sud_temp REAL,
    plancher_temp REAL,
    plafond_temp REAL,
    eclairement_moyen REAL,
    equipements_count INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etage_id) REFERENCES etages(id) ON DELETE CASCADE,
    CONSTRAINT chk_type_piece CHECK (type_piece IN (
        'bureau', 'salle_reunion', 'toilettes', 'couloir', 'escalier', 
        'hall_accueil', 'cafeteria', 'salle_serveur', 'local_technique', 
        'parking', 'autre'
    ))
)
"""

# Table 6 : CATALOGUE D'ÉQUIPEMENTS (PRÉDÉFINI)
SQL_CREATE_CATALOGUE = """
CREATE TABLE IF NOT EXISTS equipements_catalogue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie TEXT NOT NULL,
    type_specifique TEXT NOT NULL,
    designation TEXT NOT NULL,
    puissance_unitaire REAL NOT NULL,
    caracteristiques_json TEXT,
    actif INTEGER DEFAULT 1,
    CONSTRAINT chk_categorie CHECK (categorie IN (
        'lampe', 'climatiseur', 'ventilateur', 'bureautique', 'autre'
    ))
)
"""

# Table 7 : ÉQUIPEMENTS INSTALLÉS
SQL_CREATE_EQUIPEMENTS = """
CREATE TABLE IF NOT EXISTS equipements_installes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL,
    equipement_catalogue_id INTEGER,
    designation TEXT NOT NULL,
    categorie TEXT NOT NULL,
    type_specifique TEXT,
    puissance_unitaire REAL NOT NULL,
    quantite INTEGER DEFAULT 1,
    puissance_totale REAL,
    repartition TEXT,
    cop REAL,
    btu INTEGER,
    caracteristiques_supplementaires TEXT,
    saisi_manuellement INTEGER DEFAULT 0,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
    FOREIGN KEY (equipement_catalogue_id) REFERENCES equipements_catalogue(id)
)
"""

# Table 8 : GROUPES ÉLECTROGÈNES
SQL_CREATE_GROUPES = """
CREATE TABLE IF NOT EXISTS groupes_electrogenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batiment_id INTEGER NOT NULL,
    numero_groupe INTEGER NOT NULL,
    marque TEXT,
    puissance_kva REAL,
    puissance_kw REAL,
    cos_phi REAL DEFAULT 0.8,
    intensite REAL,
    annee_fabrication INTEGER,
    annee_mise_en_service INTEGER,
    heures_fonctionnement_an REAL,
    energie_produite_kwh REAL,
    consommation_l_kwh REAL,
    charge_desservie TEXT,
    puissance_totale_charge REAL,
    taux_charge_moyen REAL,
    FOREIGN KEY (batiment_id) REFERENCES batiments(id) ON DELETE CASCADE,
    CONSTRAINT chk_numero CHECK (numero_groupe BETWEEN 1 AND 3)
)
"""

# Table 9 : SOLUTIONS ÉNERGÉTIQUES ACTUELLES
SQL_CREATE_SOLUTIONS = """
CREATE TABLE IF NOT EXISTS solutions_actuelles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    utilise_panneaux_solaires INTEGER DEFAULT 0,
    puissance_solaire_kw REAL,
    production_solaire_annuelle_kwh REAL,
    utilise_groupe_electrogene INTEGER DEFAULT 0,
    nombre_groupes INTEGER DEFAULT 0,
    autre_solution TEXT,
    aucune_solution INTEGER DEFAULT 1,
    date_renseignement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projet_id) REFERENCES projets_audit(id) ON DELETE CASCADE
)
"""

# Table 10 : RÉSULTATS D'AUDIT
SQL_CREATE_RESULTATS = """
CREATE TABLE IF NOT EXISTS resultats_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    consommation_totale_kwh_an REAL,
    consommation_par_m2 REAL,
    classe_energie TEXT,
    emissions_co2_kg_an REAL,
    cout_annuel_fcfa REAL,
    cout_mensuel_fcfa REAL,
    potentiel_economie_pourcentage REAL,
    potentiel_economie_fcfa REAL,
    score_performance INTEGER,
    consommation_eclairage_kwh REAL,
    consommation_climatisation_kwh REAL,
    consommation_ventilation_kwh REAL,
    consommation_bureautique_kwh REAL,
    consommation_autres_kwh REAL,
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projet_id) REFERENCES projets_audit(id) ON DELETE CASCADE,
    CONSTRAINT chk_classe CHECK (classe_energie IN ('A', 'B', 'C', 'D', 'E', 'F', 'G'))
)
"""

# Table 11 : RECOMMANDATIONS
SQL_CREATE_RECOMMANDATIONS = """
CREATE TABLE IF NOT EXISTS recommandations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resultat_id INTEGER NOT NULL,
    priorite TEXT NOT NULL,
    categorie TEXT NOT NULL,
    titre TEXT NOT NULL,
    description TEXT NOT NULL,
    economie_estimee_pourcentage REAL,
    economie_estimee_fcfa REAL,
    cout_investissement_fcfa REAL,
    temps_retour_investissement_annees REAL,
    impact_co2_kg REAL,
    FOREIGN KEY (resultat_id) REFERENCES resultats_audit(id) ON DELETE CASCADE,
    CONSTRAINT chk_priorite CHECK (priorite IN ('haute', 'moyenne', 'basse')),
    CONSTRAINT chk_categorie CHECK (categorie IN (
        'isolation', 'equipements', 'renouvelable', 'comportement', 'autre'
    ))
)
"""

# Table 12 : ALERTES DE COMPLÉTION (Système de rappel)
SQL_CREATE_ALERTES = """
CREATE TABLE IF NOT EXISTS alertes_completion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    etage_id INTEGER,
    piece_id INTEGER,
    type_alerte TEXT NOT NULL,
    message TEXT NOT NULL,
    resolu INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projet_id) REFERENCES projets_audit(id) ON DELETE CASCADE,
    FOREIGN KEY (etage_id) REFERENCES etages(id) ON DELETE CASCADE,
    FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE,
    CONSTRAINT chk_type_alerte CHECK (type_alerte IN (
        'etage_vide', 'piece_sans_equipements', 'donnees_manquantes', 
        'facture_manquante', 'solutions_non_renseignees'
    ))
)
"""

# Table 13 : HISTORIQUE DES PAIEMENTS
SQL_CREATE_PAIEMENTS = """
CREATE TABLE IF NOT EXISTS historique_paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    montant_fcfa REAL NOT NULL,
    moyen_paiement TEXT NOT NULL,
    numero_transaction TEXT,
    plan_souscrit TEXT NOT NULL,
    statut_paiement TEXT DEFAULT 'en_attente',
    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_validation TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT chk_statut_paiement CHECK (statut_paiement IN (
        'en_attente', 'valide', 'echoue', 'rembourse'
    ))
)
"""

# ========================================
# INDEX POUR OPTIMISATION
# ========================================

SQL_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON utilisateurs(email)",
    "CREATE INDEX IF NOT EXISTS idx_projets_utilisateur ON projets_audit(utilisateur_id)",
    "CREATE INDEX IF NOT EXISTS idx_projets_statut ON projets_audit(statut)",
    "CREATE INDEX IF NOT EXISTS idx_batiments_projet ON batiments(projet_id)",
    "CREATE INDEX IF NOT EXISTS idx_etages_batiment ON etages(batiment_id)",
    "CREATE INDEX IF NOT EXISTS idx_pieces_etage ON pieces(etage_id)",
    "CREATE INDEX IF NOT EXISTS idx_equipements_piece ON equipements_installes(piece_id)",
    "CREATE INDEX IF NOT EXISTS idx_alertes_projet ON alertes_completion(projet_id)",
    "CREATE INDEX IF NOT EXISTS idx_alertes_resolu ON alertes_completion(resolu)"
]

# ========================================
# LISTE DE TOUTES LES TABLES
# ========================================

ALL_TABLES = [
    SQL_CREATE_UTILISATEURS,
    SQL_CREATE_PROJETS,
    SQL_CREATE_BATIMENTS,
    SQL_CREATE_ETAGES,
    SQL_CREATE_PIECES,
    SQL_CREATE_CATALOGUE,
    SQL_CREATE_EQUIPEMENTS,
    SQL_CREATE_GROUPES,
    SQL_CREATE_SOLUTIONS,
    SQL_CREATE_RESULTATS,
    SQL_CREATE_RECOMMANDATIONS,
    SQL_CREATE_ALERTES,
    SQL_CREATE_PAIEMENTS
]
