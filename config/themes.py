"""
VOLTIX AUDIT - Thèmes de l'application
Mode clair et mode sombre
"""

# ========================================
# MODE CLAIR (par défaut)
# ========================================

THEME_CLAIR = {
    'nom': 'clair',
    'fond_principal': (1, 1, 1, 1),  # Blanc
    'fond_secondaire': (0.96, 0.96, 0.96, 1),  # Gris très clair
    'fond_carte': (0.98, 0.98, 0.98, 1),
    'texte_principal': (0.1, 0.1, 0.1, 1),  # Noir
    'texte_secondaire': (0.5, 0.5, 0.5, 1),  # Gris
    'texte_hint': (0.6, 0.6, 0.6, 1),  # Gris clair
    'primaire': (0.1, 0.33, 0.56, 1),  # Bleu Voltix
    'secondaire': (0.15, 0.68, 0.38, 1),  # Vert
    'accent': (1, 0.76, 0.03, 1),  # Or/Jaune
    'danger': (0.76, 0.22, 0.17, 1),  # Rouge
    'bordure': (0.8, 0.8, 0.8, 1),  # Gris bordure
    'ombre': (0, 0, 0, 0.1),
}

# ========================================
# MODE SOMBRE
# ========================================

THEME_SOMBRE = {
    'nom': 'sombre',
    'fond_principal': (0.11, 0.11, 0.11, 1),  # Noir doux
    'fond_secondaire': (0.15, 0.15, 0.15, 1),  # Gris très foncé
    'fond_carte': (0.18, 0.18, 0.18, 1),
    'texte_principal': (0.95, 0.95, 0.95, 1),  # Blanc cassé
    'texte_secondaire': (0.65, 0.65, 0.65, 1),  # Gris clair
    'texte_hint': (0.5, 0.5, 0.5, 1),
    'primaire': (0.2, 0.47, 0.75, 1),  # Bleu plus clair
    'secondaire': (0.2, 0.8, 0.5, 1),  # Vert plus vif
    'accent': (1, 0.84, 0.15, 1),  # Or plus vif
    'danger': (0.95, 0.35, 0.3, 1),  # Rouge plus vif
    'bordure': (0.3, 0.3, 0.3, 1),
    'ombre': (0, 0, 0, 0.3),
}

# Thème actif par défaut
THEME_ACTIF = THEME_CLAIR
