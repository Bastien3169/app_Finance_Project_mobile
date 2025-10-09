import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *
from src.controllers.LP_VS_DCA import *
# Auth désactivé pour éviter problème cookies
# from src.models.users_db.models_db_users_test import AuthManager, AdminManager

# -------------------- Connexion DB --------------------
datas_indices = FinanceDatabaseIndice(db_path="data.db")
liste_indices = datas_indices.get_list_indices()

# -------------------- Fonction Flet --------------------
def simulation_dca_vs_ls(page: ft.Page):
    page.title = "🏛️ Simulation DCA vs Lump Sum"
    page.scroll = "adaptive"

    # Données de base
    liste_indices = ["S&P 500", "NASDAQ 100", "CAC 40"]
    indice_default = "S&P 500"

    # Widgets utilisateur
    select_indice = ft.Dropdown(
        label="Choisissez un indice pour le graphique",
        options=[ft.dropdown.Option(i) for i in liste_indices],
        value=indice_default
    )

    input_montant = ft.TextField(
        label="💰 Montant à investir (€)",
        value="100000",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    input_durees = ft.TextField(
        label="⏳ Durées d'investissement (en années)",
        value="5,10,15,20,25",
        hint_text="Ex: 5,10,15,20,25"
    )

    input_mois_dca = ft.TextField(
        label="📆 Mois de DCA",
        value="6,12,24",
        hint_text="Ex: 6,12,24"
    )

    output_zone = ft.Column(spacing=20)

    # Action : lancer la simulation
    def lancer_simulation(e):
        output_zone.controls.clear()

        ticker = select_indice.value
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

    bouton_simulation = ft.ElevatedButton(
        text="🚀 Lancer la simulation",
        on_click=lancer_simulation
    )

    # Layout principal
    page.add(
        ft.Column([
            ft.Text("🏛️ Simulation DCA vs Lump Sum", size=22, weight="bold"),
            select_indice,
            input_montant,
            input_durees,
            input_mois_dca,
            bouton_simulation,
            output_zone
        ], scroll=ft.ScrollMode.AUTO, spacing=20)
    )

# -------------------- Lancer Flet --------------------
if __name__ == "__main__":
    ft.app(target=simulation_dca_vs_ls, view=ft.WEB_BROWSER)
