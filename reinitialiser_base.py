"""
VOLTIX AUDIT - Réinitialisation COMPLÈTE
"""

import os
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

print("\n" + "=" * 70)
print("RÉINITIALISATION COMPLÈTE - VOLTIX AUDIT")
print("=" * 70)

# Chemin de la base
db_path = Path(__file__).parent / 'data' / 'voltix_audit.db'

# Supprimer l'ancienne base
if db_path.exists():
    print(f"\n🗑️  Suppression de l'ancienne base...")
    os.remove(db_path)
    print("✅ Supprimée")

# Créer le dossier data
db_path.parent.mkdir(parents=True, exist_ok=True)

# Créer la connexion
print("\n📦 Création de la base de données...")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Créer TOUTES les tables directement
print("\n🔧 Création des tables...")

# Table 1: utilisateurs
cursor.execute("""
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe_hash TEXT NOT NULL,
    nom_complet TEXT,
    telephone TEXT,
    pays TEXT DEFAULT 'BJ',
    plan TEXT DEFAULT 'gratuit',
    audits_max_mois INTEGER DEFAULT 3,
    audits_utilises_ce_mois INTEGER DEFAULT 0,
    date_expiration_plan TIMESTAMP,
    statut_paiement TEXT DEFAULT 'actif',
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ Table utilisateurs")

# Table 2: projets
cursor.execute("""
CREATE TABLE IF NOT EXISTS projets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    nom_projet TEXT NOT NULL,
    client_nom TEXT,
    client_contact TEXT,
    type_batiment TEXT,
    statut TEXT DEFAULT 'en_cours',
    pourcentage_completion INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
)
""")
print("✅ Table projets")

# Table 3: batiments
cursor.execute("""
CREATE TABLE IF NOT EXISTS batiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    surface_totale REAL,
    annee_construction INTEGER,
    latitude REAL,
    longitude REAL,
    altitude REAL,
    puissance_souscrite REAL,
    type_alimentation TEXT DEFAULT 'reseau',
    FOREIGN KEY (projet_id) REFERENCES projets(id)
)
""")
print("✅ Table batiments")

# Table 4: etages
cursor.execute("""
CREATE TABLE IF NOT EXISTS etages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batiment_id INTEGER NOT NULL,
    numero_etage INTEGER NOT NULL,
    nom_etage TEXT,
    surface_etage REAL,
    hauteur_sous_plafond REAL DEFAULT 2.5,
    pieces_count INTEGER DEFAULT 0,
    equipements_count INTEGER DEFAULT 0,
    puissance_totale_w REAL DEFAULT 0,
    est_complet INTEGER DEFAULT 0,
    FOREIGN KEY (batiment_id) REFERENCES batiments(id)
)
""")
print("✅ Table etages")

# Table 5: pieces
cursor.execute("""
CREATE TABLE IF NOT EXISTS pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etage_id INTEGER NOT NULL,
    nom_piece TEXT NOT NULL,
    type_piece TEXT,
    surface_piece REAL,
    longueur_piece REAL,
    largeur_piece REAL,
    hauteur_plafond REAL DEFAULT 2.5,
    nb_occupants INTEGER DEFAULT 0,
    equipements_count INTEGER DEFAULT 0,
    puissance_totale_w REAL DEFAULT 0,
    FOREIGN KEY (etage_id) REFERENCES etages(id)
)
""")
print("✅ Table pieces")

# Table 6: catalogue_equipements
cursor.execute("""
CREATE TABLE IF NOT EXISTS catalogue_equipements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie TEXT NOT NULL,
    nom TEXT NOT NULL,
    puissance_nominale_w REAL,
    facteur_utilisation REAL DEFAULT 1.0,
    duree_vie_ans INTEGER,
    cout_moyen_fcfa REAL
)
""")
print("✅ Table catalogue_equipements")

# Table 7: equipements
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL,
    nom_equipement TEXT NOT NULL,
    categorie TEXT,
    puissance_w REAL,
    quantite INTEGER DEFAULT 1,
    heures_utilisation_jour REAL DEFAULT 8,
    jours_utilisation_semaine INTEGER DEFAULT 5,
    FOREIGN KEY (piece_id) REFERENCES pieces(id)
)
""")
print("✅ Table equipements")

# Table 8: resultats_audits
cursor.execute("""
CREATE TABLE IF NOT EXISTS resultats_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    consommation_totale_kwh_an REAL,
    classe_energie TEXT,
    emissions_co2_kg_an REAL,
    cout_annuel_fcfa REAL,
    score_performance INTEGER,
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projet_id) REFERENCES projets(id)
)
""")
print("✅ Table resultats_audits")

# Table 9: recommandations
cursor.execute("""
CREATE TABLE IF NOT EXISTS recommandations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    categorie TEXT,
    titre TEXT,
    description TEXT,
    priorite TEXT,
    economie_estimee_fcfa REAL,
    cout_investissement_fcfa REAL,
    temps_retour_annees REAL,
    impact_co2_kg REAL,
    FOREIGN KEY (projet_id) REFERENCES projets(id)
)
""")
print("✅ Table recommandations")

