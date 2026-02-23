"""
VOLTIX AUDIT - Configuration FedaPay
Gestion des paiements mobiles en Afrique de l'Ouest
"""

import os

# ========================================
# CLÉS API FEDAPAY
# ========================================

# MODE SANDBOX (pour les tests)
FEDAPAY_SANDBOX_PUBLIC_KEY = "pk_sandbox__YqkiJGvPLAOIxpWVlsObz3t"
FEDAPAY_SANDBOX_PRIVATE_KEY = "sk_sandbox_F8Tg00nzUoO1PMJaOTH1WBOU"

# MODE LIVE (production - à remplir plus tard)
FEDAPAY_LIVE_PUBLIC_KEY = "pk_live_votre_cle_publique_ici"
FEDAPAY_LIVE_PRIVATE_KEY = "sk_live_votre_cle_privee_ici"

# Mode actif (sandbox ou live)
FEDAPAY_MODE = "sandbox"  # Changer à "live" en production

# Clés actives selon le mode
if FEDAPAY_MODE == "sandbox":
    FEDAPAY_PUBLIC_KEY = FEDAPAY_SANDBOX_PUBLIC_KEY
    FEDAPAY_PRIVATE_KEY = FEDAPAY_SANDBOX_PRIVATE_KEY
else:
    FEDAPAY_PUBLIC_KEY = FEDAPAY_LIVE_PUBLIC_KEY
    FEDAPAY_PRIVATE_KEY = FEDAPAY_LIVE_PRIVATE_KEY

# ========================================
# CONFIGURATION
# ========================================

# Environnement FedaPay
FEDAPAY_ENVIRONMENT = FEDAPAY_MODE  # 'sandbox' ou 'live'

# URL de base
FEDAPAY_API_BASE_URL = "https://sandbox-api.fedapay.com" if FEDAPAY_MODE == "sandbox" else "https://api.fedapay.com"

# Devise
FEDAPAY_CURRENCY = "XOF"  # Franc CFA (XOF) pour Afrique de l'Ouest

# URL de callback (webhook)
# Cette URL sera appelée par FedaPay après chaque paiement
FEDAPAY_WEBHOOK_URL = "https://votre-domaine.com/webhook/fedapay"  # À remplacer en production

# URL de redirection après paiement
FEDAPAY_SUCCESS_URL = "https://votre-domaine.com/paiement/succes"
FEDAPAY_CANCEL_URL = "https://votre-domaine.com/paiement/annule"

# ========================================
# TARIFS DES PLANS (en FCFA)
# ========================================

PRIX_PLANS = {
    'gratuit': 0,
    'pro': 15000,
    'entreprise': 50000
}

# Durée des plans (en jours)
DUREE_PLANS = {
    'gratuit': 9999,  # Illimité
    'pro': 30,
    'entreprise': 30
}

# ========================================
# NUMÉROS DE TEST FEDAPAY (SANDBOX)
# ========================================

# Pour tester en mode sandbox, utilise ces numéros :
NUMEROS_TEST_SANDBOX = {
    'mtn_money_success': '+22997000001',  # Paiement réussi
    'mtn_money_failed': '+22997000002',   # Paiement échoué
    'orange_money_success': '+22501000001',  # Paiement réussi
    'moov_money_success': '+22996000001'  # Paiement réussi
}

# ========================================
# MESSAGES
# ========================================

MESSAGES_PAIEMENT = {
    'en_attente': 'Paiement en cours de traitement...',
    'valide': 'Paiement validé ! Votre plan a été activé.',
    'echoue': 'Le paiement a échoué. Veuillez réessayer.',
    'rembourse': 'Le paiement a été remboursé.'
}
