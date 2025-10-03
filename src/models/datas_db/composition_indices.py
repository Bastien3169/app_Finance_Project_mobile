import pandas as pd
import yfinance as yf
import time
import os
from . import scraping_tickers  # Import de ta fonction scraping

def get_stock_data(tickers_stocks_yf, nom_indice, ticker_indice_yf, file_path):
    
    # Création du DataFrame initial avec une colonne vide
    df = pd.DataFrame({'Ticker_Stocks_Yf': tickers_stocks_yf})

    # Récupérer toutes les données en une seule requête
    tickers_obj = yf.Tickers(" ".join(tickers_stocks_yf))  # Récupération groupée des tickers

    # Initialisation des listes pour stocker les données
    short_name_stocks = []
    pays_stocks = []
    place_boursiere = []
    secteur_activite = []
    capitalisation_boursiere = []
    tickers_stocks = []

    for i in tickers_stocks_yf:
        try:
            # Récupérer les informations via l'objet Tickers
            info = tickers_obj.tickers[i].info

            # Extraction du ticker sans suffixe
            symbole_sans_suffixe = i.split(".")[0]
            tickers_stocks.append(symbole_sans_suffixe)

            # Ajouter les informations dans leurs listes respectives
            short_name_stocks.append(info.get('shortName', 'Non disponible'))
            pays_stocks.append(info.get('country', 'Non disponible'))
            place_boursiere.append(info.get('exchange', 'Non disponible'))
            secteur_activite.append(info.get('sector', 'Non disponible'))
            capitalisation_boursiere.append(info.get('marketCap', None))

        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {i}: {e}")
            short_name_stocks.append('Non disponible')
            pays_stocks.append('Non disponible')
            place_boursiere.append('Non disponible')
            secteur_activite.append('Non disponible')
            capitalisation_boursiere.append(None)
            tickers_stocks.append(i)  # Ajouter le ticker original en cas d'erreur

        time.sleep(0.5)  # Petite pause pour éviter le blocage

    # Ajout des colonnes au DataFrame
    df['Short_Name_Stocks'] = short_name_stocks
    df['Pays_Stocks'] = pays_stocks
    df['Place_Boursiere'] = place_boursiere
    df['Secteur_Activite'] = secteur_activite
    df['Capitalisation_Boursiere'] = capitalisation_boursiere
    df['Ticker_Stocks'] = tickers_stocks
    df['Nom_Indice'] = nom_indice
    df['Nombres_Entreprises'] = len(short_name_stocks)
    df['Ticker_Indice_Yf'] = ticker_indice_yf

    # Calcul de la capitalisation boursière totale
    total_capitalisation = df['Capitalisation_Boursiere'].fillna(0).sum()

    # Calcul pondération
    df['Ponderation'] = round((df['Capitalisation_Boursiere'] / total_capitalisation) * 100, 2)

    # Réorganisation des colonnes
    df = df[
        ['Short_Name_Stocks', 'Ticker_Stocks_Yf', 'Ticker_Stocks', 'Secteur_Activite', 'Pays_Stocks', 'Place_Boursiere', 
         'Capitalisation_Boursiere', 'Nom_Indice', 'Ticker_Indice_Yf', 'Nombres_Entreprises', 'Ponderation']
    ]

    # Exportation en CSV
    df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"[✅] Le fichier pour l'indice '{nom_indice}' a bien été enregistré sous le nom : {file_path}")

    return df


def csv_indices(dossier_csv = "csv/"):
    
    # Récupérer les tickers via scraping_tickers.all_tickers_yf()
    tickers_yf = scraping_tickers.all_tickers_yf()
    
    # Appels avec jointure automatique du chemin
    df_cac40 = get_stock_data(tickers_yf["CAC40"], "CAC 40", "^FCHI", os.path.join(dossier_csv, "composition_france.csv"))
    df_sp500 = get_stock_data(tickers_yf["SP500"], "S&P 500", "^GSPC", os.path.join(dossier_csv, "composition_sp500.csv"))

'''    df_dax40 = get_stock_data(tickers_yf["DAX40"], "DAX", "^GDAXI", os.path.join(base_csv_path, "composition_dax.csv"))
    df_italie40 = get_stock_data(tickers_yf["Italie40"], "FTSE MIB Index", "FTSEMIB.MI", os.path.join(base_csv_path, "composition_italie.csv"))
    df_espagne35 = get_stock_data(tickers_yf["Espagne35"], "IBEX 35", "^IBEX", os.path.join(base_csv_path, "composition_espagne.csv"))
    df_angleterre = get_stock_data(tickers_yf["Angleterre100"], "FTSE 100", "^FTSE", os.path.join(base_csv_path, "composition_angleterre.csv"))
    df_nasdaq100 = get_stock_data(tickers_yf["NASDAQ100"], "NASDAQ 100", "^NDX", os.path.join(base_csv_path, "composition_nasdaq100.csv"))
    df_dowjones = get_stock_data(tickers_yf["Dow Jones"], "Dow Jones 30", "^DJI", os.path.join(base_csv_path, "composition_dowjones.csv"))
    df_belgique = get_stock_data(tickers_yf["Belgique20"], "BEL 20", "^BFX", os.path.join(base_csv_path, "composition_belgique.csv"))
    df_pays_bas = get_stock_data(tickers_yf["Paysbas25"], "AEX-Index", "^AEX", os.path.join(base_csv_path, "composition_paysbas.csv"))
    df_finlande = get_stock_data(tickers_yf["Finlande25"], "OMX Helsinki 25", "^OMXH25", os.path.join(base_csv_path, "composition_finlande.csv"))
    df_suede = get_stock_data(tickers_yf["Suède30"], "OMX Stockholm 30", "^OMXS30", os.path.join(base_csv_path, "composition_suede.csv"))
    df_danemark = get_stock_data(tickers_yf["Danemark25"], "OMX Copenhagen 25", "^OMXC25", os.path.join(base_csv_path, "composition_danemark.csv"))
    df_stoxx50 = get _stock_data(tickers_yf["STOXX50"], "STOXX 50", "^STOXX50E", os.path.join(base_csv_path, "composition_europe50.csv"))
    df_japon225 = get_stock_data(tickers_yf["Japon225"], "Nikkei 225", "^N225", os.path.join(base_csv_path, "composition_japon.csv"))

    '''
if __name__ == "__main__":
    indices_csv = csv_indices("csv_test") #Appel de la fonction 