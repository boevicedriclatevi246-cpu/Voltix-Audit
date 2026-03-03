"""
Script de migration : Ajoute colonnes conformité UEMOA
"""

import sqlite3
from pathlib import Path

db_path = Path('data/voltix_audit.db')

if not db_path.exists():
    print("❌ Base de données introuvable")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("🔄 Migration base de données pour conformité UEMOA...\n")

# ========================================
# TABLE resultats_audits
# ========================================

print("📋 Table resultats_audits:")

# Colonne conforme_uemoa_04 (Directive équipements)
try:
    cursor.execute("ALTER TABLE resultats_audits ADD COLUMN conforme_uemoa_04 INTEGER DEFAULT 0")
    print("   ✅ Colonne conforme_uemoa_04 ajoutée")
except Exception as e:
    print("   ⚠️ conforme_uemoa_04 déjà existante")

# Colonne conforme_uemoa_05 (Directive bâtiment)
try:
    cursor.execute("ALTER TABLE resultats_audits ADD COLUMN conforme_uemoa_05 INTEGER DEFAULT 0")
    print("   ✅ Colonne conforme_uemoa_05 ajoutée")
except Exception as e:
    print("   ⚠️ conforme_uemoa_05 déjà existante")

# Colonne taux_conformite_equipements
try:
    cursor.execute("ALTER TABLE resultats_audits ADD COLUMN taux_conformite_equipements REAL DEFAULT 0")
    print("   ✅ Colonne taux_conformite_equipements ajoutée")
except Exception as e:
    print("   ⚠️ taux_conformite_equipements déjà existante")

# ========================================
# TABLE equipements
# ========================================

print("\n📋 Table equipements:")

# Colonne classe_energetique
try:
    cursor.execute("ALTER TABLE equipements ADD COLUMN classe_energetique TEXT DEFAULT 'B'")
    print("   ✅ Colonne classe_energetique ajoutée")
except Exception as e:
    print("   ⚠️ classe_energetique déjà existante")

# Colonne conforme_uemoa
try:
    cursor.execute("ALTER TABLE equipements ADD COLUMN conforme_uemoa INTEGER DEFAULT 1")
    print("   ✅ Colonne conforme_uemoa ajoutée")
except Exception as e:
    print("   ⚠️ conforme_uemoa déjà existante")

# ========================================
# COMMIT
# ========================================

conn.commit()
conn.close()

print("\n✅ Migration terminée avec succès !")
print("📊 Colonnes ajoutées pour conformité directives UEMOA 04/2020 et 05/2020")
