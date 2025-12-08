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


# Connexion DB indices
datas_indices = FinanceDatabaseIndice(db_path="data.db")
liste_indices = datas_indices.get_list_indices()
indice_default = "S&P 500"

# Connexion DB pour stocks
datas_stocks = FinanceDatabaseStocks(db_path="data.db")
liste_stocks = datas_stocks.get_list_stocks()
stock_default = "Apple Inc."

# Connexion DB cryptos
datas_cryptos = FinanceDatabaseCryptos(db_path="data.db")
liste_cryptos = datas_cryptos.get_list_cryptos()
crypto_default = "Bitcoin"

# Liste combinée de tous les actifs
liste_actifs = sorted(set(liste_stocks + liste_indices + liste_cryptos))

# Couleurs
couleur_titre_separateur = ft.Colors.PURPLE_300
couleur_bouton_fleche = ft.Colors.PURPLE_600


################################## TABLEAU COMPARATIF RENDEMENTS ################################

def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]  # affichées au début

    # Fonction pour titre et séparateur
    titre = titre_separateur(text="💯 Rendements actifs (%)",padding_text_top = 0, couleur_titre_separateur=couleur_titre_separateur)

    # ------- Sélection des actifs -------
    # Dropdown indice : (menu déroulant)
    dropdown_indices = dropdown("Sélectionnez un indice", indice_default, liste_indices, handler=lambda e: ajouter_indice(e.control.value))
    
    # Dropdown stocks :  (menu déroulant)
    dropdown_stocks = dropdown("Sélectionnez une entreprise", stock_default, liste_stocks, handler=lambda e: ajouter_indice(e.control.value))
    
    # Dropdown cryptos :  (menu déroulant)
    dropdown_cryptos = dropdown("Sélectionnez une crypto", crypto_default, liste_cryptos, handler=lambda e: ajouter_indice(e.control.value))

    # Conteneur pour les indices sélectionnés
    indices_selectionnes = [indice_default, stock_default, crypto_default]  # affichés au début
    
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_text = ft.Container(content=ft.Column([ft.Text("Actifs sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
                                                 liste_selection],
                                                horizontal_alignment=ft.CrossAxisAlignment.START),
                              padding=5,
                              border=ft.border.all(2, ft.Colors.WHITE30),
                              border_radius=10,
                              expand=True,
                              alignment=ft.alignment.top_left)

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

    # Cadre complet regroupant tout pour les indices selectionnés
    cadre_periodes = ft.Container(content=ft.Column([text_periode,
                                                     ligne_ajout_periode,
                                                     ft.Text("Périodes sélectionnées (en mois) :", size=11, style=ft.TextStyle(
                                                         decoration=ft.TextDecoration.UNDERLINE)),
                                                    liste_periodes,],
                                                    spacing=10,
                                                    alignment=ft.MainAxisAlignment.START),
                                  padding=10,
                                  border=ft.border.all(2, ft.Colors.WHITE30),
                                  border_radius=10,
                                  expand=True,
                                  alignment=ft.alignment.top_left)


    # Ossature tableau rendement + cadre
    table, cadre_tableau = tableau_cadre(expands = False, couleur = couleur_titre_separateur, heights = None)


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
            ft.Text("Actifs", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(
                ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns

        for actif in indices_selectionnes:
            # On essaie de trouver l’actif dans la bonne base
            if actif in liste_stocks:
                df = datas_stocks.get_prix_date(actif)
            elif actif in liste_indices:
                df = datas_indices.get_prix_date(actif)
            elif actif in liste_cryptos:
                df = datas_cryptos.get_prix_date(actif)
            else:
                continue  # inconnu, on passe au suivant

            # Si on a bien des données, on calcule les rendements
            if not df.empty:
                rendements = calculate_rendement(df, periods_selectionnees)
                cells = [ft.DataCell(ft.Text(actif, size=11))]
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

    contenu = contenu_widget(titre, [dropdown_indices, dropdown_stocks, dropdown_cryptos, cadre_text, cadre_periodes, cadre_tableau])

    return [contenu]


################################### FONCTION PRINCIPALE ################################

def actifs_page(page: ft.Page):
    page.clean()
    page.title = "Tous actifs"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Création Loader général
    loader_global = loader_globale(couleur_titre_separateur)
    # Mise en place du loader_global
    page.add(loader_global)

    # Récupère tous les éléments
    rendement_elements = create_rendement_section(page)

    # Bouton retour en haut à droite
    bouton_retour_haut = bout_ret_haut(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    # Bouton Retour accueil
    bouton_retour = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    # Suppresion du loader_global
    loader_global.visible = False

    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        bouton_retour_haut,  # Bouton en haut à droite
        *rendement_elements,  # Tous les éléments de la section rendements
        bouton_retour  # Bouton en dernier
    )
