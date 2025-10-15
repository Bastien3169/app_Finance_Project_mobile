import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *
from src.controllers.LP_VS_DCA import *

# -------------------- Connexion DB --------------------
datas_indices = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_indices.get_list_indices()
actif_default = "S&P 500"

# -------------------- Styles --------------------
couleur_titre_separateur = ft.Colors.RED_200
couleur_bouton_fleche = ft.Colors.RED_700
titre_size = 20


################################## INPUT SECTION ##################################
def create_input_section():
    """Crée les champs de saisie et le menu déroulant"""
    dropdown_indice = ft.Dropdown(
        label=ft.Text("Sélectionnez un indice pour le graphique", 
                      style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
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
        border=ft.InputBorder.OUTLINE,
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

    inputs_column = ft.Column(
        controls=[dropdown_indice, input_montant, input_durees, input_mois_dca],
        spacing=25,
    )

    return inputs_column, dropdown_indice, input_montant, input_durees, input_mois_dca


################################## OUTPUT SECTION ##################################
def create_output_section():
    """Crée la zone d'affichage dynamique"""
    return ft.Column()


################################## SIMULATION HANDLER ##################################
def create_simulation_handler(page, dropdown_indice, input_montant, input_durees, input_mois_dca, output_zone):
    """Crée la fonction qui gère la simulation complète"""

    def lancer_simulation(e):
        output_zone.controls.clear()
        ticker = dropdown_indice.value
        somme_investie = float(input_montant.value)
        durees = [int(x.strip()) for x in input_durees.value.split(",") if x.strip().isdigit()]
        mois_dca_list = [int(x.strip()) for x in input_mois_dca.value.split(",") if x.strip().isdigit()]

        # Loader
        output_zone.controls.append(ft.ProgressRing(color=couleur_titre_separateur, width=50, height=50))
        page.update()

        # --- Calculs ---
        df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
        df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)

        # Retirer loader
        output_zone.controls.clear()

        # ======================================================== GRAPHIQUE 1 ======================================================== #
        graph1_text = ft.Container(
            content=ft.Text("📈 Gains par durée", 
                            color=couleur_titre_separateur, 
                            weight=ft.FontWeight.BOLD, 
                            size=titre_size),
            padding=ft.padding.only(top=35),
        )

        separation = ft.Container(
            content=ft.Divider(thickness=2, color=couleur_titre_separateur),
            padding=ft.padding.only(bottom=15)
        )

        fig1 = graphe_barre(df_resultats)
        graphe1_graphe = PlotlyChart(fig1, expand=True)

        # ======================================================== GRAPHIQUE 2 ======================================================== #
        graph2_text = ft.Container(
            content=ft.Text("📊 Évolution de l’actif",
                            color=couleur_titre_separateur,
                            weight=ft.FontWeight.BOLD,
                            size=titre_size),
            padding=ft.padding.only(top=35),
        )

        fig2 = graphe_line(df, somme_investie)
        graphe2_graphe = PlotlyChart(fig2, expand=True)

        # ======================================================== TABLEAU 1 ======================================================== #
        tableau_text = ft.Container(
            content=ft.Text("📋 Résultats en tableau",
                            color=couleur_titre_separateur,
                            weight=ft.FontWeight.BOLD,
                            size=titre_size),
            padding=ft.padding.only(top=35),
        )

        titre_tableau1 = ft.Text("Montants finaux par durée", weight="bold", size=18, 
                                 text_align=ft.TextAlign.CENTER,
                                 style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
        titre_tableau1_contenair = ft.Container(content=titre_tableau1, alignment=ft.alignment.center)

        tableau1 = ft.DataTable(
            column_spacing=10,
            heading_row_height=30,
            heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
            data_row_min_height=25,
            divider_thickness=0.5,
            columns=[ft.DataColumn(ft.Text(c, size=11)) for c in df_resultats.columns],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=11)) for v in row])
                for row in df_resultats.values.tolist()
            ],
        )

        cadre_tableau1 = ft.Container(
            content=ft.Column([ft.Row([tableau1], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,
        )

        # ======================================================== TABLEAU 2 ======================================================== #
        titre_tableau2 = ft.Text("Évolutions temporelles",
                                 weight="bold", size=18,
                                 text_align=ft.TextAlign.CENTER,
                                 style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
        titre_tableau2_contenair = ft.Container(content=titre_tableau2, alignment=ft.alignment.center, padding=ft.padding.only(top=35))

        tableau2 = ft.DataTable(
            column_spacing=10,
            heading_row_height=30,
            heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
            data_row_min_height=25,
            divider_thickness=0.5,
            columns=[ft.DataColumn(ft.Text(c, size=11)) for c in df.columns],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=11)) for v in row])
                for row in df.values.tolist()
            ],
        )

        cadre_tableau2 = ft.Container(
            content=ft.Column([ft.Row([tableau2], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,
        )

        # Ajout dans la zone d'affichage
        output_zone.controls.extend([
            graph1_text, separation, graphe1_graphe,
            graph2_text, separation, graphe2_graphe,
            tableau_text, separation,
            titre_tableau1_contenair, cadre_tableau1,
            titre_tableau2_contenair, cadre_tableau2
        ])

        page.update()

    return lancer_simulation


################################## BUTTON SECTION ##################################
def create_simulation_button(lancer_simulation):
    """Crée le bouton de lancement"""
    return ft.ElevatedButton(
        content=ft.Text("🚀 Lancer la simulation", weight=ft.FontWeight.BOLD),
        on_click=lancer_simulation,
        expand=True,
        width=600,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_200,
            color=ft.Colors.RED_700,
            padding=ft.padding.symmetric(vertical=20),
        )
    )


################################## PAGE PRINCIPALE ##################################
def simulation_dca_vs_ls(page: ft.Page):
    page.title = "🏛️ Simulation DCA vs Lump Sum"
    page.scroll = "adaptive"

    text_graphique = ft.Text("📈 Simulation DCA vs Lump Sum", color=couleur_titre_separateur, weight="bold", size=titre_size)
    separation = ft.Divider(thickness=2, color=couleur_titre_separateur)

    inputs_column, dropdown_indice, input_montant, input_durees, input_mois_dca = create_input_section()
    output_zone = create_output_section()
    lancer_simulation = create_simulation_handler(page, dropdown_indice, input_montant, input_durees, input_mois_dca, output_zone)
    bouton = create_simulation_button(lancer_simulation)

    inputs_column.controls.append(bouton)

    return [text_graphique, separation, inputs_column, output_zone]


################################## WRAPPER PAGE ##################################
def dca_lp_page(page: ft.Page):
    page.clean()
    page.scroll = "auto"

    simulation = simulation_dca_vs_ls(page)

    bouton_retour = ft.ElevatedButton(
        "🏠 Retour accueil",
        icon=ft.Icons.HOME,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/")
    )

    container_bouton = ft.Container(content=bouton_retour, alignment=ft.alignment.center, padding=ft.padding.only(top=30, bottom=20))

    page.add(*simulation, container_bouton)
