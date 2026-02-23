"""
Script d'archivage automatique des projets inactifs (Gratuit uniquement)
À exécuter quotidiennement via cron job ou task scheduler
"""

import sqlite3
from datetime import datetime, timedelta
from config.config import DATABASE_PATH


def archiver_projets_inactifs():
    """
    Archive les projets gratuits sans activité depuis 30 jours
    Les projets PRO ne sont jamais archivés
    """

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Date limite (30 jours)
        date_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        print(f"🔍 Recherche de projets inactifs depuis le {date_limite}...")

        # Trouver les projets gratuits inactifs
        cursor.execute("""
            SELECT p.id, p.nom_projet, u.email, u.plan, p.derniere_activite
            FROM projets p
            JOIN utilisateurs u ON p.utilisateur_id = u.id
            WHERE u.plan = 'gratuit'
            AND p.statut != 'archive'
            AND p.derniere_activite < ?
        """, (date_limite,))

        projets_a_archiver = cursor.fetchall()

        if not projets_a_archiver:
            print("✅ Aucun projet à archiver")
            conn.close()
            return

        print(f"📦 {len(projets_a_archiver)} projet(s) à archiver :")

        for projet in projets_a_archiver:
            projet_id, nom, email, plan, derniere_activite = projet
            print(f"   - ID {projet_id}: {nom} ({email}) - Dernière activité: {derniere_activite}")

        # Archiver les projets
        cursor.execute("""
            UPDATE projets 
            SET statut = 'archive'
            WHERE id IN (
                SELECT p.id 
                FROM projets p
                JOIN utilisateurs u ON p.utilisateur_id = u.id
                WHERE u.plan = 'gratuit'
                AND p.statut != 'archive'
                AND p.derniere_activite < ?
            )
        """, (date_limite,))

        nb_archives = cursor.rowcount

        conn.commit()
        conn.close()

        print(f"✅ {nb_archives} projet(s) archivé(s) avec succès")
        print(f"📅 Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        return nb_archives

    except Exception as e:
        print(f"❌ Erreur archivage : {e}")
        import traceback
        traceback.print_exc()
        return 0


if __name__ == '__main__':
    print("🗂️ Archivage automatique des projets inactifs...")
    print("=" * 60)
    archiver_projets_inactifs()

