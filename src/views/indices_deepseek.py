    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.


import flet as ft
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from base64 import b64encode
from src.models.control_datas.connexion_db_datas import *

class IndicesApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.datas_indices = FinanceDatabaseIndice(db_path="data.db")
        self.liste_indices = self.datas_indices.get_list_indices()
        self.infos_indices = self.datas_indices.get_infos_indices()
        self.indice_default = "S&P 500"
        self.rendement_data = pd.DataFrame()
        self.build_ui()

    def setup_page(self):
        self.page.title = "Finance Facile - Indices"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.ADAPTIVE

    def build_ui(self):
        # Titre principal
        title = ft.Container(
            content=ft.Text("Bienvenue sur Finance facile !", size=24, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(bottom=20)
        )

        # Section Graphique
        graph_section = self.build_graph_section()
        
        # Section Rendement
        rendement_section = self.build_rendement_section()
        
        # Section Composition
        composition_section = self.build_composition_section()
        
        # Footer
        footer = ft.Container(
            content=ft.Text("© 2025 Bastien M. - Projet finance — Tous droits réservés.", 
                          size=12, color=ft.Colors.GREY_600),
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=40)
        )

        # Ajouter tous les éléments à la page
        self.page.add(
            title,
            graph_section,
            rendement_section,
            composition_section,
            footer
        )

    def build_graph_section(self):
        # Titre section graphique
        graph_title = ft.Text("📈 Graphiques des indices", size=20, weight=ft.FontWeight.BOLD)
        
        # Dropdown pour sélectionner l'indice
        self.graph_dropdown = ft.Dropdown(
            label="Choisissez un indice pour le graphique",
            options=[ft.dropdown.Option(indice) for indice in self.liste_indices],
            value=self.indice_default,
            width=400,
            on_change=self.update_graph
        )
        
        # Container pour le graphique
        self.graph_container = ft.Container(
            height=400,
            alignment=ft.alignment.center
        )
        
        # Initialiser le graphique
        self.update_graph(None)
        
        return ft.Column([
            graph_title,
            self.graph_dropdown,
            self.graph_container
        ], spacing=15)

    def update_graph(self, e):
        selected_indice = self.graph_dropdown.value
        df = self.datas_indices.get_prix_date(selected_indice)
        
        if not df.empty:
            # Créer le graphique Plotly
            fig = go.Figure(go.Scatter(
                x=df["Date"], 
                y=df["Close"], 
                mode='lines', 
                name=selected_indice, 
                line=dict(color='#6DBE8C', width=2)
            ))
            fig.update_layout(
                title=f"Évolution de {selected_indice} - Clôture hebdomadaire",
                xaxis_title="Date",
                yaxis_title="Prix de clôture",
                height=350
            )
            
            # Convertir en HTML et afficher
            graph_html = fig.to_html(include_plotlyjs="cdn", include_mathjax="cdn", full_html=False)
            self.graph_container.content = ft.Markdown(f"```html\n{graph_html}\n```")
        else:
            self.graph_container.content = ft.Text(
                "Aucune donnée trouvée pour cet indice.",
                color=ft.colors.RED,
                weight=ft.FontWeight.BOLD
            )
        
        self.page.update()

    def build_rendement_section(self):
        # Titre section rendement
        rendement_title = ft.Text("💯 Rendements des indices (%)", size=20, weight=ft.FontWeight.BOLD)
        
        # Multi-select pour les indices
        self.rendement_dropdown = ft.Dropdown(
            label="Ajoutez des indices au tableau pour comparer",
            options=[ft.dropdown.Option(indice) for indice in self.liste_indices],
            value=self.indice_default,
            width=400,
            on_change=self.update_rendement_table
        )
        
        # Container pour le tableau
        self.rendement_table_container = ft.Container(
            padding=10
        )
        
        # Initialiser le tableau
        self.update_rendement_table(None)
        
        return ft.Column([
            rendement_title,
            self.rendement_dropdown,
            self.rendement_table_container
        ], spacing=15)

    def update_rendement_table(self, e):
        selected_indices = [self.rendement_dropdown.value] if self.rendement_dropdown.value else []
        
        # Mettre à jour les données de rendement (simplifié)
        periods = [6, 12, 24, 60, 120, 180]
        
        # Créer un tableau simple avec les données
        if selected_indices:
            table_rows = []
            
            # En-tête du tableau
            header_row = ft.DataRow(cells=[
                ft.DataCell(ft.Text("Indice", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("6 mois", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("12 mois", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text("24 mois", weight=ft.FontWeight.BOLD)),
            ])
            table_rows.append(header_row)
            
            # Données (exemple simplifié)
            for indice in selected_indices:
                df_prix_date = self.datas_indices.get_prix_date(indice)
                if not df_prix_date.empty:
                    df_rendement = calculate_rendement(df_prix_date, periods)
                    
                    cells = [ft.DataCell(ft.Text(indice))]
                    for period in periods[:3]:  # Afficher seulement 3 périodes pour l'exemple
                        rendement = df_rendement.get(f"{period} mois", "N/A")
                        cell_text = ft.Text(
                            str(rendement),
                            color=self.get_rendement_color(rendement)
                        )
                        cells.append(ft.DataCell(cell_text))
                    
                    table_rows.append(ft.DataRow(cells=cells))
            
            data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Indice")),
                    ft.DataColumn(ft.Text("6 mois")),
                    ft.DataColumn(ft.Text("12 mois")),
                    ft.DataColumn(ft.Text("24 mois")),
                ],
                rows=table_rows
            )
            
            self.rendement_table_container.content = data_table
        else:
            self.rendement_table_container.content = ft.Text(
                "Veuillez sélectionner au moins un indice",
                color=ft.Colors.GREY
            )
        
        self.page.update()

    def get_rendement_color(self, rendement):
        try:
            rendement_value = float(rendement)
            if rendement_value > 0:
                return ft.Colors.GREEN
            elif rendement_value < 0:
                return ft.Colors.RED
            else:
                return ft.Colors.BLACK
        except:
            return ft.Colors.BLACK

    def build_composition_section(self):
        # Titre section composition
        composition_title = ft.Text("🗂 Composition des indices", size=20, weight=ft.FontWeight.BOLD)
        
        # Dropdown pour sélectionner l'indice
        self.composition_dropdown = ft.Dropdown(
            label="Choisissez un indice pour voir sa composition",
            options=[ft.dropdown.Option(indice) for indice in self.liste_indices],
            value=self.indice_default,
            width=400,
            on_change=self.update_composition
        )
        
        # Container pour la composition
        self.composition_container = ft.Container(
            padding=10
        )
        
        # Initialiser la composition
        self.update_composition(None)
        
        return ft.Column([
            composition_title,
            self.composition_dropdown,
            self.composition_container
        ], spacing=15)

    def update_composition(self, e):
        selected_indice = self.composition_dropdown.value
        
        if selected_indice:
            df_composition_indice = self.datas_indices.get_composition_indice(selected_indice)
            
            if not df_composition_indice.empty:
                # Créer un tableau simple avec les données de composition
                table_rows = []
                
                # En-tête
                header_row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Entreprise", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("Poids", weight=ft.FontWeight.BOLD)),
                ])
                table_rows.append(header_row)
                
                # Données (limitées aux 10 premières pour l'exemple)
                for _, row in df_composition_indice.head(10).iterrows():
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(row.iloc[0]))),  # Première colonne
                        ft.DataCell(ft.Text(str(row.iloc[1]))),  # Deuxième colonne
                    ]))
                
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Entreprise")),
                        ft.DataColumn(ft.Text("Poids")),
                    ],
                    rows=table_rows
                )
                
                self.composition_container.content = ft.Column([
                    ft.Text(f"Composition de l'indice {selected_indice}:"),
                    data_table
                ])
            else:
                self.composition_container.content = ft.Text(
                    f"Pas de données disponibles pour l'indice {selected_indice}.",
                    color=ft.Colors.GREY
                )
        
        self.page.update()

def indices_page(page: ft.Page):
    page.clean()
    IndicesApp(page)








