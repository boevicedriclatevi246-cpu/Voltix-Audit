"""
VOLTIX AUDIT - Écran de Connexion
Interface de connexion et inscription
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from modules.auth.user_manager import UserManager
from config.config import APP_NAME, PLANS


class EcranConnexion(tk.Frame):
    """Écran de connexion et inscription"""

    def __init__(self, parent, app):
        super().__init__(parent, bg='#f5f5f5')
        self.app = app
        self.user_manager = UserManager()

        self.mode = 'connexion'  # 'connexion' ou 'inscription'

        self.creer_interface()

    def creer_interface(self):
        """Crée l'interface de connexion"""

        # Container central
        container = tk.Frame(self, bg='white', relief='raised', bd=2)
        container.place(relx=0.5, rely=0.5, anchor='center', width=500, height=600)

        # Logo / Titre
        titre = tk.Label(
            container,
            text=f"⚡ {APP_NAME}",
            font=('Helvetica', 28, 'bold'),
            fg='#1a5490',
            bg='white'
        )
        titre.pack(pady=30)

        sous_titre = tk.Label(
            container,
            text="Votre assistant d'audit énergétique",
            font=('Helvetica', 12),
            fg='#666',
            bg='white'
        )
        sous_titre.pack(pady=(0, 30))

        # Frame pour les formulaires
        self.form_frame = tk.Frame(container, bg='white')
        self.form_frame.pack(fill='both', expand=True, padx=40)

        # Afficher le formulaire de connexion par défaut
        self.afficher_formulaire_connexion()

    def afficher_formulaire_connexion(self):
        """Affiche le formulaire de connexion"""
        self.mode = 'connexion'

        # Nettoyer
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        # Email
        tk.Label(
            self.form_frame,
            text="Email",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(10, 5))

        self.email_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1
        )
        self.email_entry.pack(fill='x', ipady=8)

        # Mot de passe
        tk.Label(
            self.form_frame,
            text="Mot de passe",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(20, 5))

        self.password_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1,
            show='●'
        )
        self.password_entry.pack(fill='x', ipady=8)

        # Bouton connexion
        btn_connexion = tk.Button(
            self.form_frame,
            text="Se connecter",
            font=('Helvetica', 12, 'bold'),
            bg='#1a5490',
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.se_connecter
        )
        btn_connexion.pack(fill='x', pady=30, ipady=10)

        # Lien inscription
        frame_inscription = tk.Frame(self.form_frame, bg='white')
        frame_inscription.pack()

        tk.Label(
            frame_inscription,
            text="Pas encore de compte ? ",
            font=('Helvetica', 9),
            bg='white',
            fg='#666'
        ).pack(side='left')

        lien_inscription = tk.Label(
            frame_inscription,
            text="S'inscrire",
            font=('Helvetica', 9, 'bold'),
            bg='white',
            fg='#27ae60',
            cursor='hand2'
        )
        lien_inscription.pack(side='left')
        lien_inscription.bind('<Button-1>', lambda e: self.afficher_formulaire_inscription())

    def afficher_formulaire_inscription(self):
        """Affiche le formulaire d'inscription"""
        self.mode = 'inscription'

        # Nettoyer
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        # Nom complet
        tk.Label(
            self.form_frame,
            text="Nom complet",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(10, 5))

        self.nom_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1
        )
        self.nom_entry.pack(fill='x', ipady=8)

        # Email
        tk.Label(
            self.form_frame,
            text="Email",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(15, 5))

        self.email_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1
        )
        self.email_entry.pack(fill='x', ipady=8)

        # Téléphone
        tk.Label(
            self.form_frame,
            text="Téléphone (optionnel)",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(15, 5))

        self.tel_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1
        )
        self.tel_entry.pack(fill='x', ipady=8)

        # Mot de passe
        tk.Label(
            self.form_frame,
            text="Mot de passe",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(15, 5))

        self.password_entry = tk.Entry(
            self.form_frame,
            font=('Helvetica', 11),
            relief='solid',
            bd=1,
            show='●'
        )
        self.password_entry.pack(fill='x', ipady=8)

        # Plan
        tk.Label(
            self.form_frame,
            text="Plan",
            font=('Helvetica', 10, 'bold'),
            bg='white',
            fg='#333'
        ).pack(anchor='w', pady=(15, 5))

        self.plan_var = tk.StringVar(value='gratuit')

        frame_plans = tk.Frame(self.form_frame, bg='white')
        frame_plans.pack(fill='x', pady=5)

        for plan_code, plan_info in PLANS.items():
            rb = tk.Radiobutton(
                frame_plans,
                text=f"{plan_info['nom']} ({plan_info['prix_mensuel']:,} FCFA/mois)",
                variable=self.plan_var,
                value=plan_code,
                font=('Helvetica', 9),
                bg='white',
                activebackground='white'
            )
            rb.pack(anchor='w', pady=2)

        # Bouton inscription
        btn_inscription = tk.Button(
            self.form_frame,
            text="S'inscrire",
            font=('Helvetica', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            cursor='hand2',
            command=self.s_inscrire
        )
        btn_inscription.pack(fill='x', pady=20, ipady=10)

        # Lien connexion
        frame_connexion = tk.Frame(self.form_frame, bg='white')
        frame_connexion.pack()

        tk.Label(
            frame_connexion,
            text="Déjà un compte ? ",
            font=('Helvetica', 9),
            bg='white',
            fg='#666'
        ).pack(side='left')

        lien_connexion = tk.Label(
            frame_connexion,
            text="Se connecter",
            font=('Helvetica', 9, 'bold'),
            bg='white',
            fg='#1a5490',
            cursor='hand2'
        )
        lien_connexion.pack(side='left')
        lien_connexion.bind('<Button-1>', lambda e: self.afficher_formulaire_connexion())

    def se_connecter(self):
        """Gère la connexion"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return

        # Tenter la connexion
        resultat = self.user_manager.connecter_utilisateur(email, password)

        if resultat['success']:
            messagebox.showinfo("Succès", resultat['message'])
            self.app.connexion_reussie(resultat['user'])
        else:
            messagebox.showerror("Erreur", resultat['message'])

    def s_inscrire(self):
        """Gère l'inscription"""
        nom = self.nom_entry.get().strip()
        email = self.email_entry.get().strip()
        telephone = self.tel_entry.get().strip()
        password = self.password_entry.get()
        plan = self.plan_var.get()

        if not nom or not email or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return

        # Tenter l'inscription
        resultat = self.user_manager.inscrire_utilisateur(
            email=email,
            mot_de_passe=password,
            nom_complet=nom,
            telephone=telephone if telephone else None,
            pays='BJ',
            plan=plan
        )

        if resultat['success']:
            messagebox.showinfo("Succès", resultat['message'])
            self.afficher_formulaire_connexion()
        else:
            messagebox.showerror("Erreur", resultat['message'])
