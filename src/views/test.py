import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *

'''
Le problème à cause du format des dates (datetime64[ns]). Conversion en string et ok pour PlotlyChart.
'''

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
    page.add(ft.Text("📈 Graphiques des indices", color=ft.Colors.CYAN_500, size=24), dropdown_indice, chart)
    
    # Charger le graphique initial
    update_graph(None)


################################## TABLEAU RENDEMENT ########################################

################################## TABLEAU COMPARATIF RENDEMENTS #################################################

    ft.Divider(height=20, thickness=2)
    ft.Text("💯 Rendements des indices (%)", color=ft.Colors.CYAN_500, size=24)
    
    # Dropdown multi-sélection (plus propre qu'une liste de checkboxes)
    indices_selectionnes = [indice_default]
    
    dropdown_multi = ft.Dropdown(
        label="Sélectionnez les indices à comparer",
        hint_text="Choisissez un ou plusieurs indices",
        width=300,
        options=[ft.dropdown.Option(indice) for indice in liste_indices],
        on_change=lambda e: ajouter_indice(e.control.value)
    )
    
    # Liste des indices sélectionnés
    liste_selection = ft.Column()
    
    # DataTable
    table = ft.DataTable(
        column_spacing=8, # Espace entre les colonnes
        columns=[
            ft.DataColumn(ft.Text("Indice", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("6m", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("12m", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("24m", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("60m", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("120m", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("180m", weight=ft.FontWeight.BOLD))
        ],
        rows=[]
    )
    
    def ajouter_indice(indice):
        """Ajoute un indice à la sélection"""
        if indice and indice not in indices_selectionnes:
            indices_selectionnes.append(indice)
            update_selection_list()
            update_table()
    
    def retirer_indice(indice):
        """Retire un indice de la sélection"""
        if indice in indices_selectionnes:
            indices_selectionnes.remove(indice)
            update_selection_list()
            update_table()
    
    def update_selection_list():
        """Met à jour la liste des indices sélectionnés"""
        liste_selection.controls.clear()
        for indice in indices_selectionnes:
            liste_selection.controls.append(
                ft.Row([
                    ft.Text(indice, size=12),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,  # ← I majuscule
                        icon_size=16,
                        on_click=lambda e, i=indice: retirer_indice(i)
                    )
                ])
            )
        page.update()
        
    def update_table():
        """Met à jour le tableau"""
        table.rows.clear()
        periods = [6, 12, 24, 60, 120, 180]
        
        for indice in indices_selectionnes:
            df = datas_indices.get_prix_date(indice)
            
            if not df.empty:
                rendements = calculate_rendement(df, periods)
                
                # Convertir en float si c'est une string
                cells = [ft.DataCell(ft.Text(indice, size=11))]
                
                for period in periods:
                    valeur = rendements.get(f'{period} mois', 0)
                    try:
                        valeur_float = float(valeur)
                        texte = f"{valeur_float:.1f}%"
                        # Couleur du TEXTE au lieu du fond
                        couleur_texte = ft.Colors.GREEN if valeur_float > 0 else ft.Colors.RED if valeur_float < 0 else ft.Colors.BLACK
                    except (ValueError, TypeError):
                        texte = str(valeur)
                        couleur_texte = ft.Colors.BLACK
                    
                    cells.append(
                        ft.DataCell(
                            ft.Text(texte, size=10, color=couleur_texte)  # ← color au lieu de bgcolor
                        )
                    )
                
                table.rows.append(ft.DataRow(cells=cells))
        
        page.update()
    
    page.add(
        dropdown_multi,
        ft.Text("Indices sélectionnés:", size=12, weight=ft.FontWeight.BOLD),
        liste_selection,
        ft.Container(
            content=table,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=5
        )
    )
    
    # Initialiser
    update_selection_list()
    update_table()