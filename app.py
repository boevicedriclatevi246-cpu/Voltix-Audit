"""
VOLTIX AUDIT - Application Flask
Application Web Moderne
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from config.config import APP_NAME, PLANS, TYPES_BATIMENTS
from modules.auth.user_manager import UserManager
from modules.database.db_manager import DatabaseManager
from modules.collecte.gestionnaire_collecte import GestionnaireCollecte
from modules.calculs.moteur_calculs import MoteurCalculs
from modules.calculs.generateur_recommandations import GenerateurRecommandations
from modules.rapports.generateur_pdf_pro import GenerateurPDFPro as GenerateurPDF, GenerateurPDFPro

# Initialisation Flask
app = Flask(__name__)
app.secret_key = 'voltix_audit_secret_key_2025'  # À changer en production

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB pour uploads


# Filtre pour formater les nombres
@app.template_filter('format_number')
def format_number_filter(value):
    """Formate un nombre avec des espaces"""
    try:
        return "{:,}".format(int(value)).replace(',', ' ')
    except:
        return value


# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'connexion'

# Modules backend
user_manager = UserManager()
db_manager = DatabaseManager()
collecte = GestionnaireCollecte()
calculs = MoteurCalculs()


# ========================================
# USER CLASS
# ========================================

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict.get('id')
        self.email = user_dict.get('email', '')
        self.nom_complet = user_dict.get('nom_complet', '')
        self.telephone = user_dict.get('telephone', '')
        self.plan = user_dict.get('plan', 'gratuit')

        # Attributs pour la limite d'audits
        self.audits_max_mois = user_dict.get('audits_max_mois', 3)
        self.audits_utilises_ce_mois = user_dict.get('audits_utilises_ce_mois', 0)

        # Alias pour compatibilité (au cas où)
        self.audits_max = self.audits_max_mois
        self.audits_utilises = self.audits_utilises_ce_mois

        # Autres attributs
        self.date_expiration_plan = user_dict.get('date_expiration_plan')
        self.statut_paiement = user_dict.get('statut_paiement', 'inactif')

    def __repr__(self):
        return f'<User {self.email}>'
@login_manager.user_loader
def load_user(user_id):
    """Charge l'utilisateur depuis la session"""
    user_data = db_manager.get_connection().execute(
        "SELECT * FROM utilisateurs WHERE id = ?", (user_id,)
    ).fetchone()
    if user_data:
        return User(dict(user_data))
    return None


# ========================================
# ROUTES - AUTHENTIFICATION
# ========================================

@app.route('/')
def index():
    """Page d'accueil - redirige selon authentification"""
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    return redirect(url_for('connexion'))


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Connexion d'un utilisateur"""
    if request.method == 'POST':
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')

        # DEBUG
        print(f"🔐 Tentative de connexion:")
        print(f"   Email: {email}")
        print(f"   Mot de passe reçu: {'Oui (' + str(len(mot_de_passe)) + ' caractères)' if mot_de_passe else 'NON'}")

        resultat = user_manager.connecter_utilisateur(email, mot_de_passe)

        print(f"   Résultat: {resultat['success']}")
        if not resultat['success']:
            print(f"   Message: {resultat['message']}")

        if resultat['success']:
            user_data = resultat['user']
            user = User(user_data)
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for('accueil'))
        else:
            flash(resultat['message'], "error")

    return render_template('connexion.html')


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_complet = request.form.get('nom_complet')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        mot_de_passe = request.form.get('mot_de_passe')
        confirmation = request.form.get('confirmation_mot_de_passe')

        # DEBUG : Afficher ce qui est reçu
        print(f"📝 Inscription tentée:")
        print(f"   Nom: {nom_complet}")
        print(f"   Email: {email}")
        print(f"   Téléphone: {telephone}")
        print(f"   Mot de passe reçu: {'Oui' if mot_de_passe else 'NON (None)'}")
        print(f"   Confirmation reçue: {'Oui' if confirmation else 'NON (None)'}")

        # Vérifier que tous les champs sont remplis
        if not all([nom_complet, email, telephone, mot_de_passe, confirmation]):
            flash("Tous les champs sont obligatoires", "error")
            return render_template('inscription.html')

        # Vérifier que les mots de passe correspondent
        if mot_de_passe != confirmation:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template('inscription.html')

        # Inscrire l'utilisateur
        resultat = user_manager.inscrire_utilisateur(
            email=email,
            mot_de_passe=mot_de_passe,
            nom_complet=nom_complet,
            telephone=telephone
        )

        if resultat['success']:
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('connexion'))
        else:
            flash(resultat['message'], "error")

    return render_template('inscription.html')


