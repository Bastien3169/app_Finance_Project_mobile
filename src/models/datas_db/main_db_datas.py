# main.py
import os
from . import scraping_tickers  # Pour récupérer les tickers
from . import composition_indices  # Pour obtenir les infos des entreprises par indice
from . import infos_stocks  # Pour concaténer les informations des entreprises et les stocker en CSV
from . import infos_indices  # Pour récupérer les infos des indices et les stocker en CSV
from . import hist_indices  # Pour récupérer l'historique des prix des indices
from . import hist_stocks  # Pour récupérer l'historique des prix des entreprises
from . import sql_datas # Pour créer la base de donnée sql

def main_db_datas(dossier_csv = "csv", csv_bdd = "csv/csv_bdd", db_path = "datas.bd"):

    #scraping_tickers.all_tickers_yf()

    # Étape 1: Scraper les tickers de chaque indice et Récupérer les informations des entreprises pour chaque indice
    composition_indices.csv_indices(dossier_csv)

    # Étape 2: Concaténer et sauvegarder les données des entreprises
    infos_stocks.infos_stocks(dossier_csv, csv_bdd) 

    # Étape 3: Récupérer et sauvegarder les informations des indices
    infos_indices.infos_indices(dossier_csv, csv_bdd)

    # Étape 4: Récupérer et sauvegarder l'historique des prix des indices
    hist_indices.recuperer_et_clean_indices(csv_bdd)

    # Étape 5: Récupérer et sauvegarder l'historique des prix des entreprises
    hist_stocks.recuperer_et_clean_stocks(csv_bdd)

    # Étape 6 : Création de la base de donnée
    sql_datas.main_creation_db(csv_bdd, db_path)

    print("[✅]✅] Toutes les étapes ont été exécutées avec succès.")

if __name__ == "__main__":
    main_db_datas("csv", "csv/csv_bdd", "datas.bd")