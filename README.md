# Projet d'Analyse des Données de Vaccination Mondiale

**Auteurs :** Esnault Julien - Galaad - Sofiane  
**TP BIGDATA**  
**M1 DEV FULL STACK - PAR02 - 2024**  
**15/12/2024 - EFREI**

**Databricks Notebook :** [Lien Databricks](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/3445251035974576/367390688357069/1714409181088165/latest.html)  
**Repo Github :** [Lien GitHub](https://github.com/julienESN/databricks-vaccination-analysis)

---

![BigDataImage](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTfo--_T2wY9gC1wJMuU54Otg28n5ZmBIOmQ&s)

## Présentation du Projet, des Données et des Objectifs

**Présentation du projet :**  
Ce projet vise à mettre en place une architecture Lakehouse pour le traitement et l'analyse de données mondiales de vaccination. Le but est de construire un pipeline de données robuste, en utilisant les zones Bronze, Silver et Gold. Le modèle Lakehouse combine les avantages des Data Lakes et Data Warehouses, permettant un traitement évolutif et une analyse en temps réel.

**Installation :**

```bash
python -m venv .venv
source .venv/bin/activate  # sous Linux/Mac
.venv\Scripts\activate     # sous Windows
pip install -r requirements.txt
```

**Configuration de Spark sur Windows :**  
Pour exécuter correctement Spark sous Windows, vous devez configurer `winutils.exe` :

**Télécharger `winutils.exe`**  
Téléchargez la version correspondante à Hadoop (ex: Hadoop 3.2.0) depuis GitHub. (https://github.com/steveloughran/winutils)
Placez le fichier, par exemple, dans :  
`C:\hadoop\bin\winutils.exe`

**Variables d'environnement**  
Ajoutez les variables d'environnement suivantes à votre système Windows :

- `HADOOP_HOME` : `C:\hadoop`
- Ajoutez `C:\hadoop\bin` à la variable `PATH`.

**Création des répertoires nécessaires**  
Exécutez la commande suivante pour définir les permissions et créer les dossiers requis :

```bash
C:\hadoop\bin\winutils.exe chmod -R 777 C:\tmp
```

**Les données :**  
Les données proviennent de sources publiques (ex. WHO) et contiennent :

- Total des vaccinations par pays
- Nombre de personnes ayant reçu au moins une dose, une dernière dose, et des boosters
- Informations géographiques et régionales (ISO3, région OMS)

Format de départ : CSV, avec chargement initial en zone Bronze, puis transformations et enrichissements.

**Objectifs du projet :**

1. **Ingestion des données (Bronze)** : Charger les données brutes sans transformation.
2. **Nettoyage et transformation (Silver)** : Gérer les valeurs manquantes, supprimer les colonnes inutiles, normaliser les types.
3. **Modélisation (Gold)** : Créer un modèle en étoile (tables de Fait et Dimensions) pour faciliter les analyses.
4. **Enrichissement des données** : Calculs de ratios, progression des vaccinations, etc.
5. **Visualisations et analyses** : Générer des graphiques pour comprendre les tendances par pays, régions OMS et dans le temps.

---

## Flux de Données et Architecture

**Architecture Lakehouse :**

- **Zone Bronze** : Données brutes (CSV) telles quelles.
- **Zone Silver** : Données nettoyées, transformation des types, suppression de colonnes inutiles.
- **Zone Gold** : Modèle en étoile (tables Fait et Dimensions), données prêtes pour l'analyse et la visualisation.

**Flux de données :**  
Source (CSV) → Zone Bronze → Zone Silver (clean, enrich) → Zone Gold (modèle analytique) → Visualisation

---

## Modèle Conceptuel des Données (MCD)

**Table Fait :**  
Contient les mesures clés (total vaccinations, personnes vaccinées, boosters, etc.) et les clés étrangères vers les dimensions.

**Dimensions :**

- **Dimension Temps** : Année, mois, jour
- **Dimension Géographique** : Région OMS, ISO3, pays
- **Dimension Pays** : Détails spécifiques aux pays

Ce modèle en étoile permet des analyses rapides et ciblées.

---

## Traitements et Transformations

- **Suppression des colonnes inutiles** (Silver) : Pour réduire la complexité.
- **Gestion des valeurs manquantes** : Remplacement de WHO_REGION manquante par "Unknown".
- **Conversion des types de données** : Notamment les dates en format `yyyy-MM-dd`.
- **Calculs d’enrichissements** :
  - Ratio de vaccination (ex. total_vaccinations_per100)
  - Progression des vaccinations par pays via une fenêtre temporelle (fonction `lag`).

**Synthèse des opérations par zone :**

- **Bronze** : Ingestion brute.
- **Silver** : Nettoyage, normalisation, préparation des données.
- **Gold** : Création de la table Fait et Dimensions, enrichissement et agrégation.

---

## Visualisations et Analyses

1. **Progression des vaccinations par pays** :  
   Graphique linéaire montrant l'évolution cumulative des vaccinations pour différents pays, avec interpolation des dates.

2. **Comparaison par région OMS** :  
   Graphique à barres comparant le total des vaccinations par région OMS. Les barres sont annotées pour une lecture facile.

3. **Analyse temporelle annuelle** :  
   Graphique linéaire affichant la progression des vaccinations cumulées par année, mettant en évidence la tendance globale.

---

## Conclusion

Ce projet illustre l'utilité de l'architecture Lakehouse et de la ségrégation des données en zones (Bronze, Silver, Gold) pour :

- Assurer la traçabilité et la flexibilité (Bronze)
- Maintenir une qualité et une cohérence des données (Silver)
- Permettre une analyse performante et évolutive (Gold)

Les visualisations et les enrichissements produits fournissent des insights exploitables sur la progression mondiale de la vaccination. Cette approche est transférable à d'autres domaines de l'analyse de données, assurant évolutivité, robustesse et efficacité.

---
