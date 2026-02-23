"""
VOLTIX AUDIT - Gestionnaire d'Utilisateurs
Authentification, inscription, réinitialisation mot de passe
"""

import bcrypt
import re
from datetime import datetime, timedelta
import secrets
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.database.db_manager import DatabaseManager
from config.config import PLANS


class UserManager:
    """Gestionnaire des utilisateurs et authentification"""

    def __init__(self):
        self.db = DatabaseManager()

    # ========================================
    # VALIDATION DES DONNÉES
    # ========================================

    def valider_email(self, email):
        """
        Valide le format d'un email

        Args:
            email: Email à valider

        Returns:
            bool: True si valide, False sinon
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def valider_mot_de_passe(self, mot_de_passe):
        """
        Valide la force d'un mot de passe

        Règles :
        - Au moins 8 caractères
        - Au moins 1 majuscule
        - Au moins 1 minuscule
        - Au moins 1 chiffre

        Args:
            mot_de_passe: Mot de passe à valider

        Returns:
            tuple: (bool, str) - (Valide?, Message d'erreur)
        """
        if len(mot_de_passe) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"

        if not re.search(r'[A-Z]', mot_de_passe):
            return False, "Le mot de passe doit contenir au moins une majuscule"

        if not re.search(r'[a-z]', mot_de_passe):
            return False, "Le mot de passe doit contenir au moins une minuscule"

        if not re.search(r'[0-9]', mot_de_passe):
            return False, "Le mot de passe doit contenir au moins un chiffre"

        return True, "Mot de passe valide"

    def hasher_mot_de_passe(self, mot_de_passe):
        """
        Hash un mot de passe avec bcrypt

        Args:
            mot_de_passe: Mot de passe en clair

        Returns:
            str: Mot de passe hashé
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(mot_de_passe.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verifier_mot_de_passe(self, mot_de_passe, hash_stocke):
        """
        Vérifie qu'un mot de passe correspond au hash

        Args:
            mot_de_passe: Mot de passe en clair
            hash_stocke: Hash stocké en base

        Returns:
            bool: True si correspond, False sinon
        """
        try:
            return bcrypt.checkpw(
                mot_de_passe.encode('utf-8'),
                hash_stocke.encode('utf-8')
            )
        except:
            return False

    # ========================================
    # INSCRIPTION
    # ========================================

    def inscrire_utilisateur(self, email, mot_de_passe, nom_complet,
                             telephone=None, pays='BJ', plan='gratuit'):
        """
        Inscrit un nouvel utilisateur

        Args:
            email: Email de l'utilisateur
            mot_de_passe: Mot de passe en clair
            nom_complet: Nom complet
            telephone: Numéro de téléphone
            pays: Code pays (BJ, CI, SN, etc.)
            plan: Plan choisi ('gratuit', 'pro', 'entreprise')

        Returns:
            dict: {'success': bool, 'message': str, 'user_id': int or None}
        """
        # Validation email
        if not self.valider_email(email):
            return {
                'success': False,
                'message': "Format d'email invalide",
                'user_id': None
            }

        # Vérifier si email existe déjà
        user_existant = self.db.get_utilisateur_by_email(email)
        if user_existant:
            return {
                'success': False,
                'message': "Cet email est déjà utilisé",
                'user_id': None
            }

        # Validation mot de passe
        valide, message = self.valider_mot_de_passe(mot_de_passe)
        if not valide:
            return {
                'success': False,
                'message': message,
                'user_id': None
            }

        # Validation nom complet
        if not nom_complet or len(nom_complet.strip()) < 3:
            return {
                'success': False,
                'message': "Le nom complet doit contenir au moins 3 caractères",
                'user_id': None
            }

        # Validation plan
        if plan not in PLANS:
            return {
                'success': False,
                'message': "Plan invalide",
                'user_id': None
            }

        # Hash du mot de passe
        mot_de_passe_hash = self.hasher_mot_de_passe(mot_de_passe)

        # Création de l'utilisateur
        user_id = self.db.creer_utilisateur(
            email=email,
            mot_de_passe_hash=mot_de_passe_hash,
            nom_complet=nom_complet,
            telephone=telephone,
            pays=pays,
            plan=plan
        )

        if user_id:
            return {
                'success': True,
                'message': "Inscription réussie !",
                'user_id': user_id
            }
        else:
            return {
                'success': False,
                'message': "Erreur lors de l'inscription",
                'user_id': None
            }

    # ========================================
    # CONNEXION
    # ========================================

    def connecter_utilisateur(self, email, mot_de_passe):
        """
        Connecte un utilisateur

        Args:
            email: Email de l'utilisateur
            mot_de_passe: Mot de passe en clair

        Returns:
            dict: {'success': bool, 'message': str, 'user': dict}
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Récupérer l'utilisateur
            cursor.execute("""
                SELECT * FROM utilisateurs WHERE email = ?
            """, (email,))

            user = cursor.fetchone()
            conn.close()

            if not user:
                return {
                    'success': False,
                    'message': 'Email ou mot de passe incorrect'
                }

            # Convertir en dictionnaire
            user_dict = dict(user)

            # Vérifier le mot de passe (utiliser mot_de_passe_hash)
            if not self.verifier_mot_de_passe(mot_de_passe, user_dict['mot_de_passe_hash']):
                return {
                    'success': False,
                    'message': 'Email ou mot de passe incorrect'
                }

            # Vérifier l'expiration du plan
            if user_dict['plan'] != 'gratuit' and user_dict['date_expiration_plan']:
                from datetime import datetime
                date_expiration = datetime.strptime(user_dict['date_expiration_plan'], '%Y-%m-%d %H:%M:%S')
                if datetime.now() > date_expiration:
                    # Plan expiré - rétrograder à gratuit
                    self._retrograder_a_gratuit(user_dict['id'])
                    user_dict['plan'] = 'gratuit'
                    user_dict['audits_max_mois'] = 3
                    user_dict['statut_paiement'] = 'expire'

            return {
                'success': True,
                'message': 'Connexion réussie',
                'user': user_dict
            }

        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Erreur lors de la connexion: {str(e)}'
            }

    # ========================================
    # RÉINITIALISATION MOT DE PASSE
    # ========================================

    def generer_token_reset(self, email):
        """
        Génère un token de réinitialisation de mot de passe

        Args:
            email: Email de l'utilisateur

        Returns:
            dict: {'success': bool, 'message': str, 'token': str or None}
        """
        # Vérifier que l'utilisateur existe
        user = self.db.get_utilisateur_by_email(email)

        if not user:
            # Par sécurité, ne pas révéler que l'email n'existe pas
            return {
                'success': True,
                'message': "Si cet email existe, un lien de réinitialisation a été envoyé",
                'token': None
            }

        # Générer un token sécurisé
        token = secrets.token_urlsafe(32)

        # Stocker le token en base (à implémenter dans db_manager)
        # Pour l'instant, on retourne juste le token

        return {
            'success': True,
            'message': "Un lien de réinitialisation a été envoyé par email",
            'token': token
        }

    def reinitialiser_mot_de_passe(self, email, nouveau_mot_de_passe, token):
        """
        Réinitialise le mot de passe d'un utilisateur

        Args:
            email: Email de l'utilisateur
            nouveau_mot_de_passe: Nouveau mot de passe
            token: Token de réinitialisation

        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Validation du nouveau mot de passe
        valide, message = self.valider_mot_de_passe(nouveau_mot_de_passe)
        if not valide:
            return {
                'success': False,
                'message': message
            }

        # TODO: Vérifier le token en base de données
        # Pour l'instant, version simplifiée

        user = self.db.get_utilisateur_by_email(email)
        if not user:
            return {
                'success': False,
                'message': "Utilisateur introuvable"
            }

        # Hash du nouveau mot de passe
        nouveau_hash = self.hasher_mot_de_passe(nouveau_mot_de_passe)

        # Mise à jour en base (à implémenter dans db_manager)
        # TODO: db.update_mot_de_passe(user['id'], nouveau_hash)

        return {
            'success': True,
            'message': "Mot de passe réinitialisé avec succès"
        }

    # ========================================
    # GESTION DU PLAN
    # ========================================

    def verifier_limite_audits(self, user_id):
        """
        Vérifie si l'utilisateur a atteint sa limite d'audits

        Args:
            user_id: ID de l'utilisateur

        Returns:
            dict: {'peut_creer': bool, 'audits_restants': int, 'message': str}
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Récupérer les infos utilisateur
        cursor.execute("""
            SELECT plan, audits_utilises_ce_mois, audits_max_mois 
            FROM utilisateurs 
            WHERE id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                'peut_creer': False,
                'audits_restants': 0,
                'message': "Utilisateur introuvable"
            }

        plan, utilises, max_audits = row['plan'], row['audits_utilises_ce_mois'], row['audits_max_mois']

        # Plan entreprise = illimité
        if max_audits == -1:
            return {
                'peut_creer': True,
                'audits_restants': -1,  # Illimité
                'message': "Audits illimités"
            }

        # Vérifier la limite
        if utilises >= max_audits:
            return {
                'peut_creer': False,
                'audits_restants': 0,
                'message': f"Limite atteinte ({max_audits} audits/mois). Passez au plan supérieur !"
            }

        restants = max_audits - utilises

        return {
            'peut_creer': True,
            'audits_restants': restants,
            'message': f"{restants} audit(s) restant(s) ce mois"
        }

    def get_info_plan(self, user_id):
        """
        Récupère les informations du plan de l'utilisateur

        Args:
            user_id: ID de l'utilisateur

        Returns:
            dict: Informations complètes du plan
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT plan, audits_utilises_ce_mois, audits_max_mois,
                   date_expiration_plan, statut_paiement
            FROM utilisateurs 
            WHERE id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        plan_nom = row['plan']
        plan_config = PLANS.get(plan_nom, PLANS['gratuit'])

        return {
            'plan_nom': plan_config['nom'],
            'plan_code': plan_nom,
            'prix_mensuel': plan_config['prix_mensuel'],
            'audits_utilises': row['audits_utilises_ce_mois'],
            'audits_max': row['audits_max_mois'],
            'audits_restants': row['audits_max_mois'] - row['audits_utilises_ce_mois'] if row[
                                                                                              'audits_max_mois'] != -1 else -1,
            'date_expiration': row['date_expiration_plan'],
            'statut': row['statut_paiement'],
            'couleur': plan_config['couleur'],
            'fonctionnalites': {
                'upload_facture': plan_config['upload_facture'],
                'ocr_facture': plan_config['ocr_facture'],
                'envoi_email': plan_config['envoi_email'],
                'support': plan_config['support']
            }
        }


# ========================================
# TEST DU MODULE
# ========================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU GESTIONNAIRE D'UTILISATEURS - VOLTIX AUDIT")
    print("=" * 60)

    um = UserManager()

    # Test 1 : Inscription
    print("\n1. Test d'inscription...")
    result = um.inscrire_utilisateur(
        email="test@voltixaudit.com",
        mot_de_passe="Test1234",
        nom_complet="Utilisateur Test",
        telephone="+22997123456",
        pays="BJ",
        plan="gratuit"
    )
    print(f"   Résultat: {result}")

    # Test 2 : Connexion
    print("\n2. Test de connexion...")
    result = um.connecter_utilisateur(
        email="test@voltixaudit.com",
        mot_de_passe="Test1234"
    )
    print(f"   Résultat: {result['success']} - {result['message']}")

    if result['success']:
        user = result['user']
        print(f"   Utilisateur connecté: {user['nom_complet']}")

        # Test 3 : Vérification limite audits
        print("\n3. Test limite d'audits...")
        limite = um.verifier_limite_audits(user['id'])
        print(f"   Résultat: {limite}")

        # Test 4 : Info plan
        print("\n4. Test info plan...")
        info_plan = um.get_info_plan(user['id'])
        print(f"   Plan: {info_plan['plan_nom']}")
        print(f"   Audits restants: {info_plan['audits_restants']}")

    print("\n" + "=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)
