# Pharma Project Tracker

Application Streamlit pour suivre les projets pharma par ligne de production :
ARV, oral oncologie, injectable oncologie, biosimilaires, hormones, capsules, general formulation, etc.

## Fonctionnalités

- Login local username/password sans Google
- Admin crée les utilisateurs et leurs accès
- Accès par ligne de production
- Accès par catégorie : Produit, Dossier, Technique, Tech Transfer, Enregistrement, Site, Business
- Tableau central éditable
- Produit standardisé : `dci dosage forme`
- Couleurs automatiques : OK vert, Manquant rouge, Réserve orange
- Détail produit
- Commentaires par cellule avec auteur/date
- Historique des commentaires
- Ajout de lignes de production
- Ajout de produits
- Export Excel

## Lancement local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Identifiants par défaut

- Username : `admin`
- Password : `admin123`

Change le mot de passe admin dès le premier lancement.

## Déploiement Streamlit Cloud

1. Créer un repo GitHub
2. Upload tous les fichiers
3. Aller sur Streamlit Cloud
4. Choisir le repo
5. Main file path : `app.py`
6. Deploy

## Structure

- `app.py` : application principale
- `db.py` : base SQLite et modèles
- `auth.py` : login et permissions
- `config.py` : catégories, colonnes, statuts
- `utils.py` : helpers
- `seed.py` : données initiales
