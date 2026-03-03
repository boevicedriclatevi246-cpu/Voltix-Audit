"""
Migration complète : Recrée la table resultats_audits avec toutes les colonnes UEMOA
"""

import sqlite3
from pathlib import Path

db_path = Path('data/voltix_audit.db')

if not db_path.exists():
    print("❌ Base de données introuvable")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("🔄 Migration complète UEMOA...\n")

# ========================================
# SAUVEGARDER LES DONNÉES EXISTANTES
# ========================================

print("📦 Sauvegarde des données existantes...")

cursor.execute("SELECT * FROM resultats_audits")
anciens_resultats = cursor.fetchall()

print(f"   ✅ {len(anciens_resultats)} résultat(s) sauvegardé(s)")

# ========================================
# SUPPRIMER ET RECRÉER LA TABLE
# ========================================

print("\n🔨 Recréation de la table resultats_audits...")

cursor.execute("DROP TABLE IF EXISTS resultats_audits")

cursor.execute("""
    CREATE TABLE resultats_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL,
        consommation_totale_kwh_an REAL NOT NULL,
        consommation_kwh_m2_an REAL,
        classe_energie TEXT NOT NULL,
        emissions_co2_kg_an REAL NOT NULL,
        cout_annuel_fcfa REAL NOT NULL,
        score_performance INTEGER NOT NULL,
        surface_totale REAL,
        conforme_uemoa_04 INTEGER DEFAULT 0,
        conforme_uemoa_05 INTEGER DEFAULT 0,
        taux_conformite_equipements REAL DEFAULT 0,
        date_calcul TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (projet_id) REFERENCES projets(id)
    )
""")

print("   ✅ Table recréée avec toutes les colonnes UEMOA")

# ========================================
# RESTAURER LES DONNÉES (avec valeurs par défaut)
# ========================================

if anciens_resultats:
    print(f"\n📥 Restauration des {len(anciens_resultats)} résultat(s)...")

    for row in anciens_resultats:
        # Anciennes colonnes : id, projet_id, consommation_totale, classe, emissions, cout, score, date
        try:
            cursor.execute("""
                INSERT INTO resultats_audits (
                    id, projet_id, consommation_totale_kwh_an, consommation_kwh_m2_an,
                    classe_energie, emissions_co2_kg_an, cout_annuel_fcfa, 
                    score_performance, surface_totale, conforme_uemoa_04, 
                    conforme_uemoa_05, taux_conformite_equipements, date_calcul
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row[0],  # id
                row[1],  # projet_id
                row[2],  # consommation_totale_kwh_an
                row[2] / 100 if row[2] else 0,  # consommation_kwh_m2_an (estimation)
                row[3] if len(row) > 3 else 'G',  # classe_energie
                row[4] if len(row) > 4 else 0,  # emissions_co2_kg_an
                row[5] if len(row) > 5 else 0,  # cout_annuel_fcfa
                row[6] if len(row) > 6 else 50,  # score_performance
                100,  # surface_totale (valeur par défaut)
                0,  # conforme_uemoa_04
                0,  # conforme_uemoa_05
                0,  # taux_conformite_equipements
                row[7] if len(row) > 7 else None  # date_calcul
            ))
            print(f"   ✅ Résultat {row[0]} restauré")
        except Exception as e:
            print(f"   ⚠️ Erreur restauration résultat {row[0]}: {e}")

# ========================================
# TABLE EQUIPEMENTS
# ========================================

print("\n📋 Table equipements:")

try:
    cursor.execute("ALTER TABLE equipements ADD COLUMN classe_energetique TEXT DEFAULT 'B'")
    print("   ✅ Colonne classe_energetique ajoutée")
except:
    print("   ⚠️ classe_energetique déjà existante")

try:
    cursor.execute("ALTER TABLE equipements ADD COLUMN conforme_uemoa INTEGER DEFAULT 1")
    print("   ✅ Colonne conforme_uemoa ajoutée")
except:
    print("   ⚠️ conforme_uemoa déjà existante")

# ========================================
# COMMIT
# ========================================

conn.commit()
conn.close()

print("\n✅ Migration complète terminée avec succès !")
print("📊 Table resultats_audits recréée avec toutes les colonnes UEMOA")
print("\n⚠️ IMPORTANT : Relancez l'application et refaites un audit pour vérifier")
