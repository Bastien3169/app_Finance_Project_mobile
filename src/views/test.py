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
def create_graph_section(page):
    page.scroll = "auto"

    # Widget : titre
    text_graphique = ft.Text("📈 Graphiques des indices", color=ft.Colors.AMBER_200, weight=ft.FontWeight.BOLD, size=21)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200),padding=ft.padding.only(bottom=15))

    # Widget : Dropdown (menu déroulant)
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez un indice pour le graphique", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        value=indice_default,
        options=[ft.dropdown.Option(indice) for indice in liste_indices],
        width=300
    )

    # Widget : graphique PlotlyChart vide
    graphique = PlotlyChart(figure=go.Figure(), visible=False)

    # Widget : loader (anneau de chargement)
    loader = ft.ProgressRing(color=ft.Colors.AMBER_200, visible=False, width=50, height=50)

    def update_graph(e):  # Met à jour le graphique quand on change l'indice
        loader.visible = True
        graphique.visible = False
        page.update()

        # Récupérer l'indice sélectionné
        selected_indice = dropdown_indice.value

        # Récupérer les données de l'indice sélectionné
        df = datas_indices.get_prix_date(selected_indice)

        # Convertir les dates en string
        df['Date'] = df['Date'].astype(str)

        # Créer le graphique avec Plotly
        fig = go.Figure(go.Scatter(
            x=df["Date"], y=df["Close"], mode='lines', name=selected_indice,
            line=dict(color='#6DBE8C', width=2)
        ))

        # Personnalisation du graphique
        fig.update_layout(
            title=f"Évolution de {selected_indice}",
            title_font=dict(size=22, color='white', family='Arial Black'),
            plot_bgcolor='black', 
            paper_bgcolor='black', 
            font=dict(color='white'),
            xaxis_title="Date", 
            yaxis_title="Prix de clôture",
            hovermode='x unified', 
            dragmode='zoom',
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis=dict(showgrid=False, zeroline=False, showline=False, tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.25)', zeroline=False, showline=False)
        )

        # Mise à jour du graphique
        graphique.figure = fig

        # Rendre le graphique visible après la première mise à jour pour pas avoir chart blanc au départ
        graphique.visible = True

        # Enlever le loader
        loader.visible = False

        # Mettre à jour la page
        page.update()

    # Lier "dropdown_indice" à la fonction "update_graph" grace à l'événement "on_change"  qui est un callback
    dropdown_indice.on_change = update_graph

    # Appel initial pour afficher le graphique par défaut
    update_graph(None)

    return [text_graphique, separation, dropdown_indice, loader, graphique]
    


################################## TABLEAU COMPARATIF RENDEMENTS ################################