@app.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnexion"""
    logout_user()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('connexion'))


# ========================================
# ROUTES - APPLICATION
# ========================================

@app.route('/accueil')
@login_required
def accueil():
    """Tableau de bord principal"""
    projets = db_manager.get_projets_utilisateur(current_user.id)
    return render_template('accueil.html', projets=projets[:5])


@app.route('/projets')
@login_required
def liste_projets():
    """Liste de tous les projets"""
    projets = db_manager.get_projets_utilisateur(current_user.id)
    return render_template('liste_projets.html', projets=projets)


@app.route('/projet/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_projet():
    """Créer un nouveau projet avec limitation pour gratuits"""

    if request.method == 'POST':
        # VÉRIFIER LA LIMITE DE PROJETS POUR LES GRATUITS
        if current_user.plan == 'gratuit':
            conn = db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM projets 
                WHERE utilisateur_id = ? AND statut != 'archive'
            """, (current_user.id,))

            nb_projets_actifs = cursor.fetchone()[0]
            conn.close()

            print(f"🔍 Vérification limite projets:")
            print(f"   Plan: {current_user.plan}")
            print(f"   Projets actifs: {nb_projets_actifs}/3")

            if nb_projets_actifs >= 3:
                flash(
                    "⚠️ Limite de projets atteinte ! "
                    "Les utilisateurs gratuits peuvent avoir maximum 3 projets actifs. "
                    "Passez au plan Pro pour créer des projets illimités.",
                    "warning"
                )
                return redirect(url_for('tarifs'))

        # Récupérer les données du formulaire
        nom_projet = request.form.get('nom_projet')
        client_nom = request.form.get('client_nom')
        type_batiment = request.form.get('type_batiment')
        adresse = request.form.get('adresse', '')
        ville = request.form.get('ville', '')
        pays = request.form.get('pays', 'BJ')

        # Informations bâtiment
        surface_totale = float(request.form.get('surface_totale', 0))
        annee_construction = int(request.form.get('annee_construction', 2020))
        nb_etages = int(request.form.get('nb_etages', 1))

        print(f"\n🔧 Création du projet...")
        print(f"   Nom: {nom_projet}")
        print(f"   Client: {client_nom}")
        print(f"   Type: {type_batiment}")

        # Créer le projet
        projet_id = collecte.creer_projet(
            utilisateur_id=current_user.id,
            nom_projet=nom_projet,
            client_nom=client_nom,
            type_batiment=type_batiment,
            adresse_complete=adresse,
            ville=ville,
            pays=pays
        )

        if projet_id:
            print(f"✅ Projet créé avec ID: {projet_id}")

            # Créer le bâtiment associé
            batiment_id = collecte.creer_batiment(
                projet_id=projet_id,
                surface_totale=surface_totale,
                annee_construction=annee_construction,
                nb_etages_prevu=nb_etages
            )

            if batiment_id:
                print(f"✅ Bâtiment créé avec ID: {batiment_id}")

                # Créer le premier étage par défaut
                etage_id = collecte.creer_etage(
                    batiment_id=batiment_id,
                    numero_etage=0,
                    nom_etage="Rez-de-chaussée",
                    surface_etage=surface_totale,
                    hauteur_sous_plafond=2.5
                )

                if etage_id:
                    print(f"✅ Étage créé: Rez-de-chaussée (ID: {etage_id})")
                    flash(f"Projet '{nom_projet}' créé avec succès !", "success")
                    return redirect(url_for('detail_projet', projet_id=projet_id))
                else:
                    print("❌ Erreur création étage")
                    flash("Erreur lors de la création de l'étage", "error")
            else:
                print("❌ Erreur création bâtiment")
                flash("Erreur lors de la création du bâtiment", "error")
        else:
            print("❌ Erreur création projet")
            flash("Erreur lors de la création du projet", "error")

    return render_template('nouveau_projet.html')


