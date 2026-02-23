"""
VOLTIX AUDIT - Gestionnaire d'Emails
Envoi automatique d'emails professionnels
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.email_config import EMAIL_CONFIG, EMAIL_TEMPLATE_BASE, TYPES_EMAILS


class GestionnaireEmail:
    """Gestionnaire pour l'envoi d'emails"""

    def __init__(self):
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.use_tls = EMAIL_CONFIG['use_tls']
        self.sender_email = EMAIL_CONFIG['sender_email']
        self.sender_password = EMAIL_CONFIG['sender_password']
        self.sender_name = EMAIL_CONFIG['sender_name']

    def envoyer_email(self, destinataire, type_email, donnees, fichier_joint=None):
        """
        Envoie un email

        Args:
            destinataire: Email du destinataire
            type_email: Type d'email (bienvenue, rapport, etc.)
            donnees: Données pour remplir le template
            fichier_joint: Chemin du fichier à joindre (optionnel)

        Returns:
            bool: True si envoyé, False sinon
        """
        try:
            # Récupérer le template
            if type_email not in TYPES_EMAILS:
                print(f"❌ Type d'email inconnu: {type_email}")
                return False

            email_info = TYPES_EMAILS[type_email]
            sujet = email_info['sujet']
            template_content = email_info['template']

            # Remplir le template
            contenu = template_content.format(**donnees)
            html_final = EMAIL_TEMPLATE_BASE.format(content=contenu)

            # Créer le message
            message = MIMEMultipart()
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = destinataire
            message['Subject'] = sujet

            # Ajouter le corps HTML
            message.attach(MIMEText(html_final, 'html'))

            # Ajouter le fichier joint si présent
            if fichier_joint and Path(fichier_joint).exists():
                with open(fichier_joint, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=Path(fichier_joint).name
                    )
                    message.attach(attachment)
                print(f"   📎 Pièce jointe: {Path(fichier_joint).name}")

            # Envoyer l'email
            print(f"\n📧 Envoi d'email...")
            print(f"   À: {destinataire}")
            print(f"   Sujet: {sujet}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"✅ Email envoyé avec succès !")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ Erreur d'authentification SMTP")
            print("💡 Vérifiez votre email et mot de passe dans config/email_config.py")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erreur SMTP: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False

    def envoyer_email_bienvenue(self, utilisateur):
        """Envoie un email de bienvenue"""
        donnees = {
            'nom_complet': utilisateur['nom_complet'],
            'email': utilisateur['email'],
            'plan': utilisateur['plan'].capitalize(),
            'audits_max': utilisateur['audits_max_mois']
        }

        return self.envoyer_email(
            destinataire=utilisateur['email'],
            type_email='bienvenue',
            donnees=donnees
        )

    def envoyer_rapport_pdf(self, utilisateur, projet, resultats, chemin_pdf):
        """Envoie un rapport PDF par email"""
        from config.config import CLASSES_ENERGIE

        classe_info = CLASSES_ENERGIE.get(resultats['classe_energie'], {})

        donnees = {
            'nom_complet': utilisateur['nom_complet'],
            'nom_projet': projet['nom_projet'],
            'classe_energie': resultats['classe_energie'],
            'couleur_classe': classe_info.get('couleur', '#666'),
            'consommation_totale': f"{resultats['consommation_totale_kwh_an']:,.0f}",
            'score': resultats['score_performance'],
            'economie_totale': f"{resultats.get('economie_totale', 0):,.0f}"
        }

        return self.envoyer_email(
            destinataire=utilisateur['email'],
            type_email='rapport',
            donnees=donnees,
            fichier_joint=chemin_pdf
        )

    def envoyer_confirmation_paiement(self, utilisateur, montant, plan, date_expiration):
        """Envoie une confirmation de paiement"""
        from datetime import datetime

        donnees = {
            'nom_complet': utilisateur['nom_complet'],
            'montant': f"{montant:,}",
            'plan': plan.capitalize(),
            'date_activation': datetime.now().strftime('%d/%m/%Y'),
            'date_expiration': date_expiration.strftime('%d/%m/%Y'),
            'audits_max': utilisateur['audits_max_mois']
        }

        return self.envoyer_email(
            destinataire=utilisateur['email'],
            type_email='paiement_valide',
            donnees=donnees
        )

    def envoyer_alerte_expiration(self, utilisateur, jours_restants):
        """Envoie une alerte d'expiration proche"""
        donnees = {
            'nom_complet': utilisateur['nom_complet'],
            'plan': utilisateur['plan'].capitalize(),
            'jours_restants': jours_restants
        }

        return self.envoyer_email(
            destinataire=utilisateur['email'],
            type_email='expiration',
            donnees=donnees
        )

    def envoyer_reset_password(self, utilisateur, token):
        """Envoie un lien de réinitialisation de mot de passe"""
        reset_link = f"https://voltixaudit.com/reset-password?token={token}"

        donnees = {
            'nom_complet': utilisateur['nom_complet'],
            'reset_link': reset_link
        }

        return self.envoyer_email(
            destinataire=utilisateur['email'],
            type_email='reset_password',
            donnees=donnees
        )


# ========================================
# TEST DU MODULE
# ========================================

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DU GESTIONNAIRE D'EMAILS - VOLTIX AUDIT")
    print("=" * 70)

    print("\n⚠️  IMPORTANT:")
    print("   Pour tester l'envoi d'emails, configurez vos identifiants dans:")
    print("   config/email_config.py")
    print()
    print("   📧 Pour Gmail:")
    print("   1. Activez la validation en 2 étapes")
    print("   2. Créez un 'mot de passe d'application'")
    print("   3. Utilisez ce mot de passe dans la config")
    print()

    # Simuler un utilisateur
    utilisateur_test = {
        'nom_complet': 'Test Voltix',
        'email': 'cedriclawson720@gmail.com',  # ← REMPLACE PAR TON EMAIL pour tester
        'plan': 'pro',
        'audits_max_mois': 20
    }

    ge = GestionnaireEmail()

    print("\n1️⃣  Test d'envoi d'email de bienvenue...")
    print(f"   📧 Destinataire: {utilisateur_test['email']}")

    if utilisateur_test['email'] == 'votre-email@example.com':
        print("\n⚠️  Remplacez 'votre-email@example.com' par votre vraie adresse dans le code pour tester !")
    else:
        succes = ge.envoyer_email_bienvenue(utilisateur_test)

        if succes:
            print("\n✅ Email envoyé ! Vérifiez votre boîte de réception.")
        else:
            print("\n❌ Échec de l'envoi. Vérifiez votre configuration SMTP.")

    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70)
    print("\n💡 Une fois configuré, le système enverra automatiquement:")
    print("   - Emails de bienvenue aux nouveaux utilisateurs")
    print("   - Rapports PDF aux clients")
    print("   - Confirmations de paiement")
    print("   - Alertes d'expiration")