def create_rendement_section(page):

    # Widget : titre dans container pour le padding
    text_rendement = ft.Container(content=ft.Text("💯 Rendements des indices (%)", color=ft.Colors.AMBER_200, weight=ft.FontWeight.BOLD, size=21),
                                  padding=ft.padding.only(top=35),
                                  )

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous 
    separation = ft.Container(content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200), padding=ft.padding.only(bottom=15))

    # Widget : Dropdown (menu déroulant)
    dropdown_multi = ft.Dropdown(
        label="Sélectionnez les indices à comparer",
        hint_text="Choisissez un ou plusieurs indices",
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
        width=300,
        options=[ft.dropdown.Option(i) for i in liste_indices], # éléments de la liste
        on_change=lambda e: ajouter_indice(e.control.value),
        value=indice_default  # Valeur par défaut (liste des indices sélectionnés)
        )

    # Liste des indices sélectionnés (initialisé avec un indice par défaut)
    indices_selectionnes = [indice_default]
    
    # Widget : liste des indices sélectionnés
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    # Cadre autour de la liste des indices sélectionnés
    cadre_text = ft.Container(
    content=ft.Column([ft.Text("Indices sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),liste_selection], 
                      horizontal_alignment=ft.CrossAxisAlignment.START),
                      padding=5,
                      border=ft.border.all(0.5, ft.Colors.WHITE30),
                      border_radius=10,
                      expand=True, # permet au container de prendre toute la largeur
                      alignment=ft.alignment.top_left # centre horizontalement le contenu
                      )
                    
    # Widget : tableau des rendements
    table = ft.DataTable(
        expand=True,
        column_spacing=10, # Espace entre les colonnes pour que tout rentre
        #vertical_lines=ft.BorderSide(1, ft.Colors.GREY_400), # Lignes verticales entre les colonnes
        heading_row_height=25,  # Hauteur de la ligne d'en-tête
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),  # Couleur de l'entête
        data_row_min_height=35,  # Hauteur minimale des lignes de données
        data_row_max_height=35,  # Hauteur maximale des lignes de données
        divider_thickness=0.5, # Epaisseur séparateur lignes
        columns=[
            ft.DataColumn(ft.Text("Indice", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("6m", weight=ft.FontWeight.BOLD, size=12),),
            ft.DataColumn(ft.Text("12m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("24m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("60m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("120m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("180m", weight=ft.FontWeight.BOLD, size=12))
        ],
        rows=[],
        )
    
    # Conteneur qui prend le tebleau  et qui l'encadre
    cadre_tableau = ft.Container(
        content=ft.Row([table], scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER), 
        border=ft.border.all(0.5, ft.Colors.AMBER_200),
        border_radius=10, 
        padding=5,
        alignment=ft.alignment.center,
    )

    # Fonction pour calculer les rendements
    def update_selection_list():
        liste_selection.controls.clear()
        for i in indices_selectionnes:
            liste_selection.controls.append(
                ft.Row([
                    ft.Text(i, size=12),
                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16,
                                  on_click=lambda e, i=i: retirer_indice(i))
                ])
            )
        page.update()

    # Fonction pour ajouter ou retirer un indice de la sélection
    def ajouter_indice(indice):
        if indice and indice not in indices_selectionnes:
            indices_selectionnes.append(indice)
            update_selection_list()
            update_table()

    # Fonction pour retirer un indice de la sélection
    def retirer_indice(indice):
        if indice in indices_selectionnes:
            indices_selectionnes.remove(indice)
            update_selection_list()
            update_table()

    # Fonction pour mettre à jour le tableau des rendements
    def update_table():
        # Met à jour le tableau
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
                        if valeur_float > 0:
                            couleur_texte = ft.Colors.GREEN
                        elif valeur_float < 0:
                            couleur_texte = ft.Colors.RED
                        else:
                            couleur_texte = ft.Colors.BLACK
                    except (ValueError, TypeError):
                        texte = str(valeur)
                        couleur_texte = ft.Colors.BLACK
                    
                    cells.append(
                        ft.DataCell(
                            ft.Text(texte, size=10, color=couleur_texte) # color au lieu de bgcolor
                        )
                    )
                
                table.rows.append(ft.DataRow(cells=cells))

        page.update()

    # Lier "dropdown_multi" à la fonction "ajouter_indice" grace à l'événement "on_change"  qui est un callback
    dropdown_multi.on_change = lambda e: ajouter_indice(e.control.value)
    
    # Initialisation des fonctions
    update_selection_list()
    update_table()

    return [
        text_rendement, 
        separation, 
        dropdown_multi, 
        cadre_text, 
        cadre_tableau
    ]


################################## COMPOSITION INDICES  ################################

def create_composition_section(page):
    
     # Widget : titre dans container pour le padding
    text_composition = ft.Container(content=ft.Text("🗂 Composition des indices",
                                                    color=ft.Colors.AMBER_200,
                                                    weight=ft.FontWeight.BOLD,
                                                    size=21),
                                                    padding=ft.padding.only(top=35))

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200),
                              padding=ft.padding.only(bottom=15))

    # Widget : Dropdown (menu déroulant)        
    dropdown_composition = ft.Dropdown(
        label="Sélectionnez la composition de l'indice",
        hint_text="Choisissez un indice",
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
        width=300,
        options=[ft.dropdown.Option(i) for i in liste_indices],
        value=indice_default
    )

    # Widget : tableau de la composition
    table_composition = ft.DataTable(
        column_spacing=10,
        heading_row_height=30,
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),  
        data_row_min_height=25,
        divider_thickness=0.5,
        columns=[ft.DataColumn(ft.Text("Chargement...", size=11))],
        rows=[]
    )

    # Cadre autour du tableau
    cadre_table_composition = ft.Container(
        content=ft.Column([ft.Row([table_composition], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
        border=ft.border.all(0.5, ft.Colors.AMBER_200),
        border_radius=10,
        padding=5,
        height=300,
    )

    # Fonction pour mettre à jour le tableau de composition
    def update_table_composition(indice):
        df = datas_indices.get_composition_indice(indice)
        table_composition.columns.clear()
        table_composition.rows.clear()
        for col in df.columns:
            table_composition.columns.append(ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11)))
        for _, row in df.iterrows():
            table_composition.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=10)) for v in row]))
        page.update()

    # Lier "dropdown_composition" à la fonction "update_table_composition" grace à l'événement "on_change"  qui est un callback
    dropdown_composition.on_change = lambda e: update_table_composition(e.control.value)
    
    # Appel initial pour afficher la composition par défaut
    update_table_composition(indice_default)

    return [text_composition, separation, dropdown_composition, cadre_table_composition]


################################### FONCTION PRINCIPALE ################################

def indices_page(page: ft.Page):
    page.clean()
    page.scroll = "auto"

    # Récupère tous les éléments
    graph_elements = create_graph_section(page)
    rendement_elements = create_rendement_section(page)
    composition_elements = create_composition_section(page)

    # Bouton Retour accueil
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.AMBER_700,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/")  # Redirection vers la page d'accueil
    )

    # Container pour centrer le bouton
    container_bouton = ft.Container(
        content=bouton_retour,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20)  # Espacement avant et après
    )

    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        *graph_elements,
        *rendement_elements, 
        *composition_elements,
        container_bouton  # Bouton en dernier
    )