@app.route('/mon-compte')
@login_required
def mon_compte():
    """Page de profil utilisateur avec statistiques et graphiques pour PRO"""

    stats_audits = None

    # Récupérer les statistiques d'audits pour les PRO
    if current_user.plan == 'pro':
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Récupérer tous les audits de l'utilisateur avec infos projet
        cursor.execute("""
            SELECT 
                p.nom_projet,
                r.consommation_annuelle_kwh,
                r.classe_energetique,
                r.date_calcul,
                strftime('%Y-%m', r.date_calcul) as mois
            FROM resultats_audits r
            JOIN projets p ON r.projet_id = p.id
            WHERE p.utilisateur_id = ?
            ORDER BY r.date_calcul ASC
        """, (current_user.id,))

        audits = cursor.fetchall()
        conn.close()

        if audits:
            stats_audits = []
            for audit in audits:
                stats_audits.append({
                    'projet_nom': audit[0],
                    'consommation': audit[1],
                    'classe': audit[2],
                    'date': audit[3],
                    'mois': audit[4]
                })

    return render_template('mon_compte.html', stats_audits=stats_audits)


@app.route('/tarifs')
@login_required
def tarifs():
    """Page des tarifs"""
    return render_template('tarifs.html')


@app.route('/comparer', methods=['GET', 'POST'])
@login_required
def comparer_projets():
    """Comparer 2 projets (PRO uniquement)"""

    # Vérifier le plan
    if current_user.plan != 'pro':
        flash("⚠️ La comparaison de projets est réservée aux utilisateurs Pro", "warning")
        return redirect(url_for('tarifs'))

    # Récupérer les projets avec audits
    conn = db_manager.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT p.* 
        FROM projets p
        JOIN resultats_audits r ON p.id = r.projet_id
        WHERE p.utilisateur_id = ?
        ORDER BY p.date_creation DESC
    """, (current_user.id,))

    projets_audites = [dict(row) for row in cursor.fetchall()]

    if request.method == 'POST':
        projet_a_id = int(request.form.get('projet_a_id'))
        projet_b_id = int(request.form.get('projet_b_id'))

        if projet_a_id == projet_b_id:
            flash("⚠️ Veuillez sélectionner 2 projets différents", "warning")
            conn.close()
            return render_template('comparer_projets.html', projets_audites=projets_audites)

        # Récupérer les données des 2 projets
        cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_a_id,))
        projet_a = dict(cursor.fetchone())

        cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_b_id,))
        projet_b = dict(cursor.fetchone())

        # Récupérer les résultats d'audit
        cursor.execute("""
            SELECT * FROM resultats_audits 
            WHERE projet_id = ? 
            ORDER BY date_calcul DESC 
            LIMIT 1
        """, (projet_a_id,))
        resultat_a = dict(cursor.fetchone())

        cursor.execute("""
            SELECT * FROM resultats_audits 
            WHERE projet_id = ? 
            ORDER BY date_calcul DESC 
            LIMIT 1
        """, (projet_b_id,))
        resultat_b = dict(cursor.fetchone())

        conn.close()

        # Couleurs des classes
        classe_couleurs = {
            'A': '#27ae60', 'B': '#2ecc71', 'C': '#f1c40f',
            'D': '#f39c12', 'E': '#e67e22', 'F': '#e74c3c', 'G': '#c0392b'
        }

        # Calculer les différences
        diff_conso = resultat_a['consommation_annuelle_kwh'] - resultat_b['consommation_annuelle_kwh']
        diff_conso_pct = (diff_conso / resultat_b['consommation_annuelle_kwh'] * 100) if resultat_b[
                                                                                             'consommation_annuelle_kwh'] > 0 else 0

        diff_cout = resultat_a['cout_annuel_fcfa'] - resultat_b['cout_annuel_fcfa']
        diff_cout_pct = (diff_cout / resultat_b['cout_annuel_fcfa'] * 100) if resultat_b['cout_annuel_fcfa'] > 0 else 0

        diff_co2 = resultat_a['emissions_co2_kg_an'] - resultat_b['emissions_co2_kg_an']

        # Déterminer le meilleur
        meilleur = 'a' if resultat_a['score_performance'] > resultat_b['score_performance'] else 'b'

        comparaison = {
            'projet_a': projet_a,
            'projet_b': projet_b,
            'resultat_a': resultat_a,
            'resultat_b': resultat_b,
            'classe_a_couleur': classe_couleurs.get(resultat_a['classe_energetique'], '#95a5a6'),
            'classe_b_couleur': classe_couleurs.get(resultat_b['classe_energetique'], '#95a5a6'),
            'diff_conso': diff_conso,
            'diff_conso_pct': diff_conso_pct,
            'diff_cout': diff_cout,
            'diff_cout_pct': diff_cout_pct,
            'diff_co2': diff_co2,
            'meilleur': meilleur
        }

        return render_template('comparer_projets.html',
                               projets_audites=projets_audites,
                               comparaison=comparaison)

    conn.close()
    return render_template('comparer_projets.html', projets_audites=projets_audites)

@app.route('/paiement/initier/<plan>', methods=['POST'])
@login_required
def paiement_initier(plan):
    """Initier un paiement FedaPay"""

    # Vérifier que le plan existe (UNIQUEMENT gratuit et pro)
    if plan not in ['gratuit', 'pro']:
        flash("Plan invalide", "error")
        return redirect(url_for('tarifs'))

    # Si l'utilisateur veut passer au plan gratuit
    if plan == 'gratuit':
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE utilisateurs 
            SET plan = 'gratuit', audits_max_mois = 3
            WHERE id = ?
        """, (current_user.id,))

        conn.commit()
        conn.close()

        flash("Vous êtes maintenant sur le plan Gratuit", "info")
        return redirect(url_for('mon_compte'))

    # Pour le plan Pro
    montant = 15000
    description = 'Abonnement Pro - 20 audits/mois'

    try:
        from modules.paiement.gestionnaire_paiement import GestionnairePaiement
        gestionnaire = GestionnairePaiement()

        resultat = gestionnaire.creer_transaction(
            montant=montant,
            description=description,
            utilisateur_id=current_user.id,
            plan=plan
        )

        if resultat['success']:
            return redirect(resultat['payment_url'])
        else:
            flash(f"Erreur : {resultat['message']}", "error")
            return redirect(url_for('tarifs'))

    except Exception as e:
        print(f"❌ Erreur initiation paiement: {e}")
        flash("Erreur lors de l'initiation du paiement", "error")
        return redirect(url_for('tarifs'))


