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
from src.components.components_views import *


# Connexion DB et récupération des données
datas_actifs = FinanceDatabaseCryptos(db_path="data.db")
liste_actifs = datas_actifs.get_list_cryptos()
infos_actifs = datas_actifs.get_infos_cryptos()
actif_default = "Bitcoin"

couleur_titre_separateur = "#F7931A"
couleur_bouton_fleche = "#FBBF63"

################################## GRAPHIQUE #################################################


def create_graph_section(page):
    page.scroll = "auto"

    # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text="📈 Graphiques de la crypto",padding_text_top = 0, couleur_titre_separateur=couleur_titre_separateur)

    # Fonction : Dropdown (menu déroulant)
    dropdown_actif = dropdown("Sélectionnez une crypto", actif_default, liste_actifs, handler=None)

    # Widget : graphique PlotlyChart vide
    graphique = PlotlyChart(figure=go.Figure(), visible=False)

    # Fonction : loader (anneau de chargement)
    loader = loader_page(couleur_titre_separateur)

    def update_graph(e):  # Met à jour le graphique quand on change l'indice
        loader.visible = True
        graphique.visible = False
        page.update()

        # Récupérer l'indice sélectionné
        selected_indice = dropdown_actif.value

        # Récupérer les données de l'indice sélectionné
        df = datas_actifs.get_prix_date(selected_indice)

        # Convertir les dates en string
        df['Date'] = df['Date'].astype(str)

        # Créer le graphique avec Plotly
        fig = go.Figure(go.Scatter(x=df["Date"], y=df["Close"], mode='lines',
                        name=selected_indice, line=dict(color='#6DBE8C', width=2)))

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
            xaxis=dict(showgrid=False, zeroline=False,
                       showline=False, tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.25)',
                       zeroline=False, showline=False)
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
    dropdown_actif.on_change = update_graph

    # Appel initial pour afficher le graphique par défaut
    update_graph(None)

    # Regroupement widger section
    contenu = contenu_widget(titre, [dropdown_actif, loader, graphique])

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

    cadre_text = ft.Container(
        content=ft.Column([
            ft.Text("Cryptos sélectionnées:", size=11, style=ft.TextStyle(
                decoration=ft.TextDecoration.UNDERLINE)),
            liste_selection
        ],
            horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=5,
        border=ft.border.all(2, ft.Colors.WHITE30),
        border_radius=10,
        expand=True,
        alignment=ft.alignment.top_left
    )

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

    # Ossature tableau rendement + cadre
    table, cadre_tableau = tableau_cadre(expands = False, couleur = couleur_titre_separateur, heights = None)


    # --- Fonctions ---
    def update_selection_list():
        liste_selection.controls.clear()
        for i in indices_selectionnes:
            liste_selection.controls.append(ft.Row([ft.Text(i, size=12),
                                                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, i=i: retirer_indice(i))],
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
    contenu = contenu_widget(
        titre, [dropdown_actif, cadre_text, cadre_periodes, cadre_tableau])

    return [contenu]

################################## INFO CRYPTOS  ################################
def create_composition_section(page):

    # Fonction : titre + séparateur dans conteneur
    titre = titre_separateur("🗂 Informations crypto",
                             couleur_titre_separateur, padding_text_top=35)

    # Widget : Dropdown (menu déroulant)
    dropdown_indice = dropdown(
        "Sélectionnez une crypto", actif_default, liste_actifs, handler=None)

    # Tableau composition + cadre
    table_composition, cadre_table_composition = tableau_cadre(expands = False, couleur = couleur_titre_separateur, heights = None)

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
