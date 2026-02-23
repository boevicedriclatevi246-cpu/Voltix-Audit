"""
Script à exécuter chaque 1er du mois pour réinitialiser les compteurs d'audits
À automatiser avec un cron job ou task scheduler
"""

import sqlite3
from config.config import DATABASE_PATH
from datetime import datetime


def reinitialiser_compteurs_audits():
    """Réinitialise les compteurs d'audits de tous les utilisateurs"""

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Réinitialiser tous les compteurs
        cursor.execute("""
            UPDATE utilisateurs 
            SET audits_utilises_ce_mois = 0
        """)

        nb_utilisateurs = cursor.rowcount

        conn.commit()
        conn.close()

        print(f"✅ Compteurs réinitialisés pour {nb_utilisateurs} utilisateur(s)")
        print(f"📅 Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        return True

    except Exception as e:
        print(f"❌ Erreur réinitialisation : {e}")
        return False


if __name__ == '__main__':
    print("🔄 Réinitialisation des compteurs d'audits mensuels...")
    reinitialiser_compteurs_audits()
