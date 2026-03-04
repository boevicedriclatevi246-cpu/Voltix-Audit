"""
Script d'initialisation de la base de données
À exécuter une seule fois après déploiement
"""

from modules.database.db_manager import db_manager

print("🔄 Initialisation de la base de données...")

try:
    db_manager.creer_toutes_les_tables()
    print("✅ Base de données initialisée avec succès !")
except Exception as e:
    print(f"❌ Erreur : {e}")
