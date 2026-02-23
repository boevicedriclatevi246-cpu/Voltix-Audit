"""
VOLTIX AUDIT - Configuration Email
Paramètres pour l'envoi d'emails
"""

# ========================================
# CONFIGURATION SMTP
# ========================================

# Option 1 : Gmail (Recommandé pour débuter)
EMAIL_CONFIG_GMAIL = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'cedriclawson720@gmail.com',  # À REMPLACER
    'sender_password': 'Yomi@nhox55',  # À REMPLACER
    'sender_name': 'Voltix Audit'
}

# Option 2 : Outlook/Hotmail
EMAIL_CONFIG_OUTLOOK = {
    'smtp_server': 'smtp-mail.outlook.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'cedriclawson720@outlook.com',
    'sender_password': 'Yomi@nhox55',
    'sender_name': 'Voltix Audit'
}

# Option 3 : Service email africain (Orange, etc.)
EMAIL_CONFIG_CUSTOM = {
    'smtp_server': 'smtp.votre-provider.com',
    'smtp_port': 587,
    'use_tls': True,
    'sender_email': 'contact@voltixaudit.com',
    'sender_password': 'votre-mot-de-passe',
    'sender_name': 'Voltix Audit'
}

# Configuration active (Choisir une option)
EMAIL_CONFIG = EMAIL_CONFIG_GMAIL  # ← Utilise Gmail par défaut

# ========================================
# TEMPLATES D'EMAILS
# ========================================

# Template de base HTML
EMAIL_TEMPLATE_BASE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #1a5490 0%, #2c5aa0 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #27ae60;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Voltix Audit</h1>
        <p>Votre assistant d'audit énergétique</p>
    </div>
    <div class="content">
        {content}
    </div>
    <div class="footer">
        <p>© 2025 Voltix Audit - Tous droits réservés</p>
        <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
    </div>
</body>
</html>
"""

# Template : Bienvenue
EMAIL_TEMPLATE_BIENVENUE = """
<h2>Bienvenue sur Voltix Audit ! 🎉</h2>
<p>Bonjour <strong>{nom_complet}</strong>,</p>
<p>Votre compte a été créé avec succès !</p>
<p><strong>Informations de votre compte :</strong></p>
<ul>
    <li>Email : {email}</li>
    <li>Plan : {plan}</li>
    <li>Audits disponibles : {audits_max} par mois</li>
</ul>
<p>Vous pouvez dès maintenant commencer à créer vos audits énergétiques.</p>
<a href="#" class="button">Commencer mon premier audit</a>
<p>Besoin d'aide ? N'hésitez pas à nous contacter.</p>
"""

# Template : Rapport PDF
EMAIL_TEMPLATE_RAPPORT = """
<h2>Votre rapport d'audit est prêt ! 📄</h2>
<p>Bonjour <strong>{nom_complet}</strong>,</p>
<p>Votre rapport d'audit énergétique pour <strong>{nom_projet}</strong> a été généré avec succès.</p>
<p><strong>Résultats clés :</strong></p>
<ul>
    <li>Classe énergétique : <strong style="color: {couleur_classe};">{classe_energie}</strong></li>
    <li>Consommation : {consommation_totale} kWh/an</li>
    <li>Score de performance : {score}/100</li>
    <li>Économies potentielles : {economie_totale} FCFA/an</li>
</ul>
<p>Le rapport PDF complet est disponible en pièce jointe.</p>
<p>Merci d'utiliser Voltix Audit !</p>
"""

# Template : Paiement validé
EMAIL_TEMPLATE_PAIEMENT_VALIDE = """
<h2>Paiement confirmé ! ✅</h2>
<p>Bonjour <strong>{nom_complet}</strong>,</p>
<p>Votre paiement de <strong>{montant} FCFA</strong> a été confirmé avec succès.</p>
<p><strong>Détails de votre abonnement :</strong></p>
<ul>
    <li>Plan : <strong>{plan}</strong></li>
    <li>Date d'activation : {date_activation}</li>
    <li>Date d'expiration : {date_expiration}</li>
    <li>Audits disponibles : {audits_max} par mois</li>
</ul>
<p>Merci de votre confiance !</p>
"""

# Template : Expiration proche
EMAIL_TEMPLATE_EXPIRATION = """
<h2>Votre abonnement expire bientôt ⚠️</h2>
<p>Bonjour <strong>{nom_complet}</strong>,</p>
<p>Votre abonnement <strong>{plan}</strong> expire dans <strong>{jours_restants} jour(s)</strong>.</p>
<p>Pour continuer à profiter de tous les avantages, renouvelez dès maintenant !</p>
<a href="#" class="button">Renouveler mon abonnement</a>
<p>Sans renouvellement, vous serez automatiquement basculé vers le plan gratuit.</p>
"""

# Template : Réinitialisation mot de passe
EMAIL_TEMPLATE_RESET_PASSWORD = """
<h2>Réinitialisation de mot de passe 🔑</h2>
<p>Bonjour <strong>{nom_complet}</strong>,</p>
<p>Vous avez demandé à réinitialiser votre mot de passe.</p>
<p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
<a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
<p><strong>Ce lien expire dans 24 heures.</strong></p>
<p>Si vous n'avez pas fait cette demande, ignorez cet email.</p>
"""

# ========================================
# TYPES D'EMAILS
# ========================================

TYPES_EMAILS = {
    'bienvenue': {
        'sujet': '🎉 Bienvenue sur Voltix Audit !',
        'template': EMAIL_TEMPLATE_BIENVENUE
    },
    'rapport': {
        'sujet': '📄 Votre rapport d\'audit est prêt',
        'template': EMAIL_TEMPLATE_RAPPORT
    },
    'paiement_valide': {
        'sujet': '✅ Paiement confirmé - Voltix Audit',
        'template': EMAIL_TEMPLATE_PAIEMENT_VALIDE
    },
    'expiration': {
        'sujet': '⚠️ Votre abonnement expire bientôt',
        'template': EMAIL_TEMPLATE_EXPIRATION
    },
    'reset_password': {
        'sujet': '🔑 Réinitialisation de mot de passe',
        'template': EMAIL_TEMPLATE_RESET_PASSWORD
    }
}
