"""
Configuration de l'application Voltix Audit
"""

import os
from pathlib import Path

# Répertoire de base
BASE_DIR = Path(__file__).parent.parent

# Base de données
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')

if DATABASE_TYPE == 'postgresql':
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASE_PATH = None  # Pas utilisé avec PostgreSQL
else:
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'voltix_audit.db')
    DATABASE_URL = None  # Pas utilisé avec SQLite

# Secret key pour Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'voltix-audit-secret-key-2024-dev')

# Email (désactivé pour le moment)
EMAIL_ENABLED = False
EMAIL_SENDER = 'cedriclawson720@gmail.com'
EMAIL_PASSWORD = None
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# FedaPay
FEDAPAY_PUBLIC_KEY = os.environ.get('FEDAPAY_PUBLIC_KEY', 'pk_sandbox_xxx')
FEDAPAY_SECRET_KEY = os.environ.get('FEDAPAY_SECRET_KEY', 'sk_sandbox_xxx')
FEDAPAY_MODE = os.environ.get('FEDAPAY_MODE', 'sandbox')

# Prix des plans (en FCFA)
PRIX_PLANS = {
    'gratuit': 0,
    'pro': 15000
}

# Limites par plan
LIMITES_PLANS = {
    'gratuit': {
        'audits_max': 3,
        'projets_max': 3
    },
    'pro': {
        'audits_max': 20,
        'projets_max': float('inf')  # Illimité
    }
}
