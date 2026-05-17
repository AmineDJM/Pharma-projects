# AT Pharma — Excel Only Tracker

Version Streamlit orientée tableau unique type Excel/Smartsheet.

## Philosophie

- Tout se fait dans le tableau principal.
- Aucun panneau de fiche produit sous le tableau.
- Les modifications se font directement dans les cellules.
- L'utilisateur clique sur "Enregistrer les modifications" en haut à droite.
- Les documents sont uploadés via une action de cellule/document et apparaissent dans le tableau.
- Les logs sont réservés à l'administrateur.

## Fonctionnalités

- Login local username/password
- Rôles : admin, editor, supplier, viewer
- Accès par feuille de production et par catégorie
- Feuilles : ARV, oral oncologie, injectable oncologie, biosimilaires, etc.
- Colonnes groupées visuellement par catégorie
- Couleurs par catégorie et par statut
- Édition directe
- Upload ZIP/documents réglementaires
- Historique de modifications : qui, quoi, avant, après, quand
- Sauvegarde cellule-par-cellule pour préserver les modifications simultanées
- Export Excel
- Responsive Streamlit wide layout

## Lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Identifiants par défaut

```txt
admin
admin123
```

Change le mot de passe après le premier lancement.
