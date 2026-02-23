"""
VOLTIX AUDIT - Application Principale Tkinter
Point d'entrée de l'interface utilisateur
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.config import APP_NAME
from interface.ecran_connexion import EcranConnexion
from interface.tableau_de_bord import TableauDeBord


class VoltixAuditApp:
    """Application principale Voltix Audit"""

    def __init__(self):
        # Créer la fenêtre principale
        self.root = tk.Tk()
        self.root.title(f"⚡ {APP_NAME}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Centrer la fenêtre
        self.centrer_fenetre()

        # Style moderne
        self.configurer_style()

        # Utilisateur connecté (None au départ)
        self.utilisateur = None

        # Container principal
        self.container = tk.Frame(self.root)
        self.container.pack(fill='both', expand=True)

        # Afficher l'écran de connexion
        self.afficher_ecran_connexion()

    def centrer_fenetre(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def configurer_style(self):
        """Configure le style de l'application"""
        style = ttk.Style()
        style.theme_use('clam')

        # Couleurs Voltix
        couleur_primaire = '#1a5490'
        couleur_secondaire = '#27ae60'
        couleur_fond = '#f5f5f5'

        # Styles personnalisés
        style.configure('Titre.TLabel',
                        font=('Helvetica', 24, 'bold'),
                        foreground=couleur_primaire)

        style.configure('SousTitre.TLabel',
                        font=('Helvetica', 16, 'bold'),
                        foreground=couleur_primaire)

        style.configure('Normal.TLabel',
                        font=('Helvetica', 10))

        style.configure('Primaire.TButton',
                        font=('Helvetica', 11, 'bold'),
                        background=couleur_primaire,
                        foreground='white')

        style.configure('Secondaire.TButton',
                        font=('Helvetica', 10),
                        background=couleur_secondaire,
                        foreground='white')

    def nettoyer_container(self):
        """Nettoie le container principal"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def afficher_ecran_connexion(self):
        """Affiche l'écran de connexion"""
        self.nettoyer_container()
        ecran = EcranConnexion(self.container, self)
        ecran.pack(fill='both', expand=True)

    def afficher_tableau_de_bord(self):
        """Affiche le tableau de bord"""
        self.nettoyer_container()
        ecran = TableauDeBord(self.container, self)
        ecran.pack(fill='both', expand=True)

    def connexion_reussie(self, utilisateur):
        """Appelé quand la connexion réussit"""
        self.utilisateur = utilisateur
        self.afficher_tableau_de_bord()

    def deconnexion(self):
        """Déconnecte l'utilisateur"""
        reponse = messagebox.askyesno(
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter ?"
        )
        if reponse:
            self.utilisateur = None
            self.afficher_ecran_connexion()

    def run(self):
        """Lance l'application"""
        self.root.mainloop()


# ========================================
# POINT D'ENTRÉE
# ========================================

if __name__ == "__main__":
    app = VoltixAuditApp()
    app.run()