# Table 10 : historique_paiements
cursor.execute("""
CREATE TABLE IF NOT EXISTS historique_paiements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    montant_fcfa REAL,
    moyen_paiement TEXT,
    numero_transaction TEXT,
    plan_souscrit TEXT,
    statut_paiement TEXT,
    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_validation TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
)
""")
print("✅ Table historique_paiements")

# Table 11 : solutions_actuelles
cursor.execute("""
CREATE TABLE IF NOT EXISTS solutions_actuelles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    a_panneaux_solaires INTEGER DEFAULT 0,
    a_chauffe_eau_solaire INTEGER DEFAULT 0,
    a_isolation_renforcee INTEGER DEFAULT 0,
    a_double_vitrage INTEGER DEFAULT 0,
    FOREIGN KEY (projet_id) REFERENCES projets(id)
)
""")
print("✅ Table solutions_actuelles")

# Table 12 : groupes_electrogenes
cursor.execute("""
CREATE TABLE IF NOT EXISTS groupes_electrogenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batiment_id INTEGER NOT NULL,
    puissance_kva REAL,
    type_carburant TEXT,
    heures_utilisation_jour REAL,
    FOREIGN KEY (batiment_id) REFERENCES batiments(id)
)
""")
print("✅ Table groupes_electrogenes")

# Table 13: alertes_completion
cursor.execute("""
CREATE TABLE IF NOT EXISTS alertes_completion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projet_id INTEGER NOT NULL,
    etage_id INTEGER,
    piece_id INTEGER,
    type_alerte TEXT,
    message TEXT,
    resolu INTEGER DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (projet_id) REFERENCES projets(id)
)
""")
print("✅ Table alertes_completion")

conn.commit()

# Remplir le catalogue
print("\n📋 Remplissage du catalogue d'équipements...")

equipements_data = [
    # Éclairage
    ('Éclairage', 'Lampe LED 9W', 9, 0.8, 10, 5000),
    ('Éclairage', 'Lampe LED 18W', 18, 0.8, 10, 8000),
    ('Éclairage', 'Lampe fluorescente 36W', 36, 0.9, 5, 3000),
    ('Éclairage', 'Tube néon 58W', 58, 0.9, 3, 2000),
    ('Éclairage', 'Lampe halogène 50W', 50, 1.0, 2, 1500),

    # Climatisation
    ('Climatisation', 'Climatiseur 9000 BTU', 900, 0.7, 8, 150000),
    ('Climatisation', 'Climatiseur 12000 BTU', 1200, 0.7, 8, 200000),
    ('Climatisation', 'Climatiseur 18000 BTU', 1800, 0.7, 8, 300000),
    ('Climatisation', 'Climatiseur 24000 BTU', 2400, 0.7, 8, 400000),

    # Ventilation
    ('Ventilation', 'Ventilateur sur pied 60W', 60, 0.8, 5, 15000),
    ('Ventilateur plafonnier 75W', 75, 0.8, 7, 25000),
    ('Ventilation', 'Brasseur d\'air 100W', 100, 0.8, 5, 30000),

    # Bureautique
    ('Bureautique', 'Ordinateur portable 65W', 65, 0.6, 5, 250000),
    ('Bureautique', 'Ordinateur fixe 200W', 200, 0.7, 5, 300000),
    ('Bureautique', 'Écran LED 24" 30W', 30, 0.8, 7, 80000),
    ('Bureautique', 'Imprimante laser 400W', 400, 0.3, 5, 150000),
    ('Bureautique', 'Photocopieur 1500W', 1500, 0.4, 7, 500000),

    # Électroménager
    ('Électroménager', 'Réfrigérateur 150W', 150, 1.0, 10, 200000),
    ('Électroménager', 'Micro-ondes 1000W', 1000, 0.3, 5, 50000),
    ('Électroménager', 'Cafetière 800W', 800, 0.2, 3, 20000),
    ('Électroménager', 'Bouilloire 2000W', 2000, 0.1, 3, 15000),
]

cursor.executemany("""
    INSERT INTO catalogue_equipements (categorie, nom, puissance_nominale_w, facteur_utilisation, duree_vie_ans, cout_moyen_fcfa)
    VALUES (?, ?, ?, ?, ?, ?)
""", equipements_data)

conn.commit()
print(f"✅ {len(equipements_data)} équipements ajoutés")

# Créer utilisateur test
print("\n👤 Création utilisateur de test...")
import bcrypt

email = "test@voltixaudit.com"
password = "Test2024!"
nom = "Utilisateur Test"

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor.execute("""
    INSERT INTO utilisateurs (email, mot_de_passe_hash, nom_complet, plan, audits_max_mois)
    VALUES (?, ?, ?, ?, ?)
""", (email, password_hash, nom, 'pro', 20))

conn.commit()
conn.close()

print(f"✅ Utilisateur créé")

print("\n" + "=" * 70)
print("✅ BASE DE DONNÉES RÉINITIALISÉE AVEC SUCCÈS !")
print("=" * 70)

# Vérifier
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
conn.close()

print(f"\n✅ {len(tables)} tables créées :")
for table in tables:
    print(f"   • {table}")

print(f"""
🎉 TOUT EST PRÊT !

📝 Connecte-toi avec :
   📧 Email : test@voltixaudit.com
   🔑 Mot de passe : Test2024!
   💎 Plan : Pro (20 audits/mois)

🚀 Lance l'application :
   python app.py
""")