@app.route('/paiement/confirmation')
@login_required
def paiement_confirmation():
    """Confirmation de paiement FedaPay"""

    # Récupérer l'ID de transaction depuis l'URL
    transaction_id = request.args.get('id')

    if not transaction_id:
        flash("Transaction introuvable", "error")
        return redirect(url_for('tarifs'))

    try:
        from modules.paiement.gestionnaire_paiement import GestionnairePaiement
        gestionnaire = GestionnairePaiement()

        # Vérifier le statut du paiement
        resultat = gestionnaire.verifier_paiement(transaction_id, current_user.id)

        if resultat['success']:
            flash(f"Paiement réussi ! Vous êtes maintenant sur le plan {resultat['plan'].upper()}", "success")
            return redirect(url_for('mon_compte'))
        else:
            flash(f"Erreur : {resultat['message']}", "error")
            return redirect(url_for('tarifs'))

    except Exception as e:
        print(f"❌ Erreur confirmation paiement: {e}")
        import traceback
        traceback.print_exc()
        flash("Erreur lors de la vérification du paiement", "error")
        return redirect(url_for('tarifs'))


@app.route('/paiement/annulation')
@login_required
def paiement_annulation():
    """Annulation de paiement"""
    flash("Paiement annulé", "warning")
    return redirect(url_for('tarifs'))

# ========================================
# ROUTES - DÉTAIL PROJET
# ========================================

@app.route('/projet/<int:projet_id>')
@login_required
def detail_projet(projet_id):
    """Détail d'un projet"""
    # Récupérer le projet
    projet = db_manager.get_connection().execute(
        "SELECT * FROM projets WHERE id = ? AND utilisateur_id = ?",
        (projet_id, current_user.id)
    ).fetchone()

    if not projet:
        flash("Projet introuvable", "error")
        return redirect(url_for('liste_projets'))

    # Récupérer le bâtiment
    batiment = db_manager.get_connection().execute(
        "SELECT * FROM batiments WHERE projet_id = ?",
        (projet_id,)
    ).fetchone()

    # Récupérer les étages
    etages = db_manager.get_connection().execute(
        "SELECT * FROM etages WHERE batiment_id = ? ORDER BY numero_etage",
        (batiment['id'],)
    ).fetchall() if batiment else []

    # Statistiques
    stats = collecte.get_statistiques_projet(projet_id)

    return render_template('detail_projet.html',
                           projet=dict(projet),
                           batiment=dict(batiment) if batiment else None,
                           etages=[dict(e) for e in etages],
                           stats=stats)



@app.route('/projet/<int:projet_id>/etage/nouveau', methods=['GET', 'POST'])
@login_required
def nouvel_etage(projet_id):
    """Ajouter un étage"""
    print(f"\n🔧 nouvel_etage appelé - Projet ID: {projet_id}, Méthode: {request.method}")

    # Vérifier que le projet appartient à l'utilisateur
    try:
        conn = db_manager.get_connection()
        projet = conn.execute(
            "SELECT * FROM projets WHERE id = ? AND utilisateur_id = ?",
            (projet_id, current_user.id)
        ).fetchone()
        conn.close()

        print(f"   Projet trouvé: {projet is not None}")

        if not projet:
            print("   ❌ Projet introuvable - redirection")
            flash("Projet introuvable", "error")
            return redirect(url_for('liste_projets'))

        # Récupérer le bâtiment
        conn = db_manager.get_connection()
        batiment = conn.execute(
            "SELECT * FROM batiments WHERE projet_id = ?",
            (projet_id,)
        ).fetchone()
        conn.close()

        print(f"   Bâtiment trouvé: {batiment is not None}")

        if not batiment:
            print("   ❌ Bâtiment introuvable - redirection")
            flash("Bâtiment introuvable pour ce projet", "error")
            return redirect(url_for('detail_projet', projet_id=projet_id))

        if request.method == 'POST':
            print("   📝 POST - Traitement du formulaire")
            try:
                numero = int(request.form.get('numero', 0))
                nom = request.form.get('nom', '').strip()
                surface = float(request.form.get('surface', 0))
                hauteur = float(request.form.get('hauteur', 2.5))

                if not nom:
                    flash("Veuillez donner un nom à l'étage", "error")
                    return render_template('nouvel_etage.html', projet_id=projet_id)

                etage_id = collecte.creer_etage(
                    batiment_id=batiment['id'],
                    numero_etage=numero,
                    nom_etage=nom,
                    surface_etage=surface,
                    hauteur_sous_plafond=hauteur
                )

                if etage_id:
                    flash(f"Étage '{nom}' créé avec succès !", "success")
                    return redirect(url_for('detail_projet', projet_id=projet_id))
                else:
                    flash("Erreur lors de la création de l'étage", "error")
            except Exception as e:
                print(f"   ❌ Erreur POST: {e}")
                import traceback
                traceback.print_exc()
                flash(f"Erreur : {str(e)}", "error")

        # Afficher le formulaire (GET)
        print("   ✅ Affichage du formulaire GET")
        return render_template('nouvel_etage.html', projet_id=projet_id)

    except Exception as e:
        print(f"❌ ERREUR GLOBALE nouvel_etage: {e}")
        import traceback
        traceback.print_exc()
        flash("Erreur lors du chargement du formulaire", "error")
        return redirect(url_for('detail_projet', projet_id=projet_id))


@app.route('/projet/<int:projet_id>/etage/<int:etage_id>')
@login_required
def detail_etage(projet_id, etage_id):
    """Détail d'un étage et ses pièces"""
    # Récupérer l'étage
    etage = db_manager.get_connection().execute(
        "SELECT e.* FROM etages e JOIN batiments b ON e.batiment_id = b.id JOIN projets p ON b.projet_id = p.id WHERE e.id = ? AND p.utilisateur_id = ?",
        (etage_id, current_user.id)
    ).fetchone()

    if not etage:
        flash("Étage introuvable", "error")
        return redirect(url_for('liste_projets'))

    # Récupérer les pièces
    pieces = db_manager.get_connection().execute(
        "SELECT * FROM pieces WHERE etage_id = ? ORDER BY nom_piece",
        (etage_id,)
    ).fetchall()

    return render_template('detail_etage.html',
                           projet_id=projet_id,
                           etage=dict(etage),
                           pieces=[dict(p) for p in pieces])


@app.route('/projet/<int:projet_id>/etage/<int:etage_id>/piece/nouvelle', methods=['GET', 'POST'])
@login_required
def nouvelle_piece(projet_id, etage_id):
    """Ajouter une pièce"""
    if request.method == 'POST':
        nom = request.form.get('nom')
        type_piece = request.form.get('type_piece')
        surface = float(request.form.get('surface', 0))
        longueur = 0  # Non utilisé - simplifié
        largeur = 0  # Non utilisé - simplifié
        hauteur = float(request.form.get('hauteur', 2.5))
        nb_occupants = int(request.form.get('nb_occupants', 0))

        piece_id = collecte.creer_piece(
            etage_id=etage_id,
            nom_piece=nom,
            type_piece=type_piece,
            surface_piece=surface,
            longueur_piece=longueur,
            largeur_piece=largeur,
            hauteur_plafond=hauteur,
            nb_occupants=nb_occupants
        )

        if piece_id:
            flash(f"Pièce '{nom}' créée avec succès !", "success")
            return redirect(url_for('detail_etage', projet_id=projet_id, etage_id=etage_id))
        else:
            flash("Erreur lors de la création de la pièce", "error")

    return render_template('nouvelle_piece.html', projet_id=projet_id, etage_id=etage_id)


@app.route('/projet/<int:projet_id>/piece/<int:piece_id>')
@login_required
def detail_piece(projet_id, piece_id):
    """Afficher le détail d'une pièce"""

    conn = db_manager.get_connection()
    cursor = conn.cursor()

    # Récupérer le projet
    cursor.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
    projet = dict(cursor.fetchone())

    # Récupérer la pièce
    cursor.execute("SELECT * FROM pieces WHERE id = ?", (piece_id,))
    piece = dict(cursor.fetchone())

    # Récupérer l'étage
    cursor.execute("SELECT * FROM etages WHERE id = ?", (piece['etage_id'],))
    etage = dict(cursor.fetchone())

    # Récupérer les équipements de la pièce
    cursor.execute("SELECT * FROM equipements WHERE piece_id = ? ORDER BY id", (piece_id,))
    equipements = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('detail_piece.html',
                           projet=projet,
                           etage=etage,
                           piece=piece,
                           equipements=equipements)


@app.route('/projet/<int:projet_id>/piece/<int:piece_id>/equipement/nouveau', methods=['POST'])
@login_required
def nouvel_equipement(projet_id, piece_id):
    """Ajouter un équipement à une pièce"""

    # Récupérer les données du formulaire
    type_equipement = request.form.get('type_equipement')
    quantite = int(request.form.get('quantite', 1))
    heures_jour = float(request.form.get('heures_jour', 8))
    jours_semaine = int(request.form.get('jours_semaine', 5))

    print(f"\n🔌 Ajout équipement:")
    print(f"   Type: {type_equipement}")
    print(f"   Quantité: {quantite}")
    print(f"   Heures/jour: {heures_jour}")
    print(f"   Jours/semaine: {jours_semaine}")

    # Extraire le nom et la puissance du type_equipement
    # Format: "Nom de l'équipement (XXXXw)"
    import re
    match = re.search(r'(.+?)\s*\((\d+)W\)', type_equipement)

    if match:
        nom_equipement = match.group(1).strip()
        puissance_w = int(match.group(2))
    else:
        flash("Format d'équipement invalide", "error")
        return redirect(url_for('detail_piece', projet_id=projet_id, piece_id=piece_id))

    # Déterminer la catégorie
    categories = {
        'LED': 'Éclairage',
        'Ampoule': 'Éclairage',
        'Tube': 'Éclairage',
        'Climatiseur': 'Climatisation',
        'Ventilateur': 'Climatisation',
        'Réfrigérateur': 'Réfrigération',
        'Congélateur': 'Réfrigération',
        'Micro-ondes': 'Cuisson',
        'Four': 'Cuisson',
        'Plaque': 'Cuisson',
        'Bouilloire': 'Cuisson',
        'Cafetière': 'Cuisson',
        'Ordinateur': 'Informatique',
        'Écran': 'Informatique',
        'Imprimante': 'Informatique',
        'Photocopieuse': 'Informatique',
        'Télévision': 'Électronique',
        'Routeur': 'Électronique',
        'Projecteur': 'Électronique',
        'Chauffe-eau': 'Électroménager',
        'Machine': 'Électroménager',
        'Sèche-linge': 'Électroménager',
        'Fer': 'Électroménager',
        'Aspirateur': 'Électroménager',
        'Pompe': 'Autres',
        'Chargeur': 'Autres'
    }

    categorie = 'Autres'
    for key, cat in categories.items():
        if key.lower() in nom_equipement.lower():
            categorie = cat
            break

    print(f"   Nom extrait: {nom_equipement}")
    print(f"   Puissance: {puissance_w}W")
    print(f"   Catégorie: {categorie}")

    # Ajouter l'équipement
    equipement_id = collecte.ajouter_equipement_piece(
        piece_id=piece_id,
        nom_equipement=nom_equipement,
        categorie=categorie,
        puissance_w=puissance_w,
        quantite=quantite,
        heures_utilisation_jour=heures_jour,
        jours_utilisation_semaine=jours_semaine
    )

    if equipement_id:
        print(f"✅ Équipement ajouté avec ID: {equipement_id}")
        flash(f"Équipement '{nom_equipement}' ajouté avec succès !", "success")
    else:
        print("❌ Erreur ajout équipement")
        flash("Erreur lors de l'ajout de l'équipement", "error")

    return redirect(url_for('detail_piece', projet_id=projet_id, piece_id=piece_id))

@app.route('/projet/<int:projet_id>/etage/<int:etage_id>/supprimer', methods=['POST'])
@login_required
def supprimer_etage(projet_id, etage_id):
    """Supprimer un étage"""
    # Vérifier que l'étage appartient au projet de l'utilisateur
    etage = db_manager.get_connection().execute("""
        SELECT e.* FROM etages e
        JOIN batiments b ON e.batiment_id = b.id
        JOIN projets p ON b.projet_id = p.id
        WHERE e.id = ? AND p.utilisateur_id = ?
    """, (etage_id, current_user.id)).fetchone()

    if not etage:
        flash("Étage introuvable", "error")
        return redirect(url_for('liste_projets'))

    # Supprimer l'étage
    if collecte.supprimer_etage(etage_id):
        flash("Étage supprimé avec succès", "success")
    else:
        flash("Erreur lors de la suppression", "error")

    return redirect(url_for('detail_projet', projet_id=projet_id))


@app.route('/projet/<int:projet_id>/piece/<int:piece_id>/equipement/<int:equipement_id>/supprimer', methods=['POST'])
@login_required
def supprimer_equipement(projet_id, piece_id, equipement_id):
    """Supprimer un équipement"""
    # Supprimer l'équipement
    if collecte.supprimer_equipement(equipement_id, piece_id):
        flash("Équipement supprimé avec succès", "success")
    else:
        flash("Erreur lors de la suppression", "error")

    return redirect(url_for('detail_piece', projet_id=projet_id, piece_id=piece_id))


