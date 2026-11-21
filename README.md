# Caniveaux en béton armé — MVP

Application web de gestion de chantier pour les caniveaux en béton armé. Elle centralise les tronçons, calcule les quantités de travaux, estime les besoins en matériaux, suit les dépenses et l'avancement, puis génère des rapports PDF et Excel.

## Fonctionnalités

- Gestion des chantiers : nom, localisation, description.
- Gestion des tronçons : dimensions, épaisseurs, fouille et géométrie.
- Quantification :
  - volume de fouille ;
  - volume du radier ;
  - volume des parois ;
  - volume total de béton ;
  - surface de coffrage.
- Catalogue des matériaux avec unité et prix unitaire.
- Composition de béton exprimée en quantité par mètre cube.
- Suivi des dépenses par catégorie, date et description.
- Suivi de l'avancement du ferraillage, du coffrage et du bétonnage.
- Tableau de bord budgétaire et technique.
- Export Excel sur plusieurs feuilles.
- Export PDF avec quantités, matériaux, dépenses et synthèse financière.
- Test de connexion à la base PostgreSQL depuis l'interface.

## Technologies

- Python 3
- Streamlit
- SQLAlchemy
- PostgreSQL / Supabase
- psycopg2-binary
- Pandas
- OpenPyXL
- ReportLab

## Structure du projet

```text
caniveaux_mvp/
├── app.py                  # Interface Streamlit et navigation
├── requirements.txt        # Dépendances Python
├── test_calculs.py         # Vérification des formules de quantification
├── core/
│   ├── calculs.py          # Calculs géométriques et agrégation
│   ├── materiaux.py        # Besoins et coûts des matériaux
│   ├── couts.py            # Module de coûts
│   └── avancement.py       # Calcul du suivi d'avancement
├── db/
│   ├── connection.py       # Connexion SQLAlchemy et initialisation
│   ├── models.py           # Modèles ORM SQLAlchemy
│   └── schema.sql          # Emplacement prévu pour le schéma SQL
├── exports/
│   ├── excel_export.py     # Génération du classeur Excel
│   └── pdf_export.py       # Génération du rapport PDF
├── pages/                  # Répertoire réservé aux pages Streamlit futures
└── .streamlit/
    └── secrets.toml        # Configuration locale des secrets
```

## Modèle de données

L'application crée automatiquement les tables suivantes avec SQLAlchemy :

| Table | Contenu |
|---|---|
| `chantiers` | Chantiers, localisation et description |
| `troncons` | Géométrie et dimensions de chaque tronçon |
| `materiaux` | Désignations, unités et prix unitaires |
| `compositions_beton` | Quantités de matériaux pour 1 m³ de béton |
| `depenses` | Dépenses réelles, catégories et dates |
| `avancements` | Statut et observations pour chaque étape |

Les suppressions de chantiers sont appliquées en cascade aux tronçons associés. Les suppressions de tronçons sont appliquées en cascade aux données d'avancement.

## Formules de quantification

Toutes les dimensions sont exprimées en mètres.

- **Hauteur de paroi** : hauteur totale moins épaisseur du radier.
- **Volume de fouille** : largeur de fouille × profondeur de fouille × longueur.
- **Volume du radier** : largeur × épaisseur du radier × longueur.
- **Volume des parois** : 2 × hauteur de paroi × épaisseur de paroi × longueur.
- **Volume total de béton** : volume du radier + volume des parois.
- **Surface de coffrage** : 4 × hauteur de paroi × longueur.

Les quantités manquantes sont ignorées dans les totaux. Les valeurs numériques négatives ne sont pas contrôlées avant les calculs : les saisies doivent donc être vérifiées lors de la préparation du chantier.

## Prérequis

- Windows, Linux ou macOS
- Python 3.10 ou supérieur recommandé
- PostgreSQL ou Supabase
- Accès réseau vers la base de données

## Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/byl06/carniveaux_MVP.git
cd carniveaux_MVP
```

### 2. Créer un environnement virtuel

Sous Windows :

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Sous Linux ou macOS :

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créer le fichier `.streamlit/secrets.toml` à la racine du projet :

```toml
SUPABASE_DB_URL = "postgresql://UTILISATEUR:MOT_DE_PASSE@HOTE:5432/NOM_DE_BASE"
```

Pour une URL PostgreSQL directement fournie par Supabase, conserver le format PostgreSQL complet sans ajouter le préfixe `postgresql+psycopg2`; l'application l'ajoute automatiquement.

Le fichier `.streamlit/secrets.toml` est exclu du dépôt par `.gitignore`. Ne jamais publier une URL contenant des identifiants.

Lors du premier démarrage, `Base.metadata.create_all()` crée les tables nécessaires si elles n'existent pas.

## Démarrage

Depuis la racine du projet :

```bash
streamlit run app.py
```

Puis ouvrir l'adresse affichée dans le terminal, généralement `http://localhost:8501`.

