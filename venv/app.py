import os
import re
from flask import jsonify, redirect, request , url_for

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
#from cryptography.fernet import Fernet

# Clé à générer UNE fois, puis stockée en sécurité
#key = os.getenv('FERNET_KEY')
#if key is None:
#    raise ValueError("La variable d'environnement FERNET_KEY n'est pas définie.")
#cipher_suite = Fernet(key.encode())
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://amal_stage:amalstage@localhost/stage_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELE : Filiere
class Filiere(db.Model):
    __tablename__ = 'filiere'
    Id_Filiere = db.Column(db.Integer, primary_key=True)
    Nom = db.Column(db.String(100), nullable=False)

    promotions = db.relationship('Promotion', backref='filiere', lazy=True)
    stagiaires = db.relationship('Stagiaire', backref='filiere_obj', lazy=True)

# MODELE : Promotion
class Promotion(db.Model):
    __tablename__ = 'promotion'
    Id_Promotion = db.Column(db.Integer, primary_key=True)
    IdFiliere = db.Column(db.Integer, db.ForeignKey('filiere.Id_Filiere'), nullable=True)
    Nom = db.Column(db.String(100))
    Annee_Debut = db.Column(db.Integer, nullable=False)
    Annee_Fin = db.Column(db.Integer, nullable=False)

    stagiaires = db.relationship('Stagiaire', backref='promotion', lazy=True)

# MODELE : Stagiaire
class Stagiaire(db.Model):
    __tablename__ = 'stagiaire'
    Id_Stagiaire = db.Column(db.Integer, primary_key=True)
    Nom = db.Column(db.String(50))
    Prenom = db.Column(db.String(50), unique=True)
    CINE = db.Column(db.String(20))
    Date_Naissance = db.Column(db.Date)
    Lieu_Naissance = db.Column(db.String(100))
    Type_Bac = db.Column(db.String(100))
    Annee_Bac = db.Column(db.Integer)
    Moyenne_Bac = db.Column(db.Float)
    Mention_Bac = db.Column(db.String(20))
    Niveau_Etude = db.Column(db.String(50))
    Autres_diplome = db.Column(db.String(100))
    RIB = db.Column(db.String(255), unique=True) 
    Telephone = db.Column(db.BigInteger, unique=True)
    Email = db.Column(db.String(50), unique=True)
    IdFiliere = db.Column(db.Integer, db.ForeignKey('filiere.Id_Filiere'))
    IdPromotion = db.Column(db.Integer, db.ForeignKey('promotion.Id_Promotion'))

    absences = db.relationship('Absence', backref='stagiaire', lazy=True)

# MODELE : Absence
class Absence(db.Model):
    __tablename__ = 'absence'
    Id = db.Column(db.Integer, primary_key=True)
    Id_Stagiaire = db.Column(db.Integer, db.ForeignKey('stagiaire.Id_Stagiaire'))
    Date_Absence = db.Column(db.Date)
    Motif = db.Column(db.String(255))
    Justifie = db.Column(db.Boolean)
    Nbre_absences = db.Column(db.Integer, default=0)

@app.route("/")
def accueil():
    return render_template("home.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/finance")
def finance():
    promotions = Promotion.query.filter_by(IdFiliere = 2 ).all()
    return render_template("promo-finance.html", promotions=promotions)


@app.route("/green-spaces")
def green_spaces():
    promotions = Promotion.query.filter_by(IdFiliere = 1 ).all()
    return render_template("promo-greenSpace.html", promotions=promotions)

@app.route("/addPromotion", methods=['POST'])
def add_promotion():
    id_filiere = request.form.get('id_filiere', type=int)
    nom = request.form.get('nom')
    anneeDebut = request.form.get('anneeDebut', type=int)
    anneeFin = request.form.get('anneeFin', type=int)

    # Validation simple
    if not all([id_filiere, nom, anneeDebut, anneeFin]):
        return "Champs manquants", 400
    if anneeDebut >= anneeFin:
        return "Année de début doit être inférieure à l'année de fin", 400

    # Création et insertion
    promotion = Promotion(
        IdFiliere=id_filiere,
        Nom="Filiere" + " " + nom + " " + "Promotion" + " " + str(anneeDebut) + "-" + str(anneeFin),
        Annee_Debut=anneeDebut,
        Annee_Fin=anneeFin
    )
    db.session.add(promotion)
    db.session.commit()

    return redirect("/about")

@app.route("/stagiaires")
def page_stagiaires():
    filieres = Filiere.query.all()
    return render_template("stagiaires_dynamique.html", filieres=filieres)

