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
    
    # Widget : titre
    text_graphique = ft.Text("📈 Graphiques des indices", color=ft.Colors.AMBER_200, weight=ft.FontWeight.BOLD, size=21)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous 
    separation = ft.Container(
        content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200),
        padding=ft.padding.only(bottom=10)  # espace seulement en dessous
    )

    # Widget : Dropdown (menu déroulant)
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez un indice pour le graphique", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        value=indice_default,
        options=[ft.dropdown.Option(indice) for indice in liste_indices],
        width=300
)    

    # Widget : graphique PlotlyChart vide
    graphique = PlotlyChart(figure=go.Figure(), visible=False)
    

    def update_graph(e): # Met à jour le graphique quand on change l'indice
        
        selected_indice = dropdown_indice.value
        
        # Récupération des données
        df = datas_indices.get_prix_date(selected_indice)
        
        # Convertir les dates en string
        df['Date'] = df['Date'].astype(str)
        
        # Créer le graphique
        fig = go.Figure(go.Scatter(x=df["Date"], y=df["Close"], mode='lines', name=selected_indice, line=dict(color='#6DBE8C', width=2)))
        fig.update_layout(
            title=f"Évolution de {selected_indice}",
            title_font=dict(size=22, color='white', family='Arial Black'),
            plot_bgcolor='black',          # fond du graphique noir
            paper_bgcolor='black',         # fond global noir
            font=dict(color='white'),      # texte blanc
            xaxis_title="Date",
            yaxis_title="Prix de clôture",
            hovermode='x unified',         # affichage des infos sur toute la verticale
            dragmode='zoom',               # zoom avec la souris
            margin=dict(l=50, r=50, t=80, b=50),
            xaxis=dict(showgrid=False, zeroline=False, showline=False, linecolor='white',tickangle=-45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.25)', zeroline=False, showline=False, linecolor='white')
            )             # pas de lignes de grille / pas de ligne à y=0 / afficher l'axe y / couleur de l'axe y

        # Mise à jour du graphique
        #graphique.figure = fig 
        #page.update()

        # Mise à jour du graphique
        graphique.figure = fig

        # Rendre le graphique visible après la première mise à jour pour pas avoir chart blanc au départ
        graphique.visible = True
        
        # Met à jour la page pour refléter les changements
        page.update()

    # Lier "dropdown_indice" à la fonction "update_graph" grace à l'événement "on_change"  qui est un callback
    dropdown_indice.on_change = update_graph
    
    # Ajouter à la page
    page.add(
        text_graphique, 
        separation,
        dropdown_indice,
        graphique, 
    )
    
    # Charger le graphique initial
    update_graph(None)


