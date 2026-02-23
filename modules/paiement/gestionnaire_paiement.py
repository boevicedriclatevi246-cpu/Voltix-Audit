"""
VOLTIX AUDIT - Gestionnaire de paiements FedaPay
Utilise l'API REST FedaPay directement (compatible Python 3.11)
"""

import requests
import json
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import DATABASE_PATH, FEDAPAY_API_KEY, FEDAPAY_MODE


class GestionnairePaiement:
    """Gestionnaire de paiements via FedaPay API REST"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.api_key = FEDAPAY_API_KEY
        self.mode = FEDAPAY_MODE

        # URLs API selon le mode
        if self.mode == 'sandbox':
            self.base_url = 'https://sandbox-api.fedapay.com/v1'
        else:
            self.base_url = 'https://api.fedapay.com/v1'

        print(f"📱 FedaPay configuré en mode : {self.mode}")
        print(f"🔗 API URL : {self.base_url}")

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _get_headers(self):
        """Retourne les headers pour les requêtes API"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def creer_transaction(self, montant, description, utilisateur_id, plan):
        """
        Crée une transaction FedaPay via API REST

        Args:
            montant: Montant en FCFA
            description: Description du paiement
            utilisateur_id: ID de l'utilisateur
            plan: Plan souscrit (pro, entreprise)

        Returns:
            dict: {'success': bool, 'payment_url': str, 'transaction_id': str}
        """
        try:
            # Récupérer l'email de l'utilisateur
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT email, nom_complet FROM utilisateurs WHERE id = ?", (utilisateur_id,))
            user = cursor.fetchone()
            conn.close()

            if not user:
                return {'success': False, 'message': 'Utilisateur introuvable'}

            email = user[0]
            nom = user[1] or "Client Voltix"
            prenom = nom.split()[0] if ' ' in nom else nom
            nom_famille = nom.split()[-1] if ' ' in nom and len(nom.split()) > 1 else "Audit"

            # URL de callback
            base_url = "http://127.0.0.1:5000"  # Remplacer par ton domaine en production

            # Créer la transaction via API REST
            print(f"💳 Création transaction : {montant} FCFA pour {email}")

            payload = {
                "description": description,
                "amount": int(montant),
                "currency": {
                    "iso": "XOF"
                },
                "callback_url": f"{base_url}/paiement/confirmation",
                "customer": {
                    "email": email,
                    "firstname": prenom,
                    "lastname": nom_famille
                }
            }

            response = requests.post(
                f"{self.base_url}/transactions",
                headers=self._get_headers(),
                json=payload
            )

            if response.status_code not in [200, 201]:
                error_msg = response.json().get('message', 'Erreur inconnue')
                print(f"❌ Erreur API FedaPay : {response.status_code} - {error_msg}")
                return {
                    'success': False,
                    'message': f"Erreur FedaPay : {error_msg}"
                }

            transaction_data = response.json()

            # DEBUG : Afficher la structure de la réponse
            print(f"📋 Structure réponse : {json.dumps(transaction_data, indent=2)}")

            # FedaPay renvoie différents formats selon la version
            # Essayer plusieurs chemins possibles
            transaction_id = None

            if 'v1/transaction' in transaction_data:
                transaction_id = transaction_data['v1/transaction']['id']
            elif 'transaction' in transaction_data:
                transaction_id = transaction_data['transaction']['id']
            elif 'id' in transaction_data:
                transaction_id = transaction_data['id']

            if not transaction_id:
                print(f"❌ Impossible de trouver l'ID de transaction dans : {transaction_data}")
                return {
                    'success': False,
                    'message': "Structure de réponse inattendue"
                }

            print(f"✅ Transaction créée : {transaction_id}")

            # Enregistrer dans la base de données
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO historique_paiements (
                    utilisateur_id, montant_fcfa, moyen_paiement, 
                    numero_transaction, plan_souscrit, statut_paiement
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                utilisateur_id,
                montant,
                'FedaPay',
                str(transaction_id),
                plan,
                'en_attente'
            ))

            conn.commit()
            conn.close()

            # Générer le token de paiement
            print(f"🔑 Génération du token pour transaction {transaction_id}...")

            token_response = requests.post(
                f"{self.base_url}/transactions/{transaction_id}/token",
                headers=self._get_headers()
            )

            if token_response.status_code not in [200, 201]:
                print(f"❌ Erreur génération token : {token_response.status_code}")
                print(f"📋 Réponse : {token_response.text}")
                return {
                    'success': False,
                    'message': "Erreur lors de la génération du lien de paiement"
                }

            token_data = token_response.json()

            # DEBUG : Afficher la structure du token
            print(f"📋 Structure token : {json.dumps(token_data, indent=2)}")

            # Essayer plusieurs chemins possibles pour l'URL
            payment_url = None

            if 'v1/transaction' in token_data and 'token' in token_data['v1/transaction']:
                payment_url = token_data['v1/transaction']['token']['url']
            elif 'transaction' in token_data and 'token' in token_data['transaction']:
                payment_url = token_data['transaction']['token']['url']
            elif 'token' in token_data and 'url' in token_data['token']:
                payment_url = token_data['token']['url']
            elif 'url' in token_data:
                payment_url = token_data['url']

            if not payment_url:
                print(f"❌ Impossible de trouver l'URL de paiement dans : {token_data}")
                return {
                    'success': False,
                    'message': "URL de paiement introuvable"
                }

            print(f"🔗 URL de paiement : {payment_url}")

            return {
                'success': True,
                'payment_url': payment_url,
                'transaction_id': transaction_id,
                'message': 'Transaction créée'
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau : {e}")
            return {
                'success': False,
                'message': f"Erreur de connexion : {str(e)}"
            }
        except KeyError as e:
            print(f"❌ Erreur structure réponse : {e}")
            print(
                f"📋 Données reçues : {json.dumps(token_data if 'token_data' in locals() else transaction_data, indent=2)}")
            return {
                'success': False,
                'message': f"Structure de réponse inattendue : {str(e)}"
            }
        except Exception as e:
            print(f"❌ Erreur création transaction : {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f"Erreur technique : {str(e)}"
            }

    def verifier_paiement(self, transaction_id, utilisateur_id):
        """
        Vérifie le statut d'une transaction via API REST

        Args:
            transaction_id: ID de la transaction FedaPay
            utilisateur_id: ID de l'utilisateur

        Returns:
            dict: {'success': bool, 'message': str, 'plan': str}
        """
        try:
            print(f"🔍 Vérification transaction : {transaction_id}")

            # Récupérer la transaction depuis l'API
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=self._get_headers()
            )

            if response.status_code != 200:
                print(f"❌ Erreur récupération transaction : {response.status_code}")
                return {
                    'success': False,
                    'message': "Transaction introuvable sur FedaPay"
                }

            transaction_data = response.json()
            transaction = transaction_data['v1/transaction']
            status = transaction['status']

            print(f"📊 Statut transaction : {status}")

            conn = self.get_connection()
            cursor = conn.cursor()

            # Récupérer le plan depuis la BDD
            cursor.execute("""
                SELECT plan_souscrit FROM historique_paiements 
                WHERE numero_transaction = ? AND utilisateur_id = ?
            """, (str(transaction_id), utilisateur_id))

            result = cursor.fetchone()

            if not result:
                conn.close()
                return {'success': False, 'message': 'Transaction introuvable dans la base'}

            plan = result[0]

            # Vérifier le statut
            if status == 'approved':
                # Paiement réussi
                print(f"✅ Paiement approuvé pour le plan {plan}")

                # Mettre à jour le statut dans historique_paiements
                cursor.execute("""
                    UPDATE historique_paiements 
                    SET statut_paiement = 'valide', date_validation = CURRENT_TIMESTAMP
                    WHERE numero_transaction = ?
                """, (str(transaction_id),))

                # Déterminer le nombre d'audits selon le plan (UNIQUEMENT pro)
                audits_max = {
                    'pro': 20
                }
                # Calculer la date d'expiration (30 jours)
                date_expiration = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

                # Mettre à jour le plan de l'utilisateur
                cursor.execute("""
                    UPDATE utilisateurs 
                    SET plan = ?,
                        audits_max_mois = ?,
                        audits_utilises_ce_mois = 0,
                        date_expiration_plan = ?,
                        statut_paiement = 'actif'
                    WHERE id = ?
                """, (plan, audits_max.get(plan, 20), date_expiration, utilisateur_id))

                conn.commit()
                conn.close()

                print(f"✅ Plan {plan} activé jusqu'au {date_expiration}")

                return {
                    'success': True,
                    'message': 'Paiement validé avec succès',
                    'plan': plan
                }

            elif status in ['declined', 'canceled', 'cancelled']:
                # Paiement refusé ou annulé
                cursor.execute("""
                    UPDATE historique_paiements 
                    SET statut_paiement = 'refuse'
                    WHERE numero_transaction = ?
                """, (str(transaction_id),))

                conn.commit()
                conn.close()

                return {'success': False, 'message': f'Paiement {status}'}

            else:
                # Paiement en attente
                conn.close()
                return {'success': False, 'message': f'Paiement en cours ({status})'}

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau : {e}")
            return {
                'success': False,
                'message': f"Erreur de connexion : {str(e)}"
            }
        except Exception as e:
            print(f"❌ Erreur vérification paiement: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Erreur technique : {str(e)}'
            }