La page **Test DB** permet de vérifier la connexion. Si elle échoue, contrôler :

- la disponibilité de Supabase ou PostgreSQL ;
- le nom d'utilisateur et le mot de passe ;
- l'hôte, le port et le nom de la base ;
- les règles réseau et le pare-feu ;
- les caractères réservés dans le mot de passe, encodés dans l'URL si nécessaire.

## Utilisation

1. Créer un chantier dans **Chantiers**.
2. Ajouter ses tronçons dans **Détail chantier**.
3. Consulter les longueurs, volumes et surfaces dans **Quantification**.
4. Ajouter les matériaux disponibles dans **Matériaux**.
5. Renseigner la composition béton pour le chantier dans **Composition béton**.
6. Ajouter les dépenses réelles dans **Dépenses**.
7. Mettre à jour le ferraillage, le coffrage et le bétonnage dans **Avancement**.
8. Consulter le tableau de bord et exporter le rapport depuis **Exports**.

## Suivi de l'avancement

Chaque tronçon dispose de trois étapes :

- Ferraillage
- Coffrage
- Bétonnage

Chaque étape peut avoir le statut `non commencé`, `en cours` ou `terminé`.

- Une étape terminée vaut 100 %.
- Une étape en cours vaut 50 %.
- Une étape non commencée vaut 0 %.
- L'avancement d'un tronçon est calculé sur les trois étapes.
- L'avancement du chantier est la moyenne des avancements de ses tronçons.

## Export des données

### Excel

Le fichier Excel contient :

- une feuille **Quantification** ;
- une feuille **Besoins matériaux** ;
- une feuille **Dépenses**.

### PDF

Le rapport PDF contient :

- les quantités globales ;
- les besoins en matériaux ;
- les dépenses ;
- le budget prévisionnel ;
- les dépenses réelles ;
- l'écart budgétaire ;
- l'avancement global.

## Tests

Le script `test_calculs.py` affiche les résultats des fonctions de quantification sur un tronçon fictif :

```bash
python test_calculs.py
```

Exemple de résultat attendu :

- hauteur de paroi : `1.30 m`
- volume de fouille : `34.2 m³`
- volume du radier : `3.0 m³`
- volume des parois : `3.9 m³`
- volume total de béton : `6.9 m³`
- surface de coffrage : `52.0 m²`

Ce script est une vérification d'exemple ; il ne constitue pas encore une suite pytest complète.

## Déploiement Streamlit Cloud

1. Connecter le dépôt GitHub à Streamlit Community Cloud.
2. Sélectionner `app.py` comme fichier principal.
3. Ajouter `SUPABASE_DB_URL` dans **Advanced settings → Secrets**.
4. Déployer l'application.

La configuration doit utiliser exactement la clé `SUPABASE_DB_URL`.

## Sécurité

- Ne pas versionner `.streamlit/secrets.toml`.
- Ne pas placer de mot de passe dans `app.py`, `README.md` ou les journaux.
- Restreindre les accès réseau et utiliser les mots de passe forts fournis par le fournisseur PostgreSQL.
- Si une URL de base de données a déjà été exposée publiquement, remplacer immédiatement le mot de passe et mettre à jour les secrets.

## Limites actuelles

- Application mono-utilisateur sans authentification ni gestion des rôles.
- Aucun mécanisme de pagination pour les grands volumes de données.
- Pas de formulaire complet de modification des tronçons ou matériaux déjà créés.
- Pas d'interface de suppression des dépenses, compositions béton ou avancements.
- Le module `core/couts.py` est actuellement vide.
- `db/schema.sql` est actuellement vide ; les tables sont créées par les modèles SQLAlchemy.
- La composition doit être validée manuellement avec une référence technique.
- Les résultats sont des estimations et doivent être vérifiés par le responsable technique.

## Licence

Aucune licence logicielle n'est définie dans ce dépôt. Toute utilisation, modification ou redistribution hors du cadre privé doit être validée avec le propriétaire du projet.