# on_click = handler d'événement :  une propriété qui attend une fonction (callable).
# Événement = ce qu'il se passe (ici le clic).
# Handler = la fonction qui gère cet événement (ex: go_home).
# Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
# => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.

import flet as ft
from flet import LineChart, LineChartData, LineChartDataPoint
import io
import base64
import tempfile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from src.models.control_datas.connexion_db_datas import *
from src.components.components_views import *

# Connexion DB
datas_actifs = FinanceDatabaseCryptos(db_path="data.db")
liste_actifs = datas_actifs.get_list_cryptos()
actif_default = "Bitcoin"
couleur_titre_separateur = "#F7931A"
couleur_bouton_fleche = "#FBBF63"

################################## GRAPHIQUE avec fl_chart
def create_graph_section(page):
    page.scroll = "auto"
    
    # Titre
    titre = titre_separateur(
        text="📈 Graphiques crypto",
        padding_text_top=0,
        couleur_titre_separateur=couleur_titre_separateur
    )
    
    # Dropdown
    dropdown_actif = dropdown(
        "Sélectionnez une crypto", 
        actif_default,
        liste_actifs, 
        handler=None
    )
    
    # Container pour le graphique
    chart_container = ft.Container(
        content=ft.Text("Chargement...", text_align=ft.TextAlign.CENTER),
        height=300,
        border=ft.border.all(2, color=ft.Colors.BLACK12),
        border_radius=10,
        padding=5,
    )
    
    # Loader
    loader = loader_page(couleur_titre_separateur)
    
    def update_graph(e):
        loader.visible = True
        page.update()
        
        try:
            # Récupérer les données
            selected_crypto = dropdown_actif.value
            df = datas_actifs.get_prix_date(selected_crypto)
            
            if df.empty:
                chart_container.content = ft.Text("Aucune donnée disponible", color=ft.Colors.RED)
                loader.visible = False
                page.update()
                return
            
            df = df.reset_index(drop=True)
            data_points = [LineChartDataPoint(i, float(row['Close'])) for i, row in df.iterrows()]
            
            prices = [float(row['Close']) for _, row in df.iterrows()]
            min_price = min(prices) * 0.95
            max_price = max(prices) * 1.05
            
            # Création du graphique sans labels pour maximiser la largeur
            chart = LineChart(
                data_series=[LineChartData(
                    data_points=data_points,
                    stroke_width=1,
                    color=couleur_titre_separateur,
                    curved=True,
                    stroke_cap_round=True,
                )],
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                horizontal_grid_lines=ft.ChartGridLines(
                    interval=(max_price - min_price) / 8,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    width=1
                ),
                vertical_grid_lines=ft.ChartGridLines(
                    interval=max(1, len(df) // 8),
                    color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    width=1
                ),
                left_axis=ft.ChartAxis(labels=None, title=None, visible=False,),
                bottom_axis=ft.ChartAxis(labels=None, title=None, visible=False),
                tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                min_y=min_price,
                max_y=max_price,
                min_x=0,
                max_x=len(df) - 1,
                expand=True,
            )
            
            # Container qui prend toute la largeur
            chart_container.content = ft.Column([
                ft.Text(f"Évolution de {selected_crypto}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Container(content=chart, height=350, expand=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
        except Exception as ex:
            chart_container.content = ft.Text(f"Erreur: {str(ex)}", color=ft.Colors.RED)
        
        finally:
            loader.visible = False
            page.update()

    
    # Lier le dropdown
    dropdown_actif.on_change = update_graph
    
    # Affichage initial
    update_graph(None)
    
    # Regroupement
    contenu = contenu_widget(titre, [dropdown_actif, loader, chart_container])
    return [contenu]


################################## TABLEAU COMPARATIF RENDEMENTS ################################

def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]  # affichées au début

    # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text="💯 Rendements cryptos (%)",
                             padding_text_top=35,
                             couleur_titre_separateur=couleur_titre_separateur)

    # Fonction : Dropdown (menu déroulant)
    dropdown_actif = dropdown("Sélectionnez les cryptos à comparer", actif_default,
                              liste_actifs, handler=lambda e: ajouter_indice(e.control.value))

    # Indice en liste
    indices_selectionnes = [actif_default]
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_text = ft.Container(content=ft.Column([ft.Text("Cryptos sélectionnées:", 
                                                         size=11, 
                                                         style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
                                                liste_selection],),
                                        padding=5,
                                        border=ft.border.all(2, ft.Colors.WHITE30),
                                        border_radius=10,)

    # Text pour période à ajouter
    text_periode = ft.Text("Ajouter une période (en mois)", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),)

    # Fonction : input période à ajouter
    input_periode = periode_input(fonc_ajouter_periode=lambda e: ajouter_periode(e.control.value))

    # Bouton "+" pour ajouter la période
    bouton_ajouter_periode = ft.IconButton(icon=ft.Icons.ADD,tooltip="Ajouter la période", on_click=lambda e: ajouter_periode(input_periode.value))

    # Ligne pour l'input et le bouton "+"
    ligne_ajout_periode = ft.Row([input_periode, bouton_ajouter_periode], alignment=ft.MainAxisAlignment.START, spacing=10)

    # Conteneur pour les périodes sélectionnées
    liste_periodes = ft.Row(scroll=ft.ScrollMode.AUTO)

    # Cadre complet regroupant tout
    cadre_periodes = ft.Container(content=ft.Column([text_periode,
                                                        ligne_ajout_periode,
                                                        ft.Text("Périodes sélectionnées (en mois) :", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
                                                        liste_periodes,],  # ici on l’ajoute DANS le cadre
                                                    spacing=10,
                                                    alignment=ft.MainAxisAlignment.START),
                                            padding=10,
                                            border=ft.border.all(2, ft.Colors.WHITE30),
                                            border_radius=10,
                                            alignment=ft.alignment.top_left)



    # Tableau des rendements
    table = ft.DataTable(
        #expand=True,
        column_spacing=10,#espacement des colonnes
        heading_row_height=30,#hauteur de la ligne de titre
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),#couleur de fond de la ligne de titre
        data_row_min_height=35,#hauteur minimale des lignes de données
        data_row_max_height=35,#hauteur maximale des lignes de données
        divider_thickness=0.5,#épaisseur des diviseurs entre les lignes
        columns=[],#colonnes du tableau
        rows=[],) #lignes du tableau

    cadre_tableau = ft.Container(content=ft.Row([table], scroll=ft.ScrollMode.AUTO,),
                                border=ft.border.all(2, couleur_titre_separateur),
                                border_radius=10,
                                padding=5,)
    



    # --- Fonctions ---
    def update_selection_list():
        liste_selection.controls.clear()
        for i in indices_selectionnes:
            liste_selection.controls.append(ft.Row([ft.Text(i, size=12),
                                                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, i=i: retirer_indice(i))],
                                                   spacing=0,))
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
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, p=p: retirer_periode(p))], spacing=0))

        page.update()

    def update_table():
        table.columns.clear()
        table.rows.clear()

        # Colonnes dynamiques selon les périodes sélectionnées
        columns = [ft.DataColumn(
            ft.Text("Indice", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(
                ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns

        for indice in indices_selectionnes:
            df = datas_actifs.get_prix_date(indice)
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
                    cells.append(ft.DataCell(
                        ft.Text(texte, size=10, color=couleur_texte)))
                table.rows.append(ft.DataRow(cells=cells))
        page.update()

    # Initialisation
    update_selection_list()
    update_periodes_list()
    update_table()

    # Regroupement widger section
    contenu = contenu_widget(titre, [dropdown_actif, cadre_text, cadre_periodes, cadre_tableau])

    return [contenu]

################################## INFO CRYPTOS  ################################
def create_composition_section(page):

    # Fonction : titre + séparateur dans conteneur
    titre = titre_separateur("🗂 Informations crypto",
                             couleur_titre_separateur, padding_text_top=35)

    # Widget : Dropdown (menu déroulant)
    dropdown_indice = dropdown(
        "Sélectionnez une crypto", actif_default, liste_actifs, handler=None)

    # Widget : tableau de la composition
    table_composition = ft.DataTable(
        #expand=True,
        column_spacing=10,#espacement des colonnes
        heading_row_height=30,#hauteur de la ligne de titre
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),#couleur de fond de la ligne de titre
        data_row_min_height=35,#hauteur minimale des lignes de données
        data_row_max_height=35,#hauteur maximale des lignes de données
        divider_thickness=0.5,#épaisseur des diviseurs entre les lignes
        columns=[],#colonnes du tableau
        rows=[],) #lignes du tableau

    # Cadre autour du tableau
    cadre_table_composition = ft.Container(content=ft.Row([table_composition], scroll=ft.ScrollMode.AUTO,),
                            border=ft.border.all(2, couleur_titre_separateur),
                            border_radius=10,
                            padding=5,)

    # Fonction pour mettre à jour le tableau de composition
    def update_table_composition(e):
        selected_indice = dropdown_indice.value  # Récupérer l'indice sélectionné
        df = datas_actifs.get_infos_cryptos(selected_indice)
        table_composition.columns.clear()
        table_composition.rows.clear()
        for col in df.columns:
            table_composition.columns.append(ft.DataColumn(
                ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11)))
        for _, row in df.iterrows():
            table_composition.rows.append(ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v), size=10)) for v in row]))
        page.update()

    # Lier le dropdown à la fonction de mise à jour
    dropdown_indice.on_change = update_table_composition

    # Appel initial pour afficher la composition par défaut
    update_table_composition(actif_default)
    page.update()

    # Regroupement widger section
    contenu = contenu_widget(titre, [dropdown_indice, cadre_table_composition])

    return [contenu]


################################### FONCTION PRINCIPALE ################################
def cryptos_page(page: ft.Page):
    page.clean()
    page.title = "Les cryptomonais"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Fonction Loader général
    loader_global = loader_globale(couleur_titre_separateur)
    page.add(loader_global)

    # Récupère tous les éléments
    graph_elements = create_graph_section(page)
    rendement_elements = create_rendement_section(page)
    infos_elements = create_composition_section(page)

    # Fonction bouton retour haut
    bouton_retour_haut = bout_ret_haut(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    # Bouton retour acceuol en bas
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    # Suppresion du loader
    loader_global.visible = False

    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        bouton_retour_haut,  # Bouton en haut à droite
        *graph_elements,
        *rendement_elements,
        *infos_elements,
        bouton_acceuil  # Bouton en dernier
    )
