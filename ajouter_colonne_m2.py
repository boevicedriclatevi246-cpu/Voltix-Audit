"""
Script pour ajouter les colonnes manquantes dans resultats_audits
"""

import sqlite3

conn = sqlite3.connect('data/voltix_audit.db')
cursor = conn.cursor()

try:
    # Ajouter consommation_kwh_m2_an
    cursor.execute("""
        ALTER TABLE resultats_audits 
        ADD COLUMN consommation_kwh_m2_an REAL
    """)
    print("✅ Colonne consommation_kwh_m2_an ajoutée")
except:
    print("⚠️ Colonne consommation_kwh_m2_an déjà existante")

try:
    # Ajouter surface_totale
    cursor.execute("""
        ALTER TABLE resultats_audits 
        ADD COLUMN surface_totale REAL
    """)
    print("✅ Colonne surface_totale ajoutée")
except:
    print("⚠️ Colonne surface_totale déjà existante")

conn.commit()
conn.close()

print("\n✅ Base de données mise à jour")