################################## TABLEAU COMPARATIF RENDEMENTS ######################

    # Widget : titre dans container pour le padding
    text_rendement = ft.Container(
        content=ft.Text(
            "💯 Rendements des indices (%)",
            color=ft.Colors.AMBER_200,
            weight=ft.FontWeight.BOLD,
            size=21),
        padding=ft.padding.only(top=30)  # espace de 10 px au-dessus
        )


    # Widget : ligne de séparation dans un container pour avoir padding
    separation = ft.Container(
        content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200),
        padding=ft.padding.only(bottom=10)  # espace seulement en dessous
    )

    # Widget : Dropdown (menu déroulant)
    dropdown_multi = ft.Dropdown(
        label="Sélectionnez les indices à comparer",
        hint_text="Choisissez un ou plusieurs indices",
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
        width=300,
        options=[ft.dropdown.Option(i) for i in liste_indices], # éléments de la liste
        on_change=lambda e: ajouter_indice(e.control.value),
        #multiple=True,  # Permet la sélection multiple
        value=indice_default  # Valeur par défaut (liste des indices sélectionnés)
        )

    
    # Widget : texte "Indices sélectionnés"
    text_liste_indice_selectionnes = ft.Text("Indices sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))

    # Widget : liste des indices sélectionnés en ligne
    liste_selection = ft.Row()

    # Widget : cadre qui prend texte + liste des indices dansun contenair
    cadre_text_liste_indice_selectionnes = ft.Container(
    content=ft.Column([text_liste_indice_selectionnes, liste_selection]),
    padding=5,  # espace autour du texte
    border=ft.border.all(1, ft.Colors.WHITE30),  # bordure 1px grise
    border_radius=10,  # coins arrondis
    alignment=ft.alignment.center_left  # contenu aligné à gauche
    )

    # Widget : tableau avec personnalisation
    table = ft.DataTable(
        column_spacing=10, # Espace entre les colonnes
        #vertical_lines=ft.BorderSide(1, ft.Colors.GREY_400),
        heading_row_height=25,  # Hauteur de la ligne d'en-tête
        data_row_min_height=35,  # Hauteur minimale des lignes de données
        data_row_max_height=35,  # Hauteur maximale des lignes de données
        divider_thickness=0.5, # Epaisseur séparateur lignes
        columns=[
            ft.DataColumn(ft.Text("Indice", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("6m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("12m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("24m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("60m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("120m", weight=ft.FontWeight.BOLD, size=12)),
            ft.DataColumn(ft.Text("180m", weight=ft.FontWeight.BOLD, size=12))
        ],
        rows=[]
        )

    # Widget : cadres tableau (dans un contenaur)
    cadre_tableau = cadre_tableau = ft.Container(
        content=ft.Row([table], scroll=ft.ScrollMode.AUTO),
        border=ft.border.all(1, ft.Colors.AMBER_200),
        border_radius=10,
        padding=5,
        width=350
        )

    # Liste des indices sélectionnés par défaut "SP500"
    indices_selectionnes = [indice_default] 

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
        for i in indices_selectionnes:
            liste_selection.controls.append(
                ft.Row([
                    ft.Text(i, size=12),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,  # ← I majuscule
                        icon_size=16,
                        on_click=lambda e, i=i : retirer_indice(i) # Utilisation de i=i pour capturer la valeur correcte au moment de l'itération
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
                            ft.Text(texte, size=10, color=couleur_texte)  # color au lieu de bgcolor
                        )
                    )
                
                table.rows.append(ft.DataRow(cells=cells))
        
        page.update()
    
    # Ajout des widgets à la page
    page.add(
        text_rendement,
        separation,
        dropdown_multi,
        cadre_text_liste_indice_selectionnes,
        cadre_tableau
        )
    
    page.update()
    # Initialiser
    update_selection_list()
    update_table()


################################## COMPOSITION INDICES ############################

    # Widget : titre dans container pour le padding
    text_composition = ft.Container(
        content=ft.Text(
            "🗂 Composition des indices",
            color=ft.Colors.AMBER_200,
            weight=ft.FontWeight.BOLD,
            size=21),
        padding=ft.padding.only(top=30)
    )

    # Widget : ligne de séparation
    separation = ft.Container(
        content=ft.Divider(thickness=2, color=ft.Colors.AMBER_200),
        padding=ft.padding.only(bottom=10)
    )

    # Widget : Dropdown
    dropdown_composition = ft.Dropdown(  # ← Nom différent pour éviter confusion
        label="Sélectionnez la composition de l'indice",
        hint_text="Choisissez un indice",
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
        width=300,
        options=[ft.dropdown.Option(i) for i in liste_indices],
        on_change=lambda e: update_table_composition(e.control.value),  # ← Appelle update_table_composition
        value=indice_default
    )

    # Tableau vide pour la composition
    table_composition = ft.DataTable(
        column_spacing=10,
        heading_row_height=30,
        data_row_min_height=25,
        divider_thickness=0.5,
        columns=[ft.DataColumn(ft.Text("Chargement...", size=11))],  # ← Au moins 1 colonne
        rows=[]
    )

    # Conteneur avec scroll
    cadre_table_composition = ft.Container(
        content=ft.Column(
            [ft.Row([table_composition], scroll=ft.ScrollMode.AUTO)],  # Row pour scroll horizontal
            scroll=ft.ScrollMode.AUTO  # Column pour scroll vertical
        ),
        border=ft.border.all(1, ft.Colors.AMBER_200),
        border_radius=10,
        padding=5,
        height=300,  # Hauteur fixe nécessaire pour activer le scroll vertical
        width=350
    )

    # Texte d'état
    texte_resultat = ft.Text("", size=13, color=ft.Colors.WHITE)

    # Fonction de mise à jour
    def update_table_composition(indice):
        df = datas_indices.get_composition_indice(indice)
        
        table_composition.columns.clear()
        table_composition.rows.clear()
        
        if df is None or df.empty:
            texte_resultat.value = f"⚠️ Pas de données disponibles pour l'indice {indice}."
            # Remettre une colonne vide pour éviter l'erreur
            table_composition.columns.append(
                ft.DataColumn(ft.Text("Aucune donnée", size=11))
            )
        else:
            texte_resultat.value = f"📊 Composition de l'indice {indice} :"
            
            # Colonnes
            for col in df.columns:
                table_composition.columns.append(
                    ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11))
                )
            
            # Lignes
            for _, row in df.iterrows():
                cells = [ft.DataCell(ft.Text(str(val), size=10)) for val in row]
                table_composition.rows.append(ft.DataRow(cells=cells))
        
        page.update()

    # Ajouter à la page
    page.add(
        text_composition,
        separation,
        dropdown_composition,  # ← Utilise le bon nom
        texte_resultat,
        cadre_table_composition
    )

    # Initialiser
    update_table_composition(indice_default)