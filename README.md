# AT Pharma — Big Excel Project Tracker

Application Streamlit pour le suivi des projets AT Pharma sous forme de grand tableau type Excel.

## Logique produit

- Une feuille par ligne de production :
  - ARV
  - Oral oncologie
  - Injectable oncologie
  - Biosimilaires
  - Oral general formulation
  - Hormones orales
  - Capsules molles
  - Capsules dures
  - Injectables classiques

- Une ligne = un produit
- Les colonnes sont groupées par catégories :
  - Produit
  - Dossier réglementaire
  - Évaluation technique
  - Tech transfer
  - Enregistrement ANPP
  - Site readiness
  - Business

## Fonctionnalités

- Interface big tableau, type Excel/Smartsheet
- Header de catégorie au-dessus des colonnes
- Couleurs par catégorie
- Couleurs par statut : OK, Manquant, Réserve, etc.
- Édition directe dans le tableau
- Permissions par ligne de production et par catégorie
- Commentaires par cellule
- Historique des commentaires
- Ajout de produits
- Ajout de lignes de production
- Export Excel

## Lancement local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Identifiants par défaut

```txt
username: admin
password: admin123
```

Change le mot de passe admin après le premier lancement.

## Déploiement Streamlit Cloud

1. Créer un repo GitHub
2. Uploader tous les fichiers
3. Streamlit Cloud > New app
4. Main file path : `app.py`
5. Deploy
