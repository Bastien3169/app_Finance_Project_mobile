import flet as ft
from flet.plotly_chart import PlotlyChart
import matplotlib
matplotlib.use('Agg')  # Important pour Android
import matplotlib.pyplot as plt
import io
import base64
from src.models.control_datas.connexion_db_datas import *
from src.controllers.LP_VS_DCA import *
from src.components.components_views import *

# -------------------- Connexion DB --------------------
datas_actifs = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_actifs.get_list_indices()
actif_default = "S&P 500"

# -------------------- Styles --------------------
couleur_titre_separateur = ft.Colors.CYAN_400 #
couleur_bouton_fleche = ft.Colors.CYAN_700
titre_size = 20


################################## INPUT SECTION ##################################
def create_input_section():

        # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text = "📊 Simulation DCA vs LS", padding_text_top = 0, couleur_titre_separateur = couleur_titre_separateur)

    # Fonction : Dropdown (menu déroulant)
    dropdown_actif = dropdown("Sélectionnez un indice pour le graphique", actif_default, liste_actifs, handler= None)

    # Input
    input_montant = dcavsls_input (labels = "💰 Montant à investir (€)", values = "100000", hint_texte = "Ex: 100000")

    input_durees = dcavsls_input (labels = "⏳ Durées d'investissement (en années)", values = "5,10,15,20,25", hint_texte = "Ex: 5,10,15,20,25")

    input_mois_dca = dcavsls_input (labels ="📆 Mois de DCA", values = "6,12,24", hint_texte = "Ex: 6,12,24")

    return [*titre, dropdown_actif, input_montant, input_durees, input_mois_dca]


################################## SIMULATION HANDLER ##################################
def create_simulation_handler(page: ft.Page, dropdown_indice, input_montant, input_durees, input_mois_dca, output_zone):
    
    def lancer_simulation(e):
        output_zone.controls.clear()
        ticker = dropdown_indice.value
        somme_investie = float(input_montant.value)
        durees = [int(i.strip()) for i in input_durees.value.split(",") if i.strip().isdigit()]
        mois_dca_list = [int(i.strip()) for i in input_mois_dca.value.split(",") if i.strip().isdigit()]

        # Loader
        output_zone.controls.append(ft.Container(content=ft.ProgressRing(color=couleur_titre_separateur,
                                                                     width=50,height=50),
                                            padding=ft.padding.only(top=20),  # 👈 espace au-dessus du loader
                                            alignment=ft.alignment.center ))     # 👈 pour le centrer proprement
        page.update()

        # --- Calculs ---
        df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
        df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)

        # Retirer loader
        output_zone.controls.clear()

        # ======================================================== GRAPHIQUE 1 ======================================================== #
        titre_graph1 = titre_separateur(text = "📊 Gains par durée", 
                        padding_text_top = 35, 
                        couleur_titre_separateur = couleur_titre_separateur)

        fig1 = graphe_barre(df_resultats)

        # Créer une figure matplotlib à partir des données Plotly
        fig_mpl, ax = plt.subplots(figsize=(10, 6), facecolor='#1e1e1e')
        ax.set_facecolor('#2d2d2d')

        # Convertir la figure Plotly en données pour matplotlib
        # Pour un graphique à barres groupées
        x = df_resultats["Année"]
        width = 0.2  # Largeur des barres

        # Couleurs
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

        # Tracer chaque colonne (sauf 'Année')
        for i, col in enumerate(df_resultats.columns):
            if col != "Année":
                values = df_resultats[col].values
                offset = (i - 1) * width  # Ajuster l'offset pour centrer
                ax.bar([x_val + offset for x_val in range(len(x))], values, 
                    width=width, label=col, color=colors[i % len(colors)])

        ax.set_xlabel('Durée (années)', color='white')
        ax.set_ylabel('Montant final (€)', color='white')
        ax.set_title('Gains par durée d\'investissement', color='white', pad=20)
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, color='white')
        ax.legend(facecolor='#2d2d2d', edgecolor='white', labelcolor='white')
        ax.grid(True, alpha=0.3)

        # Couleur des axes
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')

        # Sauvegarder en PNG dans un buffer
        buf = io.BytesIO()
        fig_mpl.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='#1e1e1e')
        buf.seek(0)

        # Convertir en base64
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig_mpl)

        # Créer l'image Flet
        graphe1_graphe = ft.Container(
            content=ft.Image(
                src_base64=img_base64,
                fit=ft.ImageFit.CONTAIN,
            ),
            height=400,
            alignment=ft.alignment.center,
            padding=10,
            border=ft.border.all(1, couleur_titre_separateur),
            border_radius=10,)

        # ======================================================== GRAPHIQUE 2 ======================================================== #
        titre_graph2 = titre_separateur(text = "📈 Évolution de l’actif", 
                        padding_text_top = 35, 
                        couleur_titre_separateur = couleur_titre_separateur)

        try:
            fig2 = graphe_line(df, somme_investie)
            
            fig_mpl2, ax2 = plt.subplots(figsize=(10, 6), facecolor='#1e1e1e')
            ax2.set_facecolor('#2d2d2d')
            
            # Vérifier que le DataFrame a les bonnes colonnes
            required_columns = ['Date', 'Rendement DCA', 'Rendement LS', 'Durée', 'Mois DCA']
            has_all_columns = all(col in df.columns for col in required_columns)
            
            if has_all_columns and not df.empty:
                # Limiter à un nombre raisonnable de lignes pour éviter la surcharge
                plot_df = df.head(1000) if len(df) > 1000 else df
                
                # Tracer seulement quelques combinaisons pour plus de clarté
                unique_combinations = list(plot_df.groupby(['Durée', 'Mois DCA']).groups.keys())
                
                # Limiter à 5 combinaisons maximum
                for (duree, mois) in unique_combinations[:5]:
                    group = plot_df[(plot_df['Durée'] == duree) & (plot_df['Mois DCA'] == mois)]
                    
                    if not group.empty:
                        # Tracer DCA
                        ax2.plot(group['Date'], group['Rendement DCA'], 
                                label=f"DCA {mois} - {duree} ans", linewidth=1.5)
                        
                        # Tracer LumpSum
                        if 'Rendement LS' in group.columns:
                            ax2.plot(group['Date'], group['Rendement LS'], 
                                    label=f"LS - {duree} ans", linewidth=1.5, linestyle='--', alpha=0.7)
                
                # Ligne d'investissement initial
                ax2.axhline(y=somme_investie, color='red', linestyle=':', 
                        label=f'Investissement initial: {somme_investie:,.0f}€', alpha=0.5)
                
                ax2.set_xlabel('Date', color='white')
                ax2.set_ylabel('Valeur (€)', color='white')
                ax2.set_title('Évolution des stratégies d\'investissement', color='white', pad=20)
                ax2.legend(facecolor='#2d2d2d', edgecolor='white', labelcolor='white', fontsize=8)
                
            else:
                # Message si colonnes manquantes
                missing_cols = [col for col in required_columns if col not in df.columns]
                ax2.text(0.5, 0.5, f"Colonnes manquantes:\n{', '.join(missing_cols)}", 
                        ha='center', va='center', color='orange', fontsize=12)
                ax2.set_title('Données incomplètes', color='orange', pad=20)
            
            ax2.grid(True, alpha=0.2)
            ax2.xaxis.set_tick_params(rotation=45, colors='white')
            ax2.tick_params(colors='white')
            
            for spine in ax2.spines.values():
                spine.set_color('white')
            
            # Sauvegarder
            buf2 = io.BytesIO()
            fig_mpl2.savefig(buf2, format='png', dpi=100, bbox_inches='tight', facecolor='#1e1e1e')
            buf2.seek(0)
            img_base64_2 = base64.b64encode(buf2.read()).decode('utf-8')
            plt.close(fig_mpl2)
            
        except Exception as e:
            # En cas d'erreur, créer un graphique d'erreur
            print(f"Erreur création graphique 2: {e}")
            
            fig_mpl2, ax2 = plt.subplots(figsize=(10, 6), facecolor='#1e1e1e')
            ax2.set_facecolor('#2d2d2d')
            ax2.text(0.5, 0.5, f"Erreur d'affichage:\n{str(e)[:50]}...", 
                    ha='center', va='center', color='red', fontsize=12)
            ax2.set_title('Erreur de génération du graphique', color='red', pad=20)
            ax2.axis('off')
            
            buf2 = io.BytesIO()
            fig_mpl2.savefig(buf2, format='png', dpi=100, bbox_inches='tight', facecolor='#1e1e1e')
            buf2.seek(0)
            img_base64_2 = base64.b64encode(buf2.read()).decode('utf-8')
            plt.close(fig_mpl2)

        graphe2_graphe = ft.Container(
            content=ft.Image(
                src_base64=img_base64_2,
                fit=ft.ImageFit.CONTAIN,
            ),
            height=400,
            alignment=ft.alignment.center,
            padding=10,
            border=ft.border.all(1, couleur_titre_separateur),
            border_radius=10,)



        # ======================================================== TITRE TABLEAU ======================================================== #
        titre_tableau = titre_separateur(text = "📋 Résultats en tableau", 
                        padding_text_top = 35, 
                        couleur_titre_separateur = couleur_titre_separateur)
        
        #============================================= TABLEAU 1 ============================================#
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
        output_zone.controls.extend([*titre_graph1, graphe1_graphe, *titre_graph2, graphe2_graphe, *titre_tableau,
                                     titre_tableau1_contenair, cadre_tableau1, titre_tableau2_contenair, cadre_tableau2])

        page.update()

    return lancer_simulation


################################## PAGE PRINCIPALE ##################################

def dca_lp_page(page: ft.Page):
    page.clean()
    page.title = "🏛️ Simulation DCA vs Lump Sum"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Fonction bouton retour haut
    bouton_retour_haut=bout_ret_haut(couleur_bouton_fleche, handler = lambda e: page.go("/"))

    # Bouton retour acceuol en bas
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler = lambda e: page.go("/"))

     # Création de la zobe out_put vide pour être accessible dans la fonction interne
    output_zone = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)  # centre les enfants directs

    # --- Inputs (renvoie un tuple) ---
    inputs = create_input_section()
    text_separateur_1 = inputs[0]
    text_separateur_2 = inputs[1]
    dropdown_indice = inputs[2]
    input_montant = inputs[3]
    input_durees = inputs[4]
    input_mois_dca = inputs[5]

    # --- Simulation handler ---
    lancer_simulation = create_simulation_handler(page, dropdown_indice, input_montant, input_durees, input_mois_dca, output_zone)

    # --- Bouton simulation --- 
    bouton_simulation =bouton_on_click ("Lancer la simulation", lancer_simulation, couleur_titre_separateur, icon=ft.Icons.CALCULATE)

    # Construis la colonne des contrôles (centrée horizontalement)
    controls_column = ft.Column(
        controls=[dropdown_indice,input_montant, input_durees, input_mois_dca , bouton_simulation,],
        spacing=25,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,      # centre horizontalement les widgets
        alignment=ft.MainAxisAlignment.START,                   # position verticale à l'intérieur du conteneur
        tight=False
    )

 
    # Ajout à la page : container centré + zone de sortie en dessous (ou à droite selon layout souhaité)
    page.add(bouton_retour_haut,text_separateur_1, text_separateur_2, controls_column, output_zone, bouton_acceuil)
