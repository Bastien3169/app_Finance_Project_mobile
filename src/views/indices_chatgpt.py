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
import io
from PIL import Image
from src.models.control_datas.connexion_db_datas import *

def indices_page(page: ft.Page):
    page.title = "📊 Indices financiers"
    page.scroll = "adaptive"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Connexion à la base
    datas_indices = FinanceDatabaseIndice(db_path="data.db")
    liste_indices = datas_indices.get_list_indices()
    infos_indices = datas_indices.get_infos_indices()
    indice_default = "S&P 500"


############################ GRAPH ############################
    def update_graph(e):
        selected_indice = dropdown_graph.value
        df = datas_indices.get_prix_date(selected_indice)

        if not df.empty:
            fig = go.Figure(
                go.Scatter(
                    x=df["Date"],
                    y=df["Close"],
                    mode='lines',
                    name=selected_indice,
                    line=dict(color='#6DBE8C', width=2)
                )
            )
            fig.update_layout(
                title=f"Évolution de {selected_indice} - Clôture hebdomadaire",
                xaxis_title="Date",
                yaxis_title="Prix de clôture",
            )

            # Convertir le graphique Plotly en image PNG
            buf = io.BytesIO()
            fig.write_image(buf, format="png")
            buf.seek(0)
            img_data = buf.read()
            img_b64 = b64encode(img_data).decode("ascii")

            # Afficher avec ft.Image
            graph_container.content = ft.Image(src=f"data:image/png;base64,{img_b64}", fit="contain", expand=True)
        else:
            graph_container.content = ft.Text("❌ Aucune donnée trouvée pour cet indice.", color="red")

        page.update()



    ############################ TABLEAU RENDEMENT ############################
    title_rend = ft.Text("💯 Rendements des indices (%)", size=20, weight=ft.FontWeight.BOLD)

    multiselect_table = ft.Dropdown(
        label="Ajoutez des indices au tableau pour comparer",
        options=[ft.dropdown.Option(i) for i in liste_indices],
        value=indice_default,
        width=300
    )

    rendement_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Indice")),
        ft.DataColumn(ft.Text("6 mois")),
        ft.DataColumn(ft.Text("12 mois")),
        ft.DataColumn(ft.Text("24 mois")),
        ft.DataColumn(ft.Text("60 mois")),
        ft.DataColumn(ft.Text("120 mois")),
        ft.DataColumn(ft.Text("180 mois")),
        ft.DataColumn(ft.Text("Devise")),
    ])

    def update_rendement(e):
        rendement_table.rows.clear()
        periods = [6, 12, 24, 60, 120, 180]
        selected = [multiselect_table.value] if multiselect_table.value else []

        for i in selected:
            df_prix_date = datas_indices.get_prix_date(i)
            if not df_prix_date.empty:
                df_rendement = calculate_rendement(df_prix_date, periods)
                df_info = infos_indices[infos_indices["Short_Name_Indice"] == i]

                row_values = []
                for p in periods:
                    row_values.append(ft.DataCell(ft.Text(str(df_rendement[f"{p} mois"].iloc[0]))))

                devise = df_info.iloc[0]["Devise"] if not df_info.empty else "?"
                row = ft.DataRow(cells=[ft.DataCell(ft.Text(i))] + row_values + [ft.DataCell(ft.Text(devise))])
                rendement_table.rows.append(row)

        page.update()

    multiselect_table.on_change = update_rendement
    update_rendement(None)

    ############################ COMPOSITION INDICE ############################
    title_comp = ft.Text("🗂 Composition des indices", size=20, weight=ft.FontWeight.BOLD)

    dropdown_comp = ft.Dropdown(
        label="Choisissez un indice pour voir sa composition",
        options=[ft.dropdown.Option(i) for i in liste_indices],
        value=indice_default,
        width=300
    )

    compo_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Ticker")),
        ft.DataColumn(ft.Text("Nom")),
        ft.DataColumn(ft.Text("Pondération")),
        ft.DataColumn(ft.Text("Secteur")),
    ])

    def update_compo(e):
        compo_table.rows.clear()
        selected = dropdown_comp.value
        df_comp = datas_indices.get_composition_indice(selected)
        if not df_comp.empty:
            for _, row in df_comp.iterrows():
                compo_table.rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row.get("ticker_stock", ""))),
                        ft.DataCell(ft.Text(row.get("short_name", ""))),
                        ft.DataCell(ft.Text(str(row.get("pondération", "")))),
                        ft.DataCell(ft.Text(row.get("secteur_activité", ""))),
                    ]
                ))
        else:
            compo_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Pas de données"))]))

        page.update()

    dropdown_comp.on_change = update_compo
    update_compo(None)

    ############################ FOOTER ############################
    footer = ft.Text("© 2025 Bastien M. - Projet finance — Tous droits réservés.", size=12, italic=True)

    ############################ LAYOUT FINAL ############################
    page.add(
        title_graph, dropdown_graph, graph_container,
        ft.Divider(),
        title_rend, multiselect_table, rendement_table,
        ft.Divider(),
        title_comp, dropdown_comp, compo_table,
        ft.Divider(),
        footer
    )