@app.route('/projet/<int:projet_id>/calculer', methods=['POST'])
@login_required
def calculer_audit(projet_id):
    """Calculer l'audit énergétique avec vérification de la limite"""

    # Recharger l'utilisateur depuis la BDD pour avoir les valeurs à jour
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, nom_complet, telephone, plan, 
               audits_max_mois, audits_utilises_ce_mois, 
               date_expiration_plan, statut_paiement
        FROM utilisateurs WHERE id = ?
    """, (current_user.id,))

    user_row = cursor.fetchone()
    if user_row:
        user_dict = {
            'id': user_row[0],
            'email': user_row[1],
            'nom_complet': user_row[2],
            'telephone': user_row[3],
            'plan': user_row[4],
            'audits_max_mois': user_row[5],
            'audits_utilises_ce_mois': user_row[6],
            'date_expiration_plan': user_row[7],
            'statut_paiement': user_row[8]
        }
        current_user_fresh = User(user_dict)
    else:
        conn.close()
        flash("Erreur de session", "error")
        return redirect(url_for('connexion'))

    # VÉRIFIER LA LIMITE D'AUDITS avec les données fraîches
    audits_restants = current_user_fresh.audits_max_mois - current_user_fresh.audits_utilises_ce_mois

    print(f"🔍 Vérification limite:")
    print(f"   Max: {current_user_fresh.audits_max_mois}")
    print(f"   Utilisés: {current_user_fresh.audits_utilises_ce_mois}")
    print(f"   Restants: {audits_restants}")

    if audits_restants <= 0:
        conn.close()
        flash(
            f"⚠️ Limite d'audits atteinte ! "
            f"Vous avez utilisé {current_user_fresh.audits_utilises_ce_mois}/{current_user_fresh.audits_max_mois} audits ce mois-ci. "
            f"Passez au plan Pro pour bénéficier de 20 audits/mois.",
            "warning"
        )
        return redirect(url_for('tarifs'))

    # Vérifier que le projet appartient à l'utilisateur
    cursor.execute("SELECT * FROM projets WHERE id = ? AND utilisateur_id = ?",
                   (projet_id, current_user.id))
    projet = cursor.fetchone()

    if not projet:
        conn.close()
        flash("Projet introuvable", "error")
        return redirect(url_for('liste_projets'))

    try:
        from modules.calculs.moteur_calculs import MoteurCalculs
        from modules.calculs.generateur_recommandations import GenerateurRecommandations

        print(f"\n🔄 Calcul de l'audit pour le projet {projet_id}...")
        print(f"   👤 Utilisateur : {current_user_fresh.nom_complet} (Plan: {current_user_fresh.plan})")
        print(f"   📊 Audits AVANT : {current_user_fresh.audits_utilises_ce_mois}/{current_user_fresh.audits_max_mois}")

        moteur = MoteurCalculs()
        generateur_reco = GenerateurRecommandations()

        # Effectuer l'audit
        resultats = moteur.effectuer_audit_complet(projet_id, pays='BJ')

        if resultats:
            # Générer les recommandations
            generateur_reco.generer_toutes_recommandations(projet_id)

            # INCRÉMENTER LE COMPTEUR D'AUDITS UTILISÉS
            cursor.execute("""
                UPDATE utilisateurs 
                SET audits_utilises_ce_mois = audits_utilises_ce_mois + 1
                WHERE id = ?
            """, (current_user.id,))

            conn.commit()

            # Vérifier que l'incrémentation a fonctionné
            cursor.execute("SELECT audits_utilises_ce_mois FROM utilisateurs WHERE id = ?",
                           (current_user.id,))
            new_count = cursor.fetchone()[0]

            audits_restants_apres = current_user_fresh.audits_max_mois - new_count

            print(f"   ✅ Audit comptabilisé")
            print(f"   📊 Audits APRÈS : {new_count}/{current_user_fresh.audits_max_mois}")
            print(f"   📊 Audits restants : {audits_restants_apres}")

            conn.close()

            # Message de succès avec info sur les audits restants
            if audits_restants_apres > 0:
                flash(
                    f"✅ Audit calculé avec succès ! "
                    f"({new_count}/{current_user_fresh.audits_max_mois} audits utilisés ce mois - "
                    f"{audits_restants_apres} restants)",
                    "success"
                )
            else:
                flash(
                    f"✅ Audit calculé avec succès ! "
                    f"⚠️ C'était votre dernier audit gratuit ce mois. "
                    f"Passez au plan Pro pour continuer.",
                    "warning"
                )

            return redirect(url_for('resultats_audit', projet_id=projet_id))
        else:
            conn.close()
            flash("Erreur lors du calcul de l'audit", "error")
            return redirect(url_for('detail_projet', projet_id=projet_id))

    except Exception as e:
        conn.close()
        print(f"❌ Erreur calcul audit: {e}")
        import traceback
        traceback.print_exc()
        flash("Erreur technique lors du calcul", "error")
        return redirect(url_for('detail_projet', projet_id=projet_id))


@app.route('/projet/<int:projet_id>/resultats')
@login_required
def resultats_audit(projet_id):
    """Afficher les résultats de l'audit"""
    # Récupérer le projet
    projet = db_manager.get_connection().execute(
        "SELECT * FROM projets WHERE id = ? AND utilisateur_id = ?",
        (projet_id, current_user.id)
    ).fetchone()

    if not projet:
        flash("Projet introuvable", "error")
        return redirect(url_for('liste_projets'))

    # Récupérer les résultats
    resultats = db_manager.get_connection().execute(
        "SELECT * FROM resultats_audits WHERE projet_id = ? ORDER BY date_calcul DESC LIMIT 1",
        (projet_id,)
    ).fetchone()

    if not resultats:
        flash("Aucun résultat disponible. Calculez d'abord l'audit.", "warning")
        return redirect(url_for('detail_projet', projet_id=projet_id))

    # Récupérer les recommandations
    recommandations = db_manager.get_connection().execute(
        "SELECT * FROM recommandations WHERE projet_id = ? ORDER BY priorite, economie_estimee_fcfa DESC",
        (projet_id,)
    ).fetchall()

    return render_template('resultats_audit.html',
                           projet=dict(projet),
                           resultats=dict(resultats),
                           recommandations=[dict(r) for r in recommandations])


@app.route('/projet/<int:projet_id>/generer-pdf')
@login_required
def generer_pdf(projet_id):
    """Générer le rapport PDF"""
    try:
        generateur = GenerateurPDFPro()
        chemin_pdf = generateur.generer_rapport(projet_id, user_plan=current_user.plan)

        if chemin_pdf and Path(chemin_pdf).exists():
            return send_file(
                chemin_pdf,
                as_attachment=True,
                download_name=f"Rapport_Audit_{projet_id}.pdf",
                mimetype='application/pdf'
            )
        else:
            flash("Erreur lors de la génération du PDF", "error")
    except Exception as e:
        flash(f"Erreur : {str(e)}", "error")

    return redirect(url_for('resultats_audit', projet_id=projet_id))


# ========================================
# LANCEMENT
# ========================================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
