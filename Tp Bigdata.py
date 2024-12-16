# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC Ce notebook présente la mise en place d’une architecture Lakehouse pour le traitement et l’analyse des données de vaccination mondiale. Le projet suit les principes de zone Bronze, Silver, et Gold afin de structurer les données et préparer des analyses efficaces.
# MAGIC
# MAGIC ## Objectifs :
# MAGIC > Ingestion des données brutes :
# MAGIC -  Chargement des données sources dans la zone Bronze (raw data).
# MAGIC > Nettoyage et transformation :
# MAGIC - Traitement des données pour les préparer dans la zone Silver (cleaned data).
# MAGIC > Structuration et Modélisation :
# MAGIC - Création d’un modèle en étoile avec des tables de faits et dimensions dans la zone Gold (analytical data).
# MAGIC > Visualisation des données :
# MAGIC - Utilisation de visualisations pour répondre aux questions analytiques sur les statistiques de vaccination.
# MAGIC > Flux de Données :
# MAGIC - Source → Zone Bronze → Zone Silver → Zone Gold → Visualisation
# MAGIC
# MAGIC ## Technologies Utilisées :
# MAGIC - Databricks pour l’exécution des traitements Big Data.
# MAGIC - Apache Spark pour le nettoyage et la transformation des données.
# MAGIC - Delta Lake pour le stockage des données avec gestion des transactions.
# MAGIC - Databricks Notebook pour les visualisations finales.
# MAGIC ## Résumé des Étapes :
# MAGIC - Bronze : Chargement des données brutes.
# MAGIC - Silver : Nettoyage, enrichissement et validation des données.
# MAGIC - Gold : Création des tables agrégées pour des analyses avancées.
# MAGIC
# MAGIC ## À suivre dans ce notebook :
# MAGIC - Préparation des données
# MAGIC - Transformation et Enrichissement
# MAGIC - Création des tables de faits et dimensions
# MAGIC - Visualisation et Analyse des données
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #  Bronze :
# MAGIC
# MAGIC - Chargement des données brutes.
# MAGIC - Sauvegarde dans la zone Bronze.

# MAGIC %md
# MAGIC
# MAGIC # **Zone Silver**
# MAGIC
# MAGIC - Nettoyage et transformation.
# MAGIC - Sauvegarde dans la zone Silver.

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

# Initialiser Spark

spark = SparkSession.builder \
    .appName("VaccinationDataPipeline") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.3.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


# 1. Zone Bronze : Chargement des données
try:
    file_location = "data/vaccination-data.csv"

    df_bronze = spark.read.format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(file_location)

    print("Zone Bronze :")
    df_bronze.printSchema()

    # Sauvegarde en Delta
    df_bronze.write.format("delta").mode("overwrite").save("delta/bronze/vaccination_data")
except Exception as e:
    print(f"Erreur Zone Bronze : {e}")

# 2. Zone Silver : Nettoyage
try:
    df_clean = df_bronze.drop("VACCINES_USED", "NUMBER_VACCINES_TYPES_USED", "DATA_SOURCE") \
        .filter(col("TOTAL_VACCINATIONS").isNotNull()) \
        .fillna({"WHO_REGION": "Unknown"})

    df_clean = df_clean.withColumn("DATE_UPDATED", to_date("DATE_UPDATED", "yyyy-MM-dd"))

    print("Zone Silver :")
    df_clean.printSchema()

    df_clean.write.format("delta").mode("overwrite").save("delta/silver/vaccination_data_cleaned")
except Exception as e:
    print(f"Erreur Zone Silver : {e}")





# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Zone Gold
# MAGIC
# MAGIC Dans cette section, nous allons :
# MAGIC - Créer la table Fait (Fact Table).
# MAGIC - Créer les tables Dimensions (géographique et temporelle).
# MAGIC - Sauvegarder les données transformées dans la zone Gold pour des analyses et visualisations.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # Bloc : Création de la Table Fait (Fact Table)

