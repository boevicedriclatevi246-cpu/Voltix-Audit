"""
VOLTIX AUDIT - Tableau de Bord
Dashboard principal de l'application
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from modules.database.db_manager import DatabaseManager
from config.config import APP_NAME


class TableauDeBord(tk.Frame):
    """Tableau de bord principal"""

    def __init__(self, parent, app):
        super().__init__(parent, bg='#f5f5f5')
        self.app = app
        self.db = DatabaseManager()

        self.creer_interface()

    def creer_interface(self):
        """Crée l'interface du tableau de bord"""

        # Barre supérieure
        self.creer_barre_superieure()

        # Container principal
        container = tk.Frame(self, bg='#f5f5f5')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Section bienvenue
        self.creer_section_bienvenue(container)

        # Section statistiques
        self.creer_section_statistiques(container)

        # Section actions rapides
        self.creer_section_actions(container)

        # Section projets récents
        self.creer_section_projets(container)

    def creer_barre_superieure(self):
        """Crée la barre de navigation supérieure"""
        barre = tk.Frame(self, bg='#1a5490', height=70)
        barre.pack(fill='x')
        barre.pack_propagate(False)

        # Logo/Titre
        tk.Label(
            barre,
            text=f"⚡ {APP_NAME}",
            font=('Helvetica', 18, 'bold'),
            fg='white',
            bg='#1a5490'
        ).pack(side='left', padx=20)

        # Infos utilisateur
        frame_user = tk.Frame(barre, bg='#1a5490')
        frame_user.pack(side='right', padx=20)

        tk.Label(
            frame_user,
            text=f"👤 {self.app.utilisateur['nom_complet']}",
            font=('Helvetica', 11),
            fg='white',
            bg='#1a5490'
        ).pack(side='left', padx=10)

        tk.Label(
            frame_user,
            text=f"💎 Plan {self.app.utilisateur['plan'].capitalize()}",
            font=('Helvetica', 10, 'bold'),
            fg='#FFD700',
            bg='#1a5490'
        ).pack(side='left', padx=10)

        # Bouton déconnexion
        btn_deconnexion = tk.Button(
            frame_user,
            text="Déconnexion",
            font=('Helvetica', 9),
            bg='#c0392b',
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.app.deconnexion
        )
        btn_deconnexion.pack(side='left', padx=10, ipadx=10, ipady=5)

    def creer_section_bienvenue(self, parent):
        """Section de bienvenue"""
        frame = tk.Frame(parent, bg='white', relief='raised', bd=1)
        frame.pack(fill='x', pady=(0, 20))

        tk.Label(
            frame,
            text=f"Bienvenue, {self.app.utilisateur['nom_complet'].split()[0]} ! 👋",
            font=('Helvetica', 20, 'bold'),
            fg='#1a5490',
            bg='white'
        ).pack(pady=20, padx=20, anchor='w')

        tk.Label(
            frame,
            text="Que souhaitez-vous faire aujourd'hui ?",
            font=('Helvetica', 12),
            fg='#666',
            bg='white'
        ).pack(pady=(0, 20), padx=20, anchor='w')

    def creer_section_statistiques(self, parent):
        """Section des statistiques"""
        frame = tk.Frame(parent, bg='#f5f5f5')
        frame.pack(fill='x', pady=(0, 20))

        # Récupérer les stats
        projets = self.db.get_projets_utilisateur(self.app.utilisateur['id'])
        nb_projets = len(projets)
        nb_audits_restants = self.app.utilisateur['audits_max_mois'] - self.app.utilisateur['audits_utilises_ce_mois']

        # Cartes de statistiques
        stats = [
            ("📊 Projets", nb_projets, "#3498db"),
            ("✅ Audits restants", nb_audits_restants, "#27ae60"),
            ("💎 Plan", self.app.utilisateur['plan'].capitalize(), "#f39c12")
        ]

        for titre, valeur, couleur in stats:
            self.creer_carte_stat(frame, titre, str(valeur), couleur)

    def creer_carte_stat(self, parent, titre, valeur, couleur):
        """Crée une carte de statistique"""
        carte = tk.Frame(parent, bg='white', relief='raised', bd=1)
        carte.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(
            carte,
            text=titre,
            font=('Helvetica', 11),
            fg='#666',
            bg='white'
        ).pack(pady=(15, 5))

        tk.Label(
            carte,
            text=valeur,
            font=('Helvetica', 24, 'bold'),
            fg=couleur,
            bg='white'
        ).pack(pady=(0, 15))

    def creer_section_actions(self, parent):
        """Section des actions rapides"""
        frame = tk.Frame(parent, bg='#f5f5f5')
        frame.pack(fill='x', pady=(0, 20))

        # Titre
        tk.Label(
            frame,
            text="Actions rapides",
            font=('Helvetica', 14, 'bold'),
            fg='#333',
            bg='#f5f5f5'
        ).pack(anchor='w', pady=(0, 10))

        # Boutons d'action
        frame_boutons = tk.Frame(frame, bg='#f5f5f5')
        frame_boutons.pack(fill='x')

        actions = [
            ("➕ Nouveau projet", self.nouveau_projet, "#27ae60"),
            ("📋 Mes projets", self.mes_projets, "#3498db"),
            ("👤 Mon compte", self.mon_compte, "#95a5a6")
        ]

        for texte, commande, couleur in actions:
            btn = tk.Button(
                frame_boutons,
                text=texte,
                font=('Helvetica', 12, 'bold'),
                bg=couleur,
                fg='white',
                relief='flat',
                cursor='hand2',
                command=commande
            )
            btn.pack(side='left', fill='x', expand=True, padx=5, ipady=15)

    def creer_section_projets(self, parent):
        """Section des projets récents"""
        frame = tk.Frame(parent, bg='white', relief='raised', bd=1)
        frame.pack(fill='both', expand=True)

        # Titre
        tk.Label(
            frame,
            text="Projets récents",
            font=('Helvetica', 14, 'bold'),
            fg='#333',
            bg='white'
        ).pack(anchor='w', pady=15, padx=20)

        # Liste des projets
        projets = self.db.get_projets_utilisateur(self.app.utilisateur['id'])

        if not projets:
            tk.Label(
                frame,
                text="Aucun projet pour le moment.\nCliquez sur 'Nouveau projet' pour commencer !",
                font=('Helvetica', 11),
                fg='#999',
                bg='white'
            ).pack(pady=50)
        else:
            # Afficher les 5 derniers projets
            for projet in projets[:5]:
                self.creer_carte_projet(frame, projet)

    def creer_carte_projet(self, parent, projet):
        """Crée une carte de projet"""
        carte = tk.Frame(parent, bg='#f9f9f9', relief='solid', bd=1)
        carte.pack(fill='x', padx=20, pady=5)

        # Infos
        frame_info = tk.Frame(carte, bg='#f9f9f9')
        frame_info.pack(side='left', fill='both', expand=True, padx=15, pady=10)

        tk.Label(
            frame_info,
            text=projet['nom_projet'],
            font=('Helvetica', 12, 'bold'),
            fg='#333',
            bg='#f9f9f9'
        ).pack(anchor='w')

        tk.Label(
            frame_info,
            text=f"{projet['client_nom']} • {projet['type_batiment']}",
            font=('Helvetica', 9),
            fg='#666',
            bg='#f9f9f9'
        ).pack(anchor='w', pady=(3, 0))

        # Statut
        couleur_statut = {
            'en_cours': '#f39c12',
            'termine': '#27ae60',
            'incomplet': '#e74c3c'
        }

        tk.Label(
            carte,
            text=projet['statut'].replace('_', ' ').capitalize(),
            font=('Helvetica', 9, 'bold'),
            fg='white',
            bg=couleur_statut.get(projet['statut'], '#999'),
            padx=10,
            pady=5
        ).pack(side='right', padx=15)

    def nouveau_projet(self):
        """Crée un nouveau projet"""
        messagebox.showinfo(
            "Nouveau projet",
            "Fonctionnalité en cours de développement...\n"
            "Cette fenêtre ouvrira l'assistant de création de projet."
        )

    def mes_projets(self):
        """Affiche la liste des projets"""
        messagebox.showinfo(
            "Mes projets",
            "Fonctionnalité en cours de développement...\n"
            "Cette fenêtre affichera tous vos projets."
        )

    def mon_compte(self):
        """Affiche les paramètres du compte"""
        messagebox.showinfo(
            "Mon compte",
            "Fonctionnalité en cours de développement...\n"
            "Cette fenêtre affichera vos paramètres de compte."
        )
