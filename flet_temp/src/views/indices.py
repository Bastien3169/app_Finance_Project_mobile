    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.

import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
import io
import base64
import matplotlib.pyplot as plt
from src.models.control_datas.connexion_db_datas import *
from src.components.components_views import *


# Connexion DB et récupération des données
datas_actifs = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_actifs.get_list_indices()
infos_actifs = datas_actifs.get_infos_indices()
actif_default = "S&P 500"

couleur_titre_separateur = "#00B388"
couleur_bouton_fleche = "#21C4A0"

################################## GRAPHIQUE #################################################
def create_graph_section(page):
    page.scroll = "auto"

    # Titre + séparateur
    titre = titre_separateur(
        text="📈 Graphique de l'indice",
        padding_text_top=0,
        couleur_titre_separateur="#00B388"
    )

    # Dropdown pour sélectionner l'indice
    dropdown_actif = dropdown(
        "Sélectionnez un indice",
        actif_default,
        liste_actifs,
        handler=None
    )

    # Widget Image (vide au départ)
    graphique = ft.Image(
        src_base64="",  # <- utilisation de src_base64 ici
        visible=True,
        fit=ft.ImageFit.CONTAIN,
        width=700,
        height=400
    )

    # Loader
    loader = loader_page("#00B388")
    loader.visible = False

    def update_graph(e):
        loader.visible = True
        page.update()

        selected_indice = dropdown_actif.value
        df = datas_actifs.get_prix_date(selected_indice)
        if df.empty:
            loader.visible = False
            page.update()
            return

        df['Date'] = df['Date'].astype(str)

        # --- Création du graphique Matplotlib ---
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df["Date"], df["Close"], color="#6DBE8C", linewidth=2)
        ax.set_title(f"Évolution de {selected_indice}", fontsize=16, color="white")
        ax.set_facecolor("black")
        fig.patch.set_facecolor("black")
        ax.tick_params(colors="white", rotation=45)
        ax.grid(color="gray", alpha=0.25)
        ax.set_xlabel("Date", color="white")
        ax.set_ylabel("Prix de clôture", color="white")

        # Conversion en image base64 pour Flet
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        graphique.src_base64 = img_b64  # <- changement clé

        loader.visible = False
        page.update()

    # Lier le dropdown
    dropdown_actif.on_change = update_graph

    # Affichage initial
    update_graph(None)

    contenu = contenu_widget(titre, [dropdown_actif, loader, graphique])
    return [contenu]

################################## TABLEAU COMPARATIF RENDEMENTS ################################

def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]  # affichées au début

 # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text = "💯 Rendements des indices (%)", 
                            padding_text_top = 35, 
                            couleur_titre_separateur = couleur_titre_separateur)


    # Fonction : Dropdown (menu déroulant)
    dropdown_actif = dropdown ("Sélectionnez les indices à comparer", actif_default, liste_actifs, handler= lambda e: ajouter_indice(e.control.value))
    
    # Mettre les indices en liste
    indices_selectionnes = [actif_default]

    # Text pour liste des indices sélectionnés
    text_liste_indices = ft.Text("Indices sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))

    # Conteneur pour la liste des indices sélectionnés
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    # Cadre autour de la liste des indices sélectionnés
    cadre_text = ft.Container(content=ft.Column([text_liste_indices, liste_selection],horizontal_alignment=ft.CrossAxisAlignment.START),
                              padding=5,
                              border=ft.border.all(2, ft.Colors.WHITE30),
                              border_radius=10,
                              expand=True,
                              alignment=ft.alignment.top_left)


    # Text pour période à ajouter
    text_periode = ft.Text("Ajouter une période (en mois)", size=11,style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),)

    # Fonction : input période à ajouter 
    input_periode = periode_input(fonc_ajouter_periode=lambda e: ajouter_periode(e.control.value))
    
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
                                border=ft.border.all(2, ft.Colors.WHITE30),
                                border_radius=10,
                                expand=True,
                                alignment=ft.alignment.top_left)

    # Ossature tableau rendement + cadre
    table, cadre_tableau = tableau_cadre(expands = False, couleur = couleur_titre_separateur, heights = None)

    
    # Fonction : mise à jour de la liste des indices sélectionnés
    def update_selection_list():
        liste_selection.controls.clear()
        for i in indices_selectionnes:
            liste_selection.controls.append(ft.Row([ft.Text(i, size=12),
                                                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16,on_click=lambda e, i=i: retirer_indice(i))], 
                                                    spacing=0,))
        page.update()


    # Fonction : ajouter un indice
    def ajouter_indice(indice):
        if indice and indice not in indices_selectionnes:
            indices_selectionnes.append(indice)
            update_selection_list()
            update_table()

    # Fonction : retirer un indice
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

    # Fonction : retirer une période
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

    # Calcul des rendements
    def update_table():
        table.columns.clear()
        table.rows.clear()

        # Colonnes dynamiques selon les périodes sélectionnées
        columns = [ft.DataColumn(ft.Text("Indice", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
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
                    cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur_texte)))
                table.rows.append(ft.DataRow(cells=cells))
        page.update()


    # Initialisation
    update_selection_list()
    update_periodes_list()
    update_table()


    contenu = contenu_widget(titre, [dropdown_actif, cadre_text, cadre_periodes, cadre_tableau])
    
    return [contenu]

################################## COMPOSITION INDICES  ################################

def create_composition_section(page):
    
     # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text = "🗂 Composition de l'indice", 
                            padding_text_top = 35,
                            couleur_titre_separateur = couleur_titre_separateur)


    # Fonction : Dropdown (menu déroulant)
    dropdown_actif = dropdown ("Sélectionnez la composition de l'indice", actif_default, liste_actifs, handler= None)

    # Tableau composition + cadre
    table_composition, cadre_table_composition = tableau_cadre(expands = False, couleur = couleur_titre_separateur, heights = 300)

    # Fonction pour mettre à jour le tableau de composition
    def update_table_composition(indice):
        df = datas_actifs.get_composition_indice(indice)
        table_composition.columns.clear()
        table_composition.rows.clear()
        for col in df.columns:
            table_composition.columns.append(ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11)))
        for _, row in df.iterrows():
            table_composition.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=10)) for v in row]))
        page.update()

    # Lier "dropdown_composition" à la fonction "update_table_composition" grace à l'événement "on_change"  qui est un callback
    dropdown_actif.on_change = lambda e: update_table_composition(e.control.value)
    
    # Appel initial pour afficher la composition par défaut
    update_table_composition(actif_default)

    contenu = contenu_widget(titre, [dropdown_actif, cadre_table_composition])
    
    return [contenu]


################################### FONCTION PRINCIPALE ################################

def indices_page(page: ft.Page):
    page.clean()
    page.title = "Les indices"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Fonction Loader général
    loader_global = loader_globale(couleur_titre_separateur)
    page.add(loader_global)

    # Récupère tous les éléments
    graph_elements = create_graph_section(page)
    rendement_elements = create_rendement_section(page)
    composition_elements = create_composition_section(page)

    # Fonction bouton retour haut
    bouton_retour_haut=bout_ret_haut(couleur_bouton_fleche, handler = lambda e: page.go("/"))

    # Bouton retour acceuol en bas
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler = lambda e: page.go("/"))

    # Suppression du loader
    loader_global.visible = False

    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        bouton_retour_haut,  # Bouton en haut à droite
        *graph_elements,
        *rendement_elements, 
        *composition_elements,
        bouton_acceuil)  # Bouton en dernier
    
