# 🌍 **Projet d'Analyse des Données de Vaccination Mondiale (Covid-19)**

**👨‍💻 Auteurs :** Esnault Julien - Galaad - Sofiane  
**📚 TP BIGDATA**  
**🎓 M1 DEV FULL STACK - PAR02 - 2024**  
**📅 15/12/2024 - EFREI**

**📓 Databricks Notebook :** [Lien Databricks](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/3445251035974576/367390688357069/1714409181088165/latest.html)  
**📂 Repo Github :** [Lien GitHub](https://github.com/julienESN/databricks-vaccination-analysis)

---

![BigDataImage](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTfo--_T2wY9gC1wJMuU54Otg28n5ZmBIOmQ&s)

## 🎯 Présentation du Projet, des Données et des Objectifs

**📋 Présentation du projet :**  
Ce projet vise à mettre en place une architecture Lakehouse pour le traitement et l'analyse de données mondiales de vaccination. Le but est de construire un pipeline de données robuste, en utilisant les zones Bronze, Silver et Gold. Le modèle Lakehouse combine les avantages des Data Lakes et Data Warehouses, permettant un traitement évolutif et une analyse en temps réel.

**⚙️ Installation :**

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

# Pré-requis : Installation de Java 8

Pour assurer la compatibilité avec Spark, il est **nécessaire d’installer Java 8**. L’installateur vous demandera d’indiquer l’emplacement de Java durant l’installation. Après l’installation, vous devez définir la variable d’environnement `JAVA_HOME` pour qu’elle pointe vers le répertoire d’installation de Java 8.

## Télécharger Java 8 (OpenJDK)

Vous pouvez télécharger Java 8 (OpenJDK) depuis le lien suivant :  
[Liste de téléchargements OpenJDK 8](https://www.openlogic.com/openjdk-downloads?page=7)

### Téléchargements directs :

- **Windows :**  
  [OpenJDK 8 pour Windows 64-bit](https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u412-b08/openlogic-openjdk-8u412-b08-windows-x64.msi)

- **macOS :**  
  [OpenJDK 8 pour macOS 64-bit](https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u412-b08/openlogic-openjdk-8u412-b08-mac-x64.pkg)

- **Linux :**  
  [OpenJDK 8 pour Linux 64-bit (Debian/Ubuntu)](https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u412-b08/openlogic-openjdk-8u412-b08-linux-x64-deb.deb)

## Configurer la variable d’environnement `JAVA_HOME`

### Sur Windows :

1. **Installer Java 8 :**  
   Exécutez le fichier `.msi` téléchargé et suivez les instructions de l’installateur. Lors de l’installation, l’installateur vous demandera de définir `JAVA_HOME`. Acceptez cette option.

2. **Vérifier et définir manuellement `JAVA_HOME` (si nécessaire) :**  
   - Ouvrez le *Panneau de configuration* > *Système* > *Paramètres système avancés* > *Variables d’environnement*.
   - Créez une nouvelle variable `JAVA_HOME` pointant vers le dossier d’installation de Java 8, par exemple :  
     ```
     C:\Program Files\Java\jdk1.8.0_xxx
     ```
   - Ajoutez `%JAVA_HOME%\bin` à la variable `PATH`.
  
   Remplacez /chemin/vers/java8 par le chemin réel d’installation de Java 8 sur votre système.
   
```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### Sur macOS et Linux :

1. **Installer Java 8 :**  
   Exécutez le fichier `.pkg` (macOS) ou `.deb` (Linux) téléchargé et suivez les instructions de l’installateur.

2. **Définir `JAVA_HOME` :**  
   Ajoutez les lignes suivantes à votre fichier de configuration de shell (`~/.bashrc`, `~/.zshrc`, etc.) :
   ```bash
   export JAVA_HOME=/chemin/vers/java8
   export PATH=$JAVA_HOME/bin:$PATH

**🛠️ Configuration de Spark sur Windows :**  
Pour exécuter correctement Spark sous Windows, vous devez configurer `winutils.exe` :

**📥 Télécharger `winutils.exe`**  
Téléchargez la version correspondante à Hadoop (ex: Hadoop 3.2.0) depuis GitHub. (https://github.com/steveloughran/winutils)  
Placez le fichier, par exemple, dans :  
`C:\hadoop\bin\winutils.exe`

**📥 Télécharger `winutils.exe`**  
Téléchargez la version correspondante à Hadoop (ex: Hadoop 3.2.0) depuis GitHub. (https://github.com/steveloughran/winutils)  
Placez le fichier, par exemple, dans :  
`C:\hadoop\bin\winutils.exe`

**🌐 Variables d'environnement**  
Ajoutez les variables d'environnement suivantes à votre système Windows :

- `HADOOP_HOME` : `C:\hadoop`
- Ajoutez `C:\hadoop\bin` à la variable `PATH`.

---

**📂 Création des répertoires nécessaires**  
Pour garantir le bon fonctionnement de Spark sous Windows, il est essentiel de créer un répertoire temporaire **`tmp`** à la racine de **`C:\`** et de définir les permissions appropriées.  

1. **Créer le répertoire `tmp`** :  
   Exécutez la commande suivante dans PowerShell ou Git Bash :  
   ```bash
   mkdir C:\tmp
    ```

    ```bash
    C:\hadoop\bin\winutils.exe chmod -R 777 C:\tmp
    ```

**📊 Les données :**  
Les données proviennent de sources publiques (ex. WHO) et contiennent :

- Total des vaccinations par pays
- Décès suite au covid par pays et date
- Nombre de personnes ayant reçu au moins une dose, une dernière dose, et des boosters
- Informations géographiques et régionales (ISO3, région OMS)

Format de départ : CSV, avec chargement initial en zone Bronze, puis transformations et enrichissements.

**🎯 Objectifs du projet :**

1. **Ingestion des données (Bronze)** : Charger les données brutes sans transformation.
2. **Nettoyage et transformation (Silver)** : Gérer les valeurs manquantes, supprimer les colonnes inutiles, normaliser les types.
3. **Modélisation (Gold)** : Créer un modèle en étoile (tables de Fait et Dimensions) pour faciliter les analyses.
4. **Enrichissement des données** : Calculs de ratios, progression des vaccinations, etc.
5. **📈 Visualisations et analyses** : Générer des graphiques pour comprendre les tendances par pays, régions OMS et dans le temps.

---

## 🏗️ Flux de Données et Architecture

**🏛️ Architecture Lakehouse :**

- **Zone Bronze** : Données brutes (CSV) telles quelles.
- **Zone Silver** : Données nettoyées, transformation des types, suppression de colonnes inutiles.
- **Zone Gold** : Modèle en étoile (tables Fait et Dimensions), données prêtes pour l'analyse et la visualisation.

**🔄 Flux de données :**  
Source (CSV) → Zone Bronze → Zone Silver (clean, enrich) → Zone Gold (modèle analytique) → Visualisation

---

## 🗂️ Modèle Conceptuel des Données (MCD)

**📊 Table Fait :**  
Contient les mesures clés (total vaccinations, personnes vaccinées, boosters, etc.) et les clés étrangères vers les dimensions.

**📐 Dimensions :**

- **Dimension Temps** : Année, mois, jour
- **Dimension Géographique** : Région OMS, ISO3, pays
- **Dimension Pays** : Détails spécifiques aux pays

Ce modèle en étoile permet des analyses rapides et ciblées.

---

## 🔄 Traitements et Transformations

- **🗑️ Suppression des colonnes inutiles** (Silver) : Pour réduire la complexité.
- **🔧 Gestion des valeurs manquantes** : Remplacement de WHO_REGION manquante par "Unknown".
- **🔄 Conversion des types de données** : Notamment les dates en format `yyyy-MM-dd`.
- **📈 Calculs d’enrichissements** :
    - Ratio de vaccination (ex. total_vaccinations_per100)
    - Progression des vaccinations par pays via une fenêtre temporelle (fonction `lag`).

**📋 Synthèse des opérations par zone :**

- **Bronze** : Ingestion brute.
- **Silver** : Nettoyage, normalisation, préparation des données.
- **Gold** : Création de la table Fait et Dimensions, enrichissement et agrégation.

---

## 📊 Visualisations et Analyses

1. **📈 Progression des vaccinations par pays** :  
     Graphique linéaire montrant l'évolution cumulative des vaccinations pour différents pays, avec interpolation des dates.

2. **📊 Comparaison par région OMS** :  
     Graphique à barres comparant le total des vaccinations par région OMS. Les barres sont annotées pour une lecture facile.

3. **📅 Analyse temporelle annuelle** :  
     Graphique linéaire affichant la progression des vaccinations cumulées par année, mettant en évidence la tendance globale.
   
5. **🪦 Progression des décès liés au COVID** :  
     Graphique linéaire illustrant l'évolution cumulative des décès liés au COVID-19 dans le temps, avec une granularité par pays et région. Ce graphique permet de comparer les tendances entre les régions et d'analyser l'impact de la vaccination sur la mortalité.

---

## 📝 Conclusion

Ce projet illustre l'utilité de l'architecture Lakehouse et de la ségrégation des données en zones (Bronze, Silver, Gold) pour :

- Assurer la traçabilité et la flexibilité (Bronze)
- Maintenir une qualité et une cohérence des données (Silver)
- Permettre une analyse performante et évolutive (Gold)
