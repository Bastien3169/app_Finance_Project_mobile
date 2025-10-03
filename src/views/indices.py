    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.


import flet as ft
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from base64 import b64encode
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *


# Connexion DB et récupération des données
datas_indices = FinanceDatabaseIndice(db_path="data.db")
liste_indices = datas_indices.get_list_indices()
infos_indices = datas_indices.get_infos_indices()
indice_default = "S&P 500"


################################## GRAPHIQUE #################################################

def indices_page(page: ft.Page):
    page.clean()
    page.scroll = "auto"
    
    # Dropdown
    dropdown_indice = ft.Dropdown(label="Choisissez un indice pour le graphique", value=indice_default, options=[ft.dropdown.Option(indice) for indice in liste_indices], width=300)
    
    # PlotlyChart (vide au départ)
    chart = PlotlyChart(figure=go.Figure())
    
    def update_graph(e): # Met à jour le graphique quand on change l'indice
        
        selected_indice = dropdown_indice.value
        
        # Récupération des données
        df = datas_indices.get_prix_date(selected_indice)
        
        # Convertir les dates en string
        df['Date'] = df['Date'].astype(str)
        
        # Créer le graphique
        fig = go.Figure(go.Scatter(x=df["Date"], y=df["Close"], mode='lines', name=selected_indice, line=dict(color='#6DBE8C', width=2)))
        fig.update_layout(title=f"Évolution de {selected_indice}", xaxis_title="Date", yaxis_title="Prix de clôture", width=340, height=300, hovermode='x unified', dragmode='zoom')
        
        # Mettre à jour le chart
        chart.figure = fig
        page.update()

    # Lier l'événement de changement
    dropdown_indice.on_change = update_graph
    
    # Ajouter à la page
    page.add(ft.Text("📈 Graphiques des indices", color=ft.Colors.AMBER_200, size=24), dropdown_indice, chart)
    
    # Charger le graphique initial
    update_graph(None)