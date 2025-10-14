import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *
from src.controllers.LP_VS_DCA import *
# Auth désactivé pour éviter problème cookies
# from src.models.users_db.models_db_users_test import AuthManager, AdminManager

# -------------------- Connexion DB --------------------
datas_indices = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_indices.get_list_indices()
actif_default = "S&P 500"

couleur_titre_separateur = ft.Colors.RED_200
couleur_bouton_fleche = ft.Colors.RED_700
titre_size = 20

################################## INPUT #################################################
def simulation_dca_vs_ls(page: ft.Page):
    page.title = "🏛️ Simulation DCA vs Lump Sum"
    page.scroll = "adaptive"

    # Widget : titre
    text_graphique = ft.Text("📈 Graphiques des indices", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=titre_size)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur),padding=ft.padding.only(bottom=15))

     # Widget : Dropdown (menu déroulant)
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez un indice pour le graphique", style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
        value=actif_default,
        options=[ft.dropdown.Option(indice) for indice in liste_actifs],
        border_radius=8,
        border_color=ft.Colors.WHITE30,
        expand=True
    )

    input_montant = ft.TextField(
        label="💰 Montant à investir (€)",
        value="100000",
        keyboard_type=ft.KeyboardType.NUMBER,
        border=ft.InputBorder.OUTLINE, # Bordure native
        border_radius=8, 
        border_color=ft.Colors.WHITE30,  
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
    )

    input_durees = ft.TextField(
        label="⏳ Durées d'investissement (en années)",
        value="5,10,15,20,25",
        hint_text="Ex: 5,10,15,20,25",
        border=ft.InputBorder.OUTLINE,
        border_radius=8,
        border_color=ft.Colors.WHITE30,
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
        
    )

    input_mois_dca = ft.TextField(
        label="📆 Mois de DCA",
        value="6,12,24",
        hint_text="Ex: 6,12,24",
        border=ft.InputBorder.OUTLINE,
        border_radius=8,
        border_color=ft.Colors.WHITE30,
        label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
    )

    # On crér un zone dynamique (un contenair ft.Columns) dans la page pour conreoler que cette zone et pas refresh la page à chaque fois
    output_zone = ft.Column()


################################## SIMULATION #################################################

    # Action : lancer la simulation
    def lancer_simulation(e):
        output_zone.controls.clear()

        ticker = dropdown_indice.value
        somme_investie = float(input_montant.value)
        durees = [int(x.strip()) for x in input_durees.value.split(",") if x.strip().isdigit()]
        mois_dca_list = [int(x.strip()) for x in input_mois_dca.value.split(",") if x.strip().isdigit()]

        # Mise en place di loader
        output_zone.controls.append(ft.ProgressRing(color=couleur_titre_separateur, visible=True, width=50, height=50))
        
        page.update()

        # Calculs
        df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
        df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)


         # suppression le loader avant d'ajouter les résultats
        output_zone.controls.clear()


#======================================================== GRAPHIQUE 1 ========================================================#

        # Graphique 1 : texte
        graphe1_text = (ft.Text(
            "📈 Les montants finaux obtenus en fonction de la durée du placement",
            size=18, weight="bold"
        ))

        graphe1_text = ft.Container(
            content=ft.Text("📈 Gains par durée",
                            color=couleur_titre_separateur,
                            weight=ft.FontWeight.BOLD,
                            size=titre_size),
            padding=ft.padding.only(top=35),
            expand=True,
            )

        # --- Séparateur ---
        separation = ft.Container(
            content=ft.Divider(thickness=2, color=couleur_titre_separateur),
            padding=ft.padding.only(bottom=15)
        )
        # Graphique 1 : graphique barre
        fig1 = graphe_barre(df_resultats)
        graphe1_graphe = (PlotlyChart(fig1, expand=True))




#======================================================== GRAPHIQUE 2 ========================================================#

        # Graphique 2 : texte
        graphe2_text = ft.Container(
            content=ft.Text("📈 Évolution de l'actif",
                            color=couleur_titre_separateur,
                            weight=ft.FontWeight.BOLD,
                            size=titre_size),
            padding=ft.padding.only(top=35),
            expand=True,
            )
        
        # Graphique 2 : évolution dans le temps
        fig2 = graphe_line(df, somme_investie)
        graphe2_graphe = (PlotlyChart(fig2, expand=True))




#======================================================== TABLEAU 1 ========================================================#
        # Titre partie tableau
        tableau_text = ft.Container(
            content=ft.Text("📈 Résultat sur tableau",
                            color=couleur_titre_separateur,
                            weight=ft.FontWeight.BOLD,
                            size=titre_size),
            padding=ft.padding.only(top=35),
            expand=True,
            )
        

       # Titre du tableau 1 : montants finaux
        titre_tableau1 = ft.Text(
            "Montants finaux par durée",
            weight=ft.FontWeight.BOLD,
            size=18,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
        )

        # Conteneur du titre tableau 1 pour mettre du padding
        titre_tableau1_contenair = ft.Container(content=titre_tableau1,
                                                alignment=ft.alignment.center,
                                                )

        # Tableau 1 stylé (même style que tableau2)
        tableau1 = ft.DataTable(
            column_spacing=10,
            heading_row_height=30,
            heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
            data_row_min_height=25,
            divider_thickness=0.5,
            columns=[ft.DataColumn(ft.Text(c, size=11)) for c in df_resultats.columns],
            rows=[
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(v), size=11)) for v in row]
                )
                for row in df_resultats.tail(10).values.tolist()
            ],
        )

        # Cadre du tableau 1 avec scroll automatique (même rendu que le 2)
        cadre_tableau1 = ft.Container(
            content=ft.Column(
                [ft.Row([tableau1], scroll=ft.ScrollMode.AUTO)],
                scroll=ft.ScrollMode.AUTO,
            ),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,  # hauteur fixe pour activer le scroll
        )



#======================================================== TABLEAU 2 ========================================================#        
        # Titre tableau 2 : évolutions temporelles
        titre_tableau2 = ft.Text("Évolutions des montants par durée",
                    weight=ft.FontWeight.BOLD,
                    size=18,
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
        
        # Contenair du titre tableau 2 pour mettre du padding
        titre_tableau2_contenair= ft.Container(content=titre_tableau2,
                                               alignment=ft.alignment.center,
                                               padding=ft.padding.only(top=35))
        
        # Tableau 2
        tableau2 = ft.DataTable(
                column_spacing=10,
                heading_row_height=30,
                heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),  
                data_row_min_height=25,
                divider_thickness=0.5,
                columns=[ft.DataColumn(ft.Text(c, size=11)) for c in df.columns],
                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=11)) for v in row])for row in df.values.tolist()]
                                            )

        # Cadre tableau 2 avec scroll automatique
        cadre_tableau2 = ft.Container(
            content=ft.Column([ft.Row([tableau2], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,  # hauteur fixe pour activer le scroll
                                    )




        # Contenair pour avoir texte + separateur sans le spacing 20 du output_zone
        graph1_separateur = ft.Column(controls=[graphe1_text, separation],
                                      spacing=0,  # pas d'espace entre les deux
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                      tight=True,  # réduit les marges
                                      )
        
        # Contenair pour avoir texte + separateur sans le spacing 20 du output_zone
        graph2_separateur = ft.Column(controls=[graphe2_text, separation],
                                      spacing=0,  # pas d'espace entre les deux
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                      tight=True,  # réduit les marges
                                      )
        
        # Contenair pour avoir texte + separateur sans le spacing 20 du output_zone
        tableau_separateur = ft.Column(controls=[tableau_text, separation],
                                      spacing=0,  # pas d'espace entre les deux
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                      tight=True,  # réduit les marges
                                      )
        

        # J'ajoute avec .extend car plusieurs ajout. Sinon c'est .append
        output_zone.controls.extend([graph1_separateur, graphe1_graphe, graph2_separateur, graphe2_graphe, tableau_separateur, titre_tableau1_contenair, cadre_tableau1, titre_tableau2_contenair, cadre_tableau2])

        page.update()

    # Personnalisation boutton
    bouton_simulation = ft.ElevatedButton(
        content=ft.Text("🚀 Lancer la simulation", weight=ft.FontWeight.BOLD),
        on_click=lancer_simulation,
        expand=True,  # prend toute la largeur
        width=600,  # largeur fixe en pixels
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_200,  # fond rouge
            color=ft.Colors.RED_700,      # texte blanc
            padding=ft.padding.symmetric(vertical=20),  # hauteur du bouton
            )
        )
    

    # Margin dans chque widget input. On met en column pour ca 
    inputs_column = ft.Column(controls=[dropdown_indice, input_montant, input_durees, input_mois_dca, bouton_simulation],
                              spacing=25,  # ici l'espacement vertical entre chaque widget
                              )
    
    return [text_graphique, separation, inputs_column, output_zone]


########################################################## FONCTION PRINCIPALE ########################################################## 

def dca_lp_page(page: ft.Page):
    page.clean()
    page.scroll = "auto"

    simulation = simulation_dca_vs_ls(page)

    # Bouton retour en haut à droite
    bouton_retour_haut = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,  # flèche gauche
        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
        tooltip="Retour accueil",
        on_click=lambda e: page.go("/")
    )

    # Container pour aligner à gauche la flèche retour
    container_retour_haut = ft.Container(
        content=ft.Row([bouton_retour_haut], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.all(0),        # plus aucun padding
        height=30, 
    )

    # Bouton Retour accueil
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/")  # Redirection vers la page d'accueil
    )

    # Container pour centrer le bouton retour
    container_bouton = ft.Container(
        content=bouton_retour,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20)  # Espacement avant et après
    )

    
    # Layout principal
    page.add(
            container_retour_haut,
            *simulation,
            container_bouton
            )


