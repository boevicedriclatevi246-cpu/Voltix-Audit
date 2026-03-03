"""
VOLTIX AUDIT - Configuration Centrale
Tous les paramètres de l'application
"""

import os
from pathlib import Path

# ========================================
# CHEMINS DE L'APPLICATION
# ========================================

# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Base de données
DATABASE_PATH = BASE_DIR / 'data' / 'voltix_audit.db'

# Rapports PDF
RAPPORTS_DIR = BASE_DIR / 'rapports_pdf'

# Assets (images, icônes)
ASSETS_DIR = BASE_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
ICONS_DIR = ASSETS_DIR / 'icons'

# Créer les dossiers s'ils n'existent pas
for directory in [DATABASE_PATH.parent, RAPPORTS_DIR, IMAGES_DIR, ICONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

import os

# Base de données
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')  # sqlite ou postgresql

if DATABASE_TYPE == 'postgresql':
    DATABASE_URL = os.environ.get('DATABASE_URL')
else:
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'voltix_audit.db')

# ========================================
# INFORMATIONS APPLICATION
# ========================================

APP_NAME = "Voltix Audit"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Application d'audit énergétique pour PME"
APP_AUTHOR = "Voltix Team"

# ========================================
# PLANS FREEMIUM (en FCFA)
# ========================================

PLANS = {
    'gratuit': {
        'nom': 'Gratuit',
        'prix_mensuel': 0,
        'audits_max_mois': 3,
        'batiments_max_par_audit': 1,
        'upload_facture': False,
        'ocr_facture': False,
        'envoi_email': False,
        'support': 'Email (72h)',
        'historique_jours': 30,
        'couleur': '#95A5A6'  # Gris
    },
    'pro': {
        'nom': 'Pro',
        'prix_mensuel': 15000,  # 15 000 FCFA
        'audits_max_mois': 20,
        'batiments_max_par_audit': 5,
        'upload_facture': True,
        'ocr_facture': False,
        'envoi_email': True,
        'support': 'Email prioritaire (24h)',
        'historique_jours': 365,
        'couleur': '#3498DB'  # Bleu
    },
    'entreprise': {
        'nom': 'Entreprise',
        'prix_mensuel': 50000,  # 50 000 FCFA
        'audits_max_mois': -1,  # Illimité
        'batiments_max_par_audit': -1,  # Illimité
        'upload_facture': True,
        'ocr_facture': True,  # Extraction automatique OCR
        'envoi_email': True,
        'support': 'Support dédié',
        'historique_jours': -1,  # Illimité
        'couleur': '#F39C12'  # Orange/Or
    }
}

# ========================================
# TYPES DE BÂTIMENTS
# ========================================

TYPES_BATIMENTS = [
    'Bureaux administratifs',
    'Établissement de santé',
    'Établissement éducatif',
    'Hôtellerie & Restauration',
    'Commerce',
    'Industrie légère',
    'Résidentiel collectif',
    'Entrepôt & Logistique'
]

# ========================================
# TYPES DE PIÈCES
# ========================================

TYPES_PIECES = [
    'Bureau',
    'Salle de réunion',
    'Toilettes',
    'Couloir',
    'Escalier',
    'Hall d\'accueil',
    'Cafétéria',
    'Salle serveur',
    'Local technique',
    'Parking',
    'Autre'
]

# ========================================
# NIVEAUX D'ISOLATION
# ========================================

NIVEAUX_ISOLATION = [
    'Inexistant',
    'Faible',
    'Moyen',
    'Bon',
    'Excellent'
]

# ========================================
# TYPES DE VITRAGE
# ========================================

TYPES_VITRAGE = [
    'Simple',
    'Double',
    'Triple',
    'Aucun'
]

# ========================================
# CLASSES ÉNERGÉTIQUES (DPE)
# ========================================

CLASSES_ENERGIE = {
    'A': {'seuil_max': 50, 'couleur': '#00A84F', 'label': 'Excellent'},
    'B': {'seuil_max': 90, 'couleur': '#50B847', 'label': 'Très bien'},
    'C': {'seuil_max': 150, 'couleur': '#C8D200', 'label': 'Bien'},
    'D': {'seuil_max': 230, 'couleur': '#FFD500', 'label': 'Moyen'},
    'E': {'seuil_max': 330, 'couleur': '#FFAA00', 'label': 'Médiocre'},
    'F': {'seuil_max': 450, 'couleur': '#FF7E00', 'label': 'Mauvais'},
    'G': {'seuil_max': 99999, 'couleur': '#FF0000', 'label': 'Très mauvais'}
}

# ========================================
# FACTEURS DE CALCUL
# ========================================

# Facteurs d'émission CO2 (kg CO2/kWh)
FACTEURS_CO2 = {
    'electricite': 0.079,  # Afrique (mix énergétique)
    'groupe_electrogene': 0.800,  # Diesel
    'solaire': 0.0
}

# Coût moyen électricité FCFA/kWh (à adapter par pays)
COUT_KWH_FCFA = {
    'benin': 110,
    'cote_ivoire': 90,
    'senegal': 100,
    'cameroun': 95,
    'togo': 105,
    'burkina_faso': 115,
    'mali': 100,
    'default': 100
}

# ========================================
# MOYENS DE PAIEMENT MOBILE
# ========================================

MOYENS_PAIEMENT = [
    {
        'nom': 'Orange Money',
        'code': 'orange_money',
        'pays': ['BJ', 'CI', 'SN', 'ML', 'BF', 'TG', 'CM'],
        'icone': '🟠'
    },
    {
        'nom': 'MTN Mobile Money',
        'code': 'mtn_money',
        'pays': ['BJ', 'CI', 'CM', 'GH'],
        'icone': '🟡'
    },
    {
        'nom': 'Moov Money',
        'code': 'moov_money',
        'pays': ['BJ', 'CI', 'TG', 'BF'],
        'icone': '🔵'
    },
    {
        'nom': 'Wave',
        'code': 'wave',
        'pays': ['SN', 'CI', 'BF', 'ML'],
        'icone': '🟢'
    },
    {
        'nom': 'Airtel Money',
        'code': 'airtel_money',
        'pays': ['CM', 'GH'],
        'icone': '🔴'
    }
]

# ========================================
# PARAMÈTRES EMAIL
# ========================================

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # À adapter selon votre service
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'contact@voltixaudit.com',  # À remplacer
    'sender_name': 'Voltix Audit'
}

# ========================================
# PARAMÈTRES OCR (Extraction facture)
# ========================================

OCR_CONFIG = {
    'language': 'fra',  # Français
    'dpi': 300,
    'confidence_min': 60  # Confiance minimale pour extraction
}

# ========================================
# LIMITES SYSTÈME
# ========================================

LIMITES = {
    'max_etages': 50,  # Maximum d'étages par bâtiment
    'max_pieces_par_etage': 200,
    'max_equipements_par_piece': 100,
    'max_taille_fichier_mo': 10,  # Pour upload facture
    'session_timeout_minutes': 30
}

# ========================================
# MESSAGES SYSTÈME
# ========================================

MESSAGES = {
    'bienvenue': f"Bienvenue sur {APP_NAME} ⚡",
    'connexion_reussie': "Connexion réussie !",
    'connexion_echouee': "Email ou mot de passe incorrect",
    'inscription_reussie': "Inscription réussie ! Vous pouvez maintenant vous connecter.",
    'audit_incomplet': "⚠️ Audit incomplet. Veuillez remplir toutes les sections.",
    'limite_atteinte': "Limite d'audits atteinte pour votre plan. Passez au plan supérieur !",
    'sauvegarde_reussie': "✅ Données sauvegardées avec succès",
    'erreur_sauvegarde': "❌ Erreur lors de la sauvegarde"
}

# ========================================
# MODE DEBUG
# ========================================

DEBUG_MODE = True  # Mettre False en production
LOG_LEVEL = 'DEBUG' if DEBUG_MODE else 'INFO'

# ========================================
# TARIFS ÉLECTRICITÉ PAR PAYS (FCFA/kWh)
# ========================================

TARIFS_ELECTRICITE = {
    'BJ': 100,   # Bénin
    'CI': 95,    # Côte d'Ivoire
    'SN': 110,   # Sénégal
    'TG': 105,   # Togo
    'BF': 115,   # Burkina Faso
    'ML': 120,   # Mali
    'NE': 100,   # Niger
    'FR': 150,   # France (pour test)
}

# ========================================
# FACTEUR D'ÉMISSION CO2 (kg CO2/kWh)
# ========================================

FACTEUR_EMISSION_CO2 = {
    'BJ': 0.55,  # Bénin (mix énergétique)
    'CI': 0.50,  # Côte d'Ivoire
    'SN': 0.60,  # Sénégal
    'TG': 0.55,  # Togo
    'BF': 0.65,  # Burkina Faso
    'ML': 0.70,  # Mali
    'NE': 0.75,  # Niger
    'FR': 0.06,  # France (nucléaire)
}
# ========================================
# CONFIGURATION FEDAPAY - MODE PRODUCTION
# ========================================

# INSTRUCTIONS POUR PASSER EN PRODUCTION :
#
# 1. Créer un compte sur https://fedapay.com
# 2. Compléter la vérification KYC (documents d'identité)
# 3. Aller dans Paramètres > Développeurs > Clés API
# 4. Copier votre clé LIVE (commence par sk_live_...)
# 5. Remplacer ci-dessous



# IMPORTANT : En mode PRODUCTION, les paiements sont RÉELS !
# Les utilisateurs paieront vraiment depuis leur Mobile Money
# Passer en PRODUCTION

FEDAPAY_API_KEY = 'sk_sandbox_F8Tg00nzUoO1PMJaOTH1WBOU'  # Récupère depuis FedaPay
FEDAPAY_MODE = 'sandbox'

# Type de base de données
DATABASE_TYPE = 'sqlite'  # ou 'postgresql' en production

# Chemins base de données
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'voltix_audit.db')

# URL PostgreSQL (pour production uniquement)
DATABASE_URL = os.environ.get('DATABASE_URL', None)  # AJOUTE CETTE LIGNE

# Autres configs...