@app.route("/api/promotions/<int:id_filiere>")
def api_promotions(id_filiere):
    promotions = Promotion.query.filter_by(IdFiliere=id_filiere).all()
    return jsonify([
        {"id": p.Id_Promotion, "nom": f"{p.Nom} ({p.Annee_Debut}-{p.Annee_Fin})"}
        for p in promotions
    ])

@app.route("/api/stagiaires")
def api_stagiaires_all():
    stagiaires = Stagiaire.query.all()
    return jsonify([
        {
            "id_stagiaire": s.Id_Stagiaire,
            "id": s.Id_Stagiaire,
            "nom": s.Nom,
            "prenom": s.Prenom,
            "cine": s.CINE,
            "date_naissance": s.Date_Naissance.strftime("%Y-%m-%d"),
            "lieu_naissance": s.Lieu_Naissance,
            "type_bac": s.Type_Bac,
            "annee_bac": s.Annee_Bac,
            "moyenne_bac": s.Moyenne_Bac,
            "mention_bac": s.Mention_Bac,
            "niveau_etude": s.Niveau_Etude,
            "autres_diplome": s.Autres_diplome,
           # "rib": cipher_suite.decrypt(s.RIB.encode()).decode(),  # Déchiffrement du RIB
            "rib": s.RIB,  
            "telephone": s.Telephone,
            "email": s.Email
        }
        for s in stagiaires
    ])

@app.route("/api/stagiaires/<int:id_promotion>")
def api_stagiaires(id_promotion):
    stagiaires = Stagiaire.query.filter_by(IdPromotion=id_promotion).all()
    return jsonify([
        {
            
            "nom": s.Nom,
            "prenom": s.Prenom,
            "cine": s.CINE,
            "date_naissance": s.Date_Naissance.strftime("%Y-%m-%d"),
            "lieu_naissance": s.Lieu_Naissance,
            "type_bac": s.Type_Bac,
            "annee_bac": s.Annee_Bac,
            "moyenne_bac": s.Moyenne_Bac,
            "mention_bac": s.Mention_Bac,
            "niveau_etude": s.Niveau_Etude,
            "autres_diplome": s.Autres_diplome,
            "rib": s.RIB,
            "telephone": s.Telephone,
            "email": s.Email
        }
        for s in stagiaires
    ])

@app.route("/addStagiaire")
def add_stagiaire():
    filieres = Filiere.query.all()
    promotions = Promotion.query.all()
    return render_template("addStagiaire.html", filieres=filieres, promotions=promotions)
@app.route("/addStagiaire", methods=['POST'])
def api_add_stagiaire():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    cine = request.form.get('cine')
    date_naissance = request.form.get('date_naissance')
    lieu_naissance = request.form.get('lieu_naissance')
    type_bac = request.form.get('type_bac')
    annee_bac = request.form.get('annee_bac', type=int)
    moyenne_bac = request.form.get('moyenne_bac', type=float)
    mention_bac = request.form.get('mention_bac')
    niveau_etude = request.form.get('niveau_etude')
    autres_diplome = request.form.get('autres_diplome')
    rib = request.form.get('rib')
    telephone = request.form.get('telephone', type=int)
    email = request.form.get('email')
    id_filiere = request.form.get('id_filiere', type=int)
    id_promotion = request.form.get('id_promotion', type=int)

    # Validation simple
    if not all([nom, prenom, cine, date_naissance, lieu_naissance, type_bac, annee_bac, moyenne_bac, mention_bac, niveau_etude, rib, telephone, email, id_filiere, id_promotion]):
        return "Champs manquants", 400
    
    if not re.fullmatch(r'[A-Za-z]{2}\d{6}', cine):
        return "CINE doit commencer par 2 lettres suivies de 6 chiffres (8 caractères au total)", 400

    if not (rib and len(rib) >= 10):
        erreur = "RIB invalide"
        return render_template('addStagiaire.html', erreur=erreur,
                           filieres=Filiere.query.all(),
                           promotions=Promotion.query.all())
    # Chiffrement du RIB
    # rib_crypte = cipher_suite.encrypt(rib.encode()).decode()
    if rib in [s.RIB for s in Stagiaire.query.all()]:
        return render_template('addStagiaire.html', erreur_rib="RIB déjà utilisé",
                           filieres=Filiere.query.all(),
                           promotions=Promotion.query.all())
    
    if telephone in [s.Telephone for s in Stagiaire.query.all()]:
        return render_template('addStagiaire.html', erreur_telephone="Numéro de téléphone déjà utilisé",
                           filieres=Filiere.query.all(),
                           promotions=Promotion.query.all())
    
    if email in [s.Email for s in Stagiaire.query.all()]:
        return render_template('addStagiaire.html', erreur_email="Email déjà utilisé",
                           filieres=Filiere.query.all(),
                           promotions=Promotion.query.all())
    
    if cine in [s.CINE for s in Stagiaire.query.all()]:
        return render_template('addStagiaire.html', erreur_cine="CINE déjà utilisé",
                           filieres=Filiere.query.all(),
                           promotions=Promotion.query.all())
    
    # Création et insertion
    stagiaire = Stagiaire(
        Nom=nom,
        Prenom=prenom,
        CINE=cine,
        Date_Naissance=date_naissance,
        Lieu_Naissance=lieu_naissance,
        Type_Bac=type_bac,
        Annee_Bac=annee_bac,
        Moyenne_Bac=moyenne_bac,
        Mention_Bac=mention_bac,
        Niveau_Etude=niveau_etude,
        Autres_diplome=autres_diplome,
        RIB=rib,
        Telephone=telephone,
        Email=email,
        IdFiliere=id_filiere,
        IdPromotion=id_promotion
    )
    
    db.session.add(stagiaire)
    db.session.commit()

    return redirect("/stagiaires")
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/absence")
def absence():
    absences = Absence.query.all()
    return render_template("absence.html", absences=absences)


@app.route("/addAbsence", methods=['GET', 'POST'])
def add_absence():
    stagiaires = Stagiaire.query.all()

    if request.method == 'POST':
        id_stagiaire = request.form.get('id_stagiaire', type=int)
        date_absence = request.form.get('date_absence')
        motif = request.form.get('motif')
        justifie = 'justifie' in request.form  
        nbre_jour = request.form.get('nbre_jour')

        # Validation simple
        if not all([id_stagiaire, date_absence]):
            return "Champs manquants", 400

        # Création et insertion
        absence = Absence(
            Id_Stagiaire=id_stagiaire,
            Date_Absence=date_absence,
            Motif=motif,
            Justifie=justifie,
            Nbre_absences=nbre_jour if nbre_jour else 0
        )

        db.session.add(absence)
        db.session.commit()

        return redirect("/absence")

    # Méthode GET
    return render_template("addAbsence.html", stagiaires=stagiaires)
@app.route("/deleteAbsence/<int:id_absence>")
def delete_absence(id_absence):
    absence = Absence.query.get_or_404(id_absence)
    db.session.delete(absence)
    db.session.commit()
    return redirect("/absence")

@app.route("/deleteStagiaire/<int:id_stagiaire>")
def delete_stagiaire(id_stagiaire):
    stagiaire = Stagiaire.query.get_or_404(id_stagiaire)
    db.session.delete(stagiaire)
    db.session.commit()
    return redirect("/stagiaires")

@app.route("/editStagiaire/<int:id_stagiaire>")
def edit_stagiaire(id_stagiaire):
    stagiaire = Stagiaire.query.get_or_404(id_stagiaire)
    filieres = Filiere.query.all()
    promotions = Promotion.query.all()
    return render_template("editStagiaire.html", stagiaire=stagiaire, filieres=filieres, promotions=promotions)

@app.route("/updateStagiaire/<int:id_stagiaire>", methods=['GET', 'POST'])
def update_stagiaire(id_stagiaire):
    stagiaire = Stagiaire.query.get_or_404(id_stagiaire)


    stagiaire.Nom = request.form.get('nom')
    stagiaire.Prenom = request.form.get('prenom')
    stagiaire.CINE = request.form.get('cine')
    stagiaire.Date_Naissance = request.form.get('date_naissance')
    stagiaire.Lieu_Naissance = request.form.get('lieu_naissance')
    stagiaire.Type_Bac = request.form.get('type_bac')
    stagiaire.Annee_Bac = request.form.get('annee_bac', type=int)
    stagiaire.Moyenne_Bac = request.form.get('moyenne_bac', type=float)
    stagiaire.Mention_Bac = request.form.get('mention_bac')
    stagiaire.Niveau_Etude = request.form.get('niveau_etude')
    stagiaire.Autres_diplome = request.form.get('autres_diplome')
    stagiaire.RIB = request.form.get('rib')
    stagiaire.Telephone = request.form.get('telephone', type=int)
    stagiaire.Email = request.form.get('email')
    stagiaire.IdFiliere = request.form.get('id_filiere', type=int)
    stagiaire.IdPromotion = request.form.get('id_promotion', type=int)

    db.session.commit()
    return redirect("/stagiaires")

    return render_template("updateStagiaire.html", stagiaire=stagiaire, filieres=filieres, promotions=promotions)
if __name__ == "__main__":
    app.run(debug=True)     
