    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.

import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *


# Connexion DB et récupération des données
datas_stocks = FinanceDatabaseStocks(db_path="data.db")
liste_actifs = datas_stocks.get_list_stocks()
infos_actifs = datas_stocks.get_infos_stocks()
actif_default = "Apple Inc."

couleur_titre_separateur = ft.Colors.GREEN_200
couleur_bouton_fleche = ft.Colors.GREEN_700

################################## GRAPHIQUE #################################################
def create_graph_section(page):
    page.scroll = "auto"
    
    # Widget : titre
    text_graphique = ft.Text("📈 Graphiques entreprise", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=21)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur),padding=ft.padding.only(bottom=15))

    # Widget : Dropdown (menu déroulant)
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez une entreprise", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        value=actif_default,
        options=[ft.dropdown.Option(indice) for indice in liste_actifs],
        width=300
    )

    # Widget : graphique PlotlyChart vide
    graphique = PlotlyChart(figure=go.Figure(), visible=False)

    # Widget : loader (anneau de chargement)
    loader = ft.ProgressRing(color=couleur_titre_separateur, visible=False, width=50, height=50)

    def update_graph(e):  # Met à jour le graphique quand on change l'indice
        loader.visible = True
        graphique.visible = False
        page.update()

        # Récupérer l'indice sélectionné
        selected_indice = dropdown_indice.value

        # Récupérer les données de l'indice sélectionné
        df = datas_stocks.get_prix_date(selected_indice)

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

    periods_selectionnees = [6, 12, 24, 60, 120, 180]  # affichées au début

    # --- Titre ---
    text_rendement = ft.Container(
        content=ft.Text("💯 Rendements entreprises (%)",
                        color=couleur_titre_separateur,
                        weight=ft.FontWeight.BOLD,
                        size=21),
        padding=ft.padding.only(top=35),
    )

    # --- Séparateur ---
    separation = ft.Container(
        content=ft.Divider(thickness=2, color=couleur_titre_separateur),
        padding=ft.padding.only(bottom=15)
    )

    # --- Sélection des indices ---
    dropdown_multi = ft.Dropdown(
        label="Sélectionnez les entreprises à comparer",
        hint_text="Choisissez une ou plusieurs entreprises",
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
        width=300,
        options=[ft.dropdown.Option(i) for i in liste_actifs],
        on_change=lambda e: ajouter_indice(e.control.value),
        value=actif_default
    )

    indices_selectionnes = [actif_default]
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_text = ft.Container(
        content=ft.Column([
            ft.Text("Entreprises sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
            liste_selection
        ],
            horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=5,
        border=ft.border.all(0.5, ft.Colors.WHITE30),
        border_radius=10,
        expand=True,
        alignment=ft.alignment.top_left
    )

    # Text pour période à ajouter
    text_periode = ft.Text("Ajouter une période (en mois)", size=11,style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),)

    # Input période à ajouter
    input_periode = ft.TextField(width=200,
                                keyboard_type=ft.KeyboardType.NUMBER, 
                                label="Ex: 3, 9, 18...", 
                                label_style=ft.TextStyle(size=12, italic=True),
                                on_submit=lambda e: ajouter_periode(e.control.value), 
                                text_style=ft.TextStyle(size=11))
    
    # Bouton "+" pour ajouter la période
    bouton_ajouter_periode = ft.IconButton(icon=ft.Icons.ADD, 
                                           tooltip="Ajouter la période", 
                                           on_click=lambda e: ajouter_periode(input_periode.value))

    # Ligne pour l'input et le bouton "+"
    ligne_ajout_periode = ft.Row([input_periode, bouton_ajouter_periode], 
                                 alignment=ft.MainAxisAlignment.START, 
                                 spacing=10)

    # Conteneur pour les périodes sélectionnées
    liste_periodes = ft.Row(scroll=ft.ScrollMode.AUTO)

    # Cadre complet regroupant tout
    cadre_periodes = ft.Container(content=ft.Column([text_periode,
                                                     ligne_ajout_periode,
                                                     ft.Text("Périodes sélectionnées (en mois) :", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
                                                    liste_periodes,],  # <= ici on l’ajoute DANS le cadre
                                                    spacing=10,
                                                    alignment=ft.MainAxisAlignment.START),
                                padding=10,
                                border=ft.border.all(0.5, ft.Colors.WHITE30),
                                border_radius=10,
                                expand=True,
                                alignment=ft.alignment.top_left)

    # Tableau des rendements
    table = ft.DataTable(
        expand=True,
        column_spacing=10,
        heading_row_height=25,
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
        data_row_min_height=35,
        data_row_max_height=35,
        divider_thickness=0.5,
        columns=[],
        rows=[],
    )

    cadre_tableau = ft.Container(
        content=ft.Row([table],
                       scroll=ft.ScrollMode.AUTO,
                       alignment=ft.MainAxisAlignment.CENTER),
        border=ft.border.all(0.5, couleur_titre_separateur),
        border_radius=10,
        padding=5,
        alignment=ft.alignment.center,
    )

    # --- Fonctions ---
    def update_selection_list():
        liste_selection.controls.clear()
        for i in indices_selectionnes:
            liste_selection.controls.append(ft.Row([ft.Text(i, size=12),
                                                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16,on_click=lambda e, i=i: retirer_indice(i))], 
                                                    spacing=0,)
                                )
        page.update()

    def ajouter_indice(indice):
        if indice and indice not in indices_selectionnes:
            indices_selectionnes.append(indice)
            update_selection_list()
            update_table()

    def retirer_indice(indice):
        if indice in indices_selectionnes:
            indices_selectionnes.remove(indice)
            update_selection_list()
            update_table()

    # Fonction : ajouter une période personnalisée
    def ajouter_periode(p):
        try:
            p = int(p)
            if p <= 0:
                return
        except (ValueError, TypeError):
            return
        if p not in periods_selectionnees:
            periods_selectionnees.append(p)
            update_periodes_list()
            update_table()
        input_periode.value = ""  # on vide le champ
        page.update()

    def retirer_periode(p):
        if p in periods_selectionnees:
            periods_selectionnees.remove(p)
            update_periodes_list()
            update_table()

    # Affichage dynamique des périodes sélectionnées
    def update_periodes_list():
        liste_periodes.controls.clear()
        for p in sorted(periods_selectionnees):
            liste_periodes.controls.append(
                ft.Row([ft.Text(f"{p}m", size=12),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, p=p: retirer_periode(p))]
                        , spacing=0))
            
        page.update()

    def update_table():
        table.columns.clear()
        table.rows.clear()

        # Colonnes dynamiques selon les périodes sélectionnées
        columns = [ft.DataColumn(ft.Text("Entreprises", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns

        for indice in indices_selectionnes:
            df = datas_stocks.get_prix_date(indice)
            if not df.empty:
                rendements = calculate_rendement(df, periods_selectionnees)
                cells = [ft.DataCell(ft.Text(indice, size=11))]
                for period in sorted(periods_selectionnees):
                    valeur = rendements.get(f'{period} mois', 0)
                    try:
                        valeur_float = float(valeur)
                        texte = f"{valeur_float:.1f}%"
                        couleur_texte = (
                            ft.Colors.GREEN if valeur_float > 0
                            else ft.Colors.RED if valeur_float < 0
                            else ft.Colors.BLACK
                        )
                    except (ValueError, TypeError):
                        texte = str(valeur)
                        couleur_texte = ft.Colors.BLACK
                    cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur_texte)))
                table.rows.append(ft.DataRow(cells=cells))
        page.update()

    # Initialisation
    update_selection_list()
    update_periodes_list()
    update_table()

    return [
        text_rendement,
        separation,
        dropdown_multi,
        cadre_text,
        cadre_periodes,
        cadre_tableau
    ]


################################## INFO ENTREPRISE  ################################

def create_composition_section(page):
    
     # Widget : titre dans container pour le padding
    text_composition = ft.Container(content=ft.Text("🗂 Informations entreprise",
                                                    color=couleur_titre_separateur,
                                                    weight=ft.FontWeight.BOLD,
                                                    size=21),
                                                    padding=ft.padding.only(top=35))

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur),
                              padding=ft.padding.only(bottom=15))



    # Widget : Dropdown (menu déroulant)
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez une entreprise", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        value=actif_default,
        options=[ft.dropdown.Option(indice) for indice in liste_actifs],
        width=300
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
        border=ft.border.all(0.5, couleur_titre_separateur),
        border_radius=10,
        padding=5,
    )


    # Fonction pour mettre à jour le tableau de composition
    def update_table_composition(e):
        selected_indice = dropdown_indice.value # Récupérer l'indice sélectionné
        df = datas_stocks.get_infos_stocks(selected_indice)
        table_composition.columns.clear()
        table_composition.rows.clear()
        for col in df.columns:
            table_composition.columns.append(ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11)))
        for _, row in df.iterrows():
            table_composition.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=10)) for v in row]))
        page.update()
    

    # Lier le dropdown à la fonction de mise à jour
    dropdown_indice.on_change = update_table_composition

    # Appel initial pour afficher la composition par défaut
    update_table_composition(actif_default)
    page.update()

    return [text_composition, separation, dropdown_indice, cadre_table_composition]


################################### FONCTION PRINCIPALE ################################

def stocks_page(page: ft.Page):
    page.clean()
    page.title = "Les entreprises"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

     # Création Loader général
    loader_global = ft.Container(content=ft.ProgressRing(color=ft.Colors.GREEN_200, width=60, height=60),
                                 alignment=ft.alignment.center,
                                 visible=True)
    page.add(loader_global)

    # Récupère tous les éléments
    graph_elements = create_graph_section(page)
    rendement_elements = create_rendement_section(page)
    infos_elements = create_composition_section(page)

    # Bouton retour en haut à droite
    bouton_retour_haut = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,  # flèche gauche
        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
        tooltip="Retour accueil",
        on_click=lambda e: page.go("/"))

    container_retour_haut = ft.Container(
        content=ft.Row([bouton_retour_haut], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.all(0),        # plus aucun padding
        height=30,)


    # Bouton Retour accueil
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/"))  # Redirection vers la page d'accueil


    container_bouton = ft.Container(
        content=bouton_retour,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20))  # Espacement avant et après


    # Suppresion du loader
    loader_global.visible = False


    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        container_retour_haut,  # Bouton en haut à droite
        *graph_elements,
        *rendement_elements, 
        *infos_elements,
        container_bouton  # Bouton en dernier
    )