# COMMAND ----------

# Bloc Table Fait corrigé
try:
    # Création de la table Fait à partir des données nettoyées
    fact_table = df_clean.select(
        "COUNTRY",
        "WHO_REGION",
        "DATE_UPDATED",
        "TOTAL_VACCINATIONS",
        "PERSONS_VACCINATED_1PLUS_DOSE", 
        "PERSONS_LAST_DOSE",
        "PERSONS_BOOSTER_ADD_DOSE"
    )

    # Vérification des types de données
    fact_table.printSchema()

    # Sauvegarde de la table Fait dans la zone Gold avec Delta
    fact_table.write.format("delta").mode("overwrite").save("delta/gold/fact_covid_vaccinations")
    print("Table Fait créée et sauvegardée avec succès dans la zone Gold avec Delta.")
except Exception as e:
    print(f"Erreur lors de la création de la Table Fait : {e}")



# COMMAND ----------

# MAGIC %md
# MAGIC # Bloc : Création de la Dimension Géographique

# COMMAND ----------

try:
    # Création de la dimension géographique
    dimension_country = df_clean.select("COUNTRY", "ISO3", "WHO_REGION").distinct()

    # Vérification des types de données
    dimension_country.printSchema()

    # Sauvegarde de la dimension géographique dans la zone Gold
    dimension_country.write.format("delta").mode("overwrite").save("delta/gold/dimension_country")

    print("Dimension Géographique créée et sauvegardée avec succès dans la zone Gold.")
except Exception as e:
    print(f"Erreur lors de la création de la Dimension Géographique : {e}")


# COMMAND ----------

# MAGIC %md
# MAGIC # Bloc : Création de la Dimension Temporelle

# COMMAND ----------

from pyspark.sql.functions import year, month, dayofmonth

try:
    # Création de la dimension temporelle
    dimension_date = df_clean.select("DATE_UPDATED").distinct() \
        .withColumn("year", year("DATE_UPDATED")) \
        .withColumn("month", month("DATE_UPDATED")) \
        .withColumn("day", dayofmonth("DATE_UPDATED"))

    # Vérification des types de données
    dimension_date.printSchema()

    # Sauvegarde de la dimension temporelle dans la zone Gold
    dimension_date.write.format("delta").mode("overwrite").save("delta/gold/dimension_date")

    print("Dimension Temporelle créée et sauvegardée avec succès dans la zone Gold.")
except Exception as e:
    print(f"Erreur lors de la création de la Dimension Temporelle : {e}")


# COMMAND ----------

# MAGIC %md
# MAGIC # Ajout des enrichissements pour la Table Fait

# COMMAND ----------

# Création et enrichissement de la table Fait
from pyspark.sql.functions import col, lag
from pyspark.sql.window import Window

from pyspark.sql.functions import col, lag, when
from pyspark.sql.window import Window

try:
    # Rechargement de fact_table
    fact_table = spark.read.format("delta").load("delta/gold/fact_covid_vaccinations")

    # Ajout de la progression des vaccinations
    window_spec = Window.partitionBy("COUNTRY").orderBy("DATE_UPDATED")
    fact_table = fact_table.withColumn("progression_vaccinations", 
                                       col("TOTAL_VACCINATIONS") - lag("TOTAL_VACCINATIONS").over(window_spec))

    # Ajout du ratio (remplacer par la bonne colonne si disponible)
    fact_table = fact_table.withColumn(
        "vaccination_ratio",
        when(col("PERSONS_VACCINATED_1PLUS_DOSE") > 0, 
             col("TOTAL_VACCINATIONS") / col("PERSONS_VACCINATED_1PLUS_DOSE"))
        .otherwise(None)
    )

    # Sauvegarde finale
    fact_table.write.format("delta").mode("overwrite").save("delta/gold/fact_covid_vaccinations_enriched")
    print("Table Fait enrichie et sauvegardée avec succès.")
except Exception as e:
    print(f"Erreur lors de l'enrichissement de la Table Fait : {e}")

# Export des résultats localement
export_path = "exports/fact_covid_vaccinations_enriched"
fact_table.coalesce(1).write.csv(export_path, mode="overwrite", header=True)
print(f"Données exportées avec succès dans : {export_path}")




# COMMAND ----------

# MAGIC %md
# MAGIC # Ajout des tables agrégées

# COMMAND ----------

# MAGIC %md
# MAGIC ## a. Total des vaccinations par région OMS

# COMMAND ----------

from pyspark.sql.functions import col

region_aggregation = fact_table.groupBy("WHO_REGION").agg({"total_vaccinations": "sum"}) \
    .withColumnRenamed("sum(total_vaccinations)", "total_vaccinations_sum")

region_aggregation.write.format("delta").mode("overwrite").save("delta/gold/region_aggregation")



# COMMAND ----------

# MAGIC %md
# MAGIC ## b. Moyenne quotidienne des vaccinations par pays

# COMMAND ----------

from pyspark.sql.functions import col

# Agrégation pour calculer la moyenne quotidienne des vaccinations par pays
daily_avg = fact_table.groupBy("COUNTRY").agg({"total_vaccinations": "avg"}) \
    .withColumnRenamed("avg(total_vaccinations)", "avg_total_vaccinations")

# Sauvegarde des résultats dans la zone Gold
daily_avg.write.format("delta").mode("overwrite").save("delta/gold/daily_avg_vaccinations")



# COMMAND ----------

# MAGIC %md
# MAGIC # 5. Ajout d'une table enrichie pour les Dimensions

# COMMAND ----------

# MAGIC %md
# MAGIC ## a. Enrichissement de la dimension temporelle

# COMMAND ----------

from pyspark.sql.functions import when, dayofweek

# Ajout de la colonne `day_of_week`
dimension_date = dimension_date.withColumn("day_of_week", dayofweek(col("DATE_UPDATED")))

# Ajout de la colonne `season`
dimension_date = dimension_date.withColumn(
    "season",
    when((col("month") >= 3) & (col("month") <= 5), "Spring")
    .when((col("month") >= 6) & (col("month") <= 8), "Summer")
    .when((col("month") >= 9) & (col("month") <= 11), "Fall")
    .otherwise("Winter")
)

# Ajout de la colonne `is_weekend`
dimension_date = dimension_date.withColumn(
    "is_weekend",
    when((col("day_of_week") == 7) | (col("day_of_week") == 1), True).otherwise(False)
)

# Sauvegarde des données dans la zone Gold
dimension_date.write.format("delta").mode("overwrite").save("delta/gold/enriched_dimension_date")



# COMMAND ----------

# MAGIC %md
# MAGIC # Export des données
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## a. Export des données de la Table Fait enrichie

# COMMAND ----------

import os
import shutil

# Création d'un répertoire local pour les exports
export_dir = "exports"
os.makedirs(export_dir, exist_ok=True)
print(f"Répertoire '{export_dir}' créé avec succès.")

os.makedirs(export_dir, exist_ok=True)

import os
import shutil

# Création d'un répertoire local pour les exports
export_dir = "exports"
os.makedirs(export_dir, exist_ok=True)
print(f"Répertoire '{export_dir}' créé avec succès.")

# Export des fichiers
try:
    # Export des données de la table Fait enrichie
    fact_table.toPandas().to_csv(f"{export_dir}/fact_covid_vaccinations_enriched.csv", index=False)

    # Export des dimensions
    dimension_country.toPandas().to_csv(f"{export_dir}/dimension_country.csv", index=False)
    dimension_date.toPandas().to_csv(f"{export_dir}/dimension_date.csv", index=False)

    print(f"Fichiers exportés avec succès dans le répertoire '{export_dir}'")
except Exception as e:
    print(f"Erreur lors de l'export des fichiers : {e}")

# Vérification du contenu du répertoire
print("Contenu du répertoire d'exports :")
print(os.listdir(export_dir))


import shutil

# Export des données dans un répertoire local
# Après coalescence, vous obtenez un fichier type : exports/fact_covid_vaccinations_enriched/part-00000-tid-xxxx.csv
# Vous pouvez le renommer ou le copier explicitement :
import glob
files = glob.glob("exports/fact_covid_vaccinations_enriched/*.csv")
if files:
    shutil.copy(files[0], f"{export_dir}/fact_covid_vaccinations_enriched.csv")

print(f"Fichier exporté dans : {export_dir}/fact_covid_vaccinations_enriched.csv")


# Vérification de la version de Pandas
import os
import shutil
import pandas as pd  # Ajout de l'import manquant

# Vérification de la version de Pandas
assert pd.__version__ >= "1.0.5", "Pandas >= 1.0.5 must be installed. Run `pip install pandas --upgrade`."

# Répertoire d'export
export_dir = "exports"
os.makedirs(export_dir, exist_ok=True)
print(f"Répertoire '{export_dir}' créé avec succès.")

# Export des données fact_table
if 'fact_table' in locals():
    fact_table.toPandas().to_csv(f"{export_dir}/fact_covid_vaccinations_enriched.csv", index=False)
else:
    print("Erreur : La table `fact_table` n'est pas définie.")

# Export des dimensions
if 'dimension_country' in locals():
    dimension_country.toPandas().to_csv(f"{export_dir}/dimension_country.csv", index=False)
else:
    print("Erreur : La table `dimension_country` n'est pas définie.")

if 'dimension_date' in locals():
    dimension_date.toPandas().to_csv(f"{export_dir}/dimension_date.csv", index=False)
else:
    print("Erreur : La table `dimension_date` n'est pas définie.")

print("Fichiers exportés avec succès dans le répertoire local.")

# Vérification du contenu du répertoire
print("Contenu du répertoire d'exports :")
print(os.listdir(export_dir))


# Validation des données
try:
    fact_data = spark.read.format("delta").load("delta/gold/fact_covid_vaccinations")
    dimension_country = spark.read.format("delta").load("delta/gold/dimension_country")
    dimension_date = spark.read.format("delta").load("delta/gold/dimension_date")

    fact_data.show(5)
    dimension_country.show(5)
    dimension_date.show(5)
    print("Validation des données terminée avec succès.")
except Exception as e:
    print(f"Erreur lors de la validation : {e}")


# COMMAND ----------

# MAGIC %md
# MAGIC # Visualisation et Analyse

# COMMAND ----------

# MAGIC %md
# MAGIC ## Progression des vaccinations par pays
# MAGIC
# MAGIC - Visualisation de l'évolution des vaccinations dans chaque pays à travers le temps.
# MAGIC - Permet de comparer les tendances de vaccination entre différents pays.

# COMMAND ----------

from pyspark.sql.functions import col
import matplotlib.pyplot as plt
import pandas as pd

# Agrégation des données par pays et date
vaccination_progress = fact_table.groupBy("COUNTRY", "DATE_UPDATED") \
    .agg({"total_vaccinations": "sum"}) \
    .withColumnRenamed("sum(total_vaccinations)", "total_vaccinations_sum")

# Conversion des données en Pandas DataFrame
vaccination_df = vaccination_progress.toPandas()

# Nettoyage des données
vaccination_df = vaccination_df.dropna(subset=["DATE_UPDATED", "total_vaccinations_sum"])
vaccination_df["DATE_UPDATED"] = pd.to_datetime(vaccination_df["DATE_UPDATED"])
vaccination_df = vaccination_df.sort_values(by="DATE_UPDATED")

# Vérification des valeurs pour chaque pays (Debugging Step)
print("Vérification des données avant normalisation :")
for country in vaccination_df["COUNTRY"].unique()[:5]:
    country_data = vaccination_df[vaccination_df["COUNTRY"] == country]
    print(f"Progression des vaccinations pour {country}:")
    print(country_data[["DATE_UPDATED", "total_vaccinations_sum"]].head(10))
    print("\n")

# Normalisation des dates pour chaque pays
all_dates = pd.date_range(start=vaccination_df["DATE_UPDATED"].min(), 
                          end=vaccination_df["DATE_UPDATED"].max())

# Création d'une nouvelle table avec des dates uniformisées et interpolation
normalized_data = []

for country in vaccination_df["COUNTRY"].unique()[:5]:  # Sélection des 5 premiers pays
    country_data = vaccination_df[vaccination_df["COUNTRY"] == country]
    country_data = country_data.set_index("DATE_UPDATED").reindex(all_dates)
    country_data["total_vaccinations_sum"] = country_data["total_vaccinations_sum"].interpolate()
    country_data["COUNTRY"] = country  # Réajoute la colonne pays
    normalized_data.append(country_data)

# Fusion des données normalisées
normalized_df = pd.concat(normalized_data).reset_index()
normalized_df.rename(columns={"index": "DATE_UPDATED"}, inplace=True)

# Ajout de progression cumulée pour visualisation plus dynamique
normalized_df["cumulative_vaccinations"] = normalized_df.groupby("COUNTRY")["total_vaccinations_sum"].cumsum()

# Visualisation de la progression cumulative
plt.figure(figsize=(12, 6))
for country in normalized_df["COUNTRY"].unique():
    country_data = normalized_df[normalized_df["COUNTRY"] == country]
    plt.plot(country_data["DATE_UPDATED"], country_data["cumulative_vaccinations"], label=country)

plt.xlabel("Date")
plt.ylabel("Cumulative Vaccinations")
plt.title("Progression cumulée des vaccinations par pays (avec dates normalisées)")
plt.legend()
plt.grid(True)
plt.show()


# COMMAND ----------

# MAGIC %md
# MAGIC #  Comparaison des vaccinations par région OMS
# MAGIC Description : Ce graphique en barres présente le nombre total de vaccinations agrégées par région OMS. Cela permet de comparer rapidement les performances de chaque région en matière de couverture vaccinale.

# COMMAND ----------

from pyspark.sql.functions import col
import matplotlib.pyplot as plt
import pandas as pd

# Agrégation des vaccinations par région OMS
region_aggregation = fact_table.groupBy("WHO_REGION") \
    .agg({"total_vaccinations": "sum"}) \
    .withColumnRenamed("sum(total_vaccinations)", "total_vaccinations_sum")

# Conversion en Pandas DataFrame
region_df = region_aggregation.toPandas()

# Trier par ordre décroissant
region_df = region_df.sort_values(by="total_vaccinations_sum", ascending=False)

# Affichage sous forme de graphique barre avec annotations et couleurs personnalisées
plt.figure(figsize=(10, 6))
colors = plt.cm.viridis(range(len(region_df)))  # Palette de couleurs dynamique

bars = plt.bar(region_df["WHO_REGION"], region_df["total_vaccinations_sum"], color=colors)

# Ajouter des annotations pour chaque barre
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + yval*0.01, f'{int(yval):,}', 
             ha='center', va='bottom', fontsize=10, rotation=45)

# Configuration du graphique
plt.title("Comparaison des vaccinations par région OMS (Tri décroissant)")
plt.ylabel("Total Vaccinations")
plt.xlabel("Région OMS")
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Afficher le graphique
plt.show()


# COMMAND ----------

# MAGIC %md
# MAGIC # Analyse temporelle des vaccinations
# MAGIC Description : Ce graphique linéaire illustre la progression des vaccinations cumulées par année. L'axe des abscisses représente les années, tandis que l'axe des ordonnées montre le total des vaccinations.

# COMMAND ----------

from pyspark.sql.functions import year
import matplotlib.pyplot as plt
import numpy as np

# Agrégation des données par année
yearly_vaccinations = fact_table.withColumn("year", year("DATE_UPDATED")) \
    .groupBy("year").agg({"total_vaccinations": "sum"}) \
    .withColumnRenamed("sum(total_vaccinations)", "total_vaccinations_sum")

# Conversion en Pandas DataFrame
yearly_df = yearly_vaccinations.toPandas()

# Nettoyage des valeurs NaN ou inf
yearly_df = yearly_df.dropna(subset=["year", "total_vaccinations_sum"])
yearly_df = yearly_df.replace([np.inf, -np.inf], np.nan).dropna()

# Affichage des résultats avec améliorations
plt.figure(figsize=(10, 6))
plt.plot(yearly_df["year"], yearly_df["total_vaccinations_sum"], 
         marker='o', linestyle='-', color='tab:blue', label='Total Vaccinations')

# Annotations des points
for x, y in zip(yearly_df["year"], yearly_df["total_vaccinations_sum"]):
    plt.text(x, y, f'{y:,.0f}', ha='center', va='bottom', fontsize=10)

# Configuration des axes et du titre
plt.title("Analyse temporelle des vaccinations (par année)", fontsize=14)
plt.xlabel("Année", fontsize=12)
plt.ylabel("Total Vaccinations", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(yearly_df["year"].astype(int))  # Format des années en entier
plt.legend()

# Affichage du graphique
plt.show()


# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## 🎯 **Conclusion du Projet**
# MAGIC
# MAGIC Le projet a permis de construire une **pipeline de données robuste et scalable** en utilisant l'architecture **Lakehouse** avec les zones **Bronze**, **Silver** et **Gold**. Voici les principaux résultats obtenus :  
# MAGIC
# MAGIC 1. **Ingestion et stockage des données brutes** :  
# MAGIC    - Les données sources ont été chargées dans la **zone Bronze** sans aucune transformation pour assurer leur traçabilité et permettre un retraitement en cas de besoin.
# MAGIC
# MAGIC 2. **Nettoyage et transformation** :  
# MAGIC    - Dans la **zone Silver**, les données ont été normalisées et enrichies :  
# MAGIC      - Suppression des colonnes inutiles.  
# MAGIC      - Gestion des valeurs manquantes.  
# MAGIC      - Conversion des types de données (ex : dates).  
# MAGIC
# MAGIC 3. **Modélisation en étoile** :  
# MAGIC    - La **zone Gold** a été structurée en utilisant un **modèle en étoile** comprenant :  
# MAGIC      - Une **table Fait** pour les mesures analytiques.  
# MAGIC      - Des **tables Dimensions** pour les informations temporelles et géographiques.
# MAGIC
# MAGIC 4. **Visualisations et analyses** :  
# MAGIC    - Les résultats obtenus ont été analysés grâce à des visualisations claires et interactives :  
# MAGIC      - **Progression des vaccinations par pays**.  
# MAGIC      - **Comparaison des vaccinations par région OMS**.  
# MAGIC      - **Analyse temporelle des vaccinations cumulées par année**.  
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## 📊 **Impact et Perspectives**
# MAGIC
# MAGIC - **Impact du projet** :  
# MAGIC    Ce pipeline permet d'obtenir des **insights exploitables** sur les progrès de la vaccination dans le monde, facilitant la prise de décision par les analystes et les décideurs.
# MAGIC
# MAGIC - **Perspectives d'amélioration** :  
# MAGIC    - Intégration de **flux en temps réel** avec des outils comme **Kafka** ou **Redpanda**.  
# MAGIC    - Ajout de **données supplémentaires** pour affiner les analyses (ex : démographie, densité).  
# MAGIC    - Utilisation de **Airbyte** pour une ingestion de données automatisée et optimisée.  
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC 🚀 **En conclusion, ce projet démontre la puissance de l'architecture Lakehouse associée aux outils modernes comme Databricks et Apache Spark pour l'ingénierie et l'analyse de données.**
# MAGIC
