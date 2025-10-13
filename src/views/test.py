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

################################## INPUT #################################################
def simulation_dca_vs_ls(page: ft.Page):
    page.title = "🏛️ Simulation DCA vs Lump Sum"
    page.scroll = "adaptive"

    # Widget : titre
    text_graphique = ft.Text("📈 Graphiques des indices", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=21)

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
        border=ft.InputBorder.OUTLINE,  # ✅ Bordure native
        border_radius=8,  # ✅ Coins arrondis
        border_color=ft.Colors.WHITE30,  # ✅ Bordure blanche
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


    output_zone = ft.Column(spacing=20)

    # Action : lancer la simulation
    def lancer_simulation(e):
        output_zone.controls.clear()
        output_zone.spacing = 20  # ✅ Réappliquer le spacing après clear

        ticker = dropdown_indice.value
        somme_investie = float(input_montant.value)
        durees = [int(x.strip()) for x in input_durees.value.split(",") if x.strip().isdigit()]
        mois_dca_list = [int(x.strip()) for x in input_mois_dca.value.split(",") if x.strip().isdigit()]

        output_zone.controls.append(ft.Text("Calcul en cours...", italic=True))
        page.update()

        # 🔹 Données financières
        data_financiere = datas_indices.get_prix_date(ticker)

        # 🔹 Calculs
        df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
        df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)

        # 🔹 Graphique 1 : montants finaux
        output_zone.controls.append(ft.Text(
            "📈 Les montants finaux obtenus en fonction de la durée du placement",
            size=18, weight="bold"
        ))
        fig1 = graphe_barre(df_resultats)
        output_zone.controls.append(PlotlyChart(fig1, expand=True))

        # 🔹 Graphique 2 : évolution dans le temps
        output_zone.controls.append(ft.Text(
            "📈 Évolution des placements en fonction du temps",
            size=18, weight="bold"
        ))
        fig2 = graphe_line(df, somme_investie)
        output_zone.controls.append(PlotlyChart(fig2, expand=True))

        # 🔹 Tableaux
        output_zone.controls.append(ft.Text("📋 Tableaux comparatifs DCA vs Lump Sum", size=18, weight="bold"))

        # Montants finaux
        output_zone.controls.append(ft.Text("Tableau des montants finaux"))
        output_zone.controls.append(ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in df_resultats.columns],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in row])
                  for row in df_resultats.tail(10).values.tolist()]
        ))

        # Évolution temporelle
        output_zone.controls.append(ft.Text("Tableau des évolutions temporelles"))
        output_zone.controls.append(ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in df.columns],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in row])
                  for row in df.tail(10).values.tolist()]
        ))

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


################################### FONCTION PRINCIPALE ################################

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


