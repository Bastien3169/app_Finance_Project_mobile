import flet as ft
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
import numpy as np
from src.models.control_datas.connexion_db_datas import *
from src.controllers.LP_VS_DCA import *
from src.components.components_views import *

# -------------------- Connexion DB --------------------
datas_actifs = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_actifs.get_list_indices()
actif_default = "S&P 500"

# -------------------- Styles --------------------
couleur_titre_separateur = ft.Colors.CYAN_400
couleur_bouton_fleche = ft.Colors.CYAN_700
titre_size = 20

################################## INPUT SECTION ##################################
def create_input_section():
    titre = titre_separateur(text="📊 Simulation DCA vs LS", padding_text_top=0,
                            couleur_titre_separateur=couleur_titre_separateur)
    dropdown_actif = dropdown("Sélectionnez un indice pour le graphique",
                             actif_default, liste_actifs, handler=None)
    input_montant = dcavsls_input(labels="💰 Montant à investir (€)", values="100000",
                                 hint_texte="Ex: 100000")
    input_durees = dcavsls_input(labels="⏳ Durées d'investissement (en années)",
                                values="5,10,15,20,25", hint_texte="Ex: 5,10,15,20,25")
    input_mois_dca = dcavsls_input(labels="📆 Mois de DCA", values="6,12,24",
                                  hint_texte="Ex: 6,12,24")
    return [*titre, dropdown_actif, input_montant, input_durees, input_mois_dca]


################################## GRAPHIQUE 1 - BARRES ##################################
def create_graph_barres(df_resultats, couleur_titre_separateur):
    """
    Graphique à barres groupées pour comparer DCA vs LumpSum par durée
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Inverser l'ordre des données (du plus grand au plus petit)
    df_resultats = df_resultats.iloc[::-1].reset_index(drop=True)
    
    # Récupération des données
    annees = df_resultats["Année"].values
    n_annees = len(annees)
    
    # Trouver toutes les colonnes DCA
    colonnes_dca = [col for col in df_resultats.columns if col.startswith("DCA")]
    n_colonnes = len(colonnes_dca) + 1  # +1 pour LumpSum
    
    # Palette de couleurs vives (extension automatique si besoin)
    couleurs_base = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                     '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']
    
    # Générer plus de couleurs si nécessaire
    def get_color(index):
        if index < len(couleurs_base):
            return couleurs_base[index]
        else:
            # Générer une couleur avec variation de teinte
            import matplotlib.cm as cm
            cmap = cm.get_cmap('tab20')
            return cmap(index % 20 / 20)
    
    # Calcul de la largeur des barres et positions
    largeur_barre = 0.8 / n_colonnes
    positions_base = np.arange(n_annees)
    
    # Tracer chaque colonne DCA
    for i, col in enumerate(colonnes_dca):
        offset = (i - (n_colonnes - 1) / 2) * largeur_barre
        ax.bar(positions_base + offset, 
               df_resultats[col].values,
               width=largeur_barre,
               label=col,
               color=get_color(i),
               edgecolor='white',
               linewidth=0.5)
    
    # Tracer LumpSum
    if "LumpSum" in df_resultats.columns:
        offset = (len(colonnes_dca) - (n_colonnes - 1) / 2) * largeur_barre
        ax.bar(positions_base + offset,
               df_resultats["LumpSum"].values,
               width=largeur_barre,
               label="LumpSum",
               color='#000000',
               edgecolor='white',
               linewidth=0.5)
    
    # ✅ Titre
    ax.set_title('Gains par durée d\'investissement', 
                 color='white', fontsize=30)
    
    # ✅ Axe X - CENTRÉ sur les années (décroissant)
    ax.set_xticks(positions_base)
    ax.set_xticklabels(annees, color='white', fontsize=14)
    ax.set_xlabel('Durée (années)', color='white', fontsize=20, labelpad=15)
    
    # ✅ Axe Y
    ax.set_ylabel('Montant final (€)', color='white', fontsize=20, labelpad=15)
    ax.tick_params(axis='y', colors='white', labelsize=14)
    
    # ✅ Légende
    ax.legend(facecolor='#2d2d2d', edgecolor='white', 
              labelcolor='white', fontsize=12, loc='upper right')
    
    # ✅ Grille sobre
    ax.grid(True, axis='y', linestyle='-', alpha=0.25, color="#FFFFFF")
    
    # ✅ Suppression des bordures
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    
    # ✅ Layout serré
    fig.tight_layout(pad=0.5)
    
    # Export en base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, dpi=300)
    buf.seek(0)
    plt.close(fig)
    
    return base64.b64encode(buf.read()).decode('utf-8')


################################## GRAPHIQUE 2 - LIGNES ##################################
def create_graph_ligne(df, somme_investie, couleur_titre_separateur):
    """
    Graphique de lignes pour l'évolution temporelle DCA vs LumpSum
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Vérification DataFrame vide
    if df.empty:
        ax.text(0.5, 0.5, "Aucune donnée à afficher",
                ha='center', va='center', color='orange', fontsize=20)
        ax.set_title('Erreur : Données manquantes', color='orange', fontsize=30)
        ax.axis('off')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    # Déterminer les noms des colonnes
    col_dca = 'DCA' if 'DCA' in df.columns else 'Rendement DCA'
    col_ls = 'LS' if 'LS' in df.columns else 'Rendement LS'
    
    # Vérification des colonnes essentielles
    if 'Date' not in df.columns or col_dca not in df.columns or col_ls not in df.columns:
        ax.text(0.5, 0.5, "Colonnes essentielles manquantes",
                ha='center', va='center', color='orange', fontsize=20)
        ax.set_title('Erreur de structure', color='orange', fontsize=30)
        ax.axis('off')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent=True, dpi=300)
        buf.seek(0)
        plt.close(fig)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    try:
        plot_df = df.head(1000) if len(df) > 1000 else df.copy()
        
        # Même palette de couleurs que le graphique 1 (vives et jolies)
        couleurs_base = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                         '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']
        
        def get_color_dca(index):
            """Couleur pour DCA (même palette que graphique 1)"""
            if index < len(couleurs_base):
                return couleurs_base[index]
            else:
                import matplotlib.cm as cm
                cmap = cm.get_cmap('tab20')
                return cmap(index % 20 / 20)
        
        def get_color_ls(index):
            """Couleur pour LS (légèrement plus foncée/différente)"""
            # Décalage de 1 pour différencier LS de DCA
            offset_index = index + 1
            if offset_index < len(couleurs_base):
                return couleurs_base[offset_index]
            else:
                import matplotlib.cm as cm
                cmap = cm.get_cmap('tab20b')
                return cmap(offset_index % 20 / 20)
        
        # Tracer par combinaisons si colonnes disponibles
        if 'Durée' in df.columns and 'Mois DCA' in df.columns:
            combinations = list(plot_df.groupby(['Durée', 'Mois DCA']).groups.keys())
            
            # Tracer TOUTES les combinaisons (pas de limite à 5)
            for idx, (duree, mois) in enumerate(combinations):
                group = plot_df[(plot_df['Durée'] == duree) & (plot_df['Mois DCA'] == mois)].copy()
                
                if not group.empty and len(group) > 0:
                    ax.plot(group['Date'], group[col_dca],
                           label=f"DCA {mois} - {duree}",
                           linewidth=2,
                           color=get_color_dca(idx),
                           linestyle='--')
                    
                    ax.plot(group['Date'], group[col_ls],
                           label=f"LS - {duree}",
                           linewidth=2.5,
                           color=get_color_ls(idx))
        else:
            # Mode simple sans groupement
            ax.plot(plot_df['Date'], plot_df[col_dca],
                   label="DCA", linewidth=2,
                   color=get_color_dca(0), linestyle='--')
            
            ax.plot(plot_df['Date'], plot_df[col_ls],
                   label="LumpSum", linewidth=2.5,
                   color=get_color_ls(0))
        
        # Ligne d'investissement initial
        ax.axhline(y=somme_investie, color='red', linestyle=':', 
                   linewidth=2, label=f'Investissement: {somme_investie:,.0f}€',
                   alpha=0.7)
        
        # Configuration graphique
        ax.set_title('Évolution des stratégies d\'investissement',
                     color='white', fontsize=30)
        
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.set_xlabel('Date', color='white', fontsize=20, labelpad=15)
        ax.tick_params(axis='x', colors='white', labelsize=14, rotation=45)
        
        ax.set_ylabel('Valeur du portefeuille (€)', color='white', fontsize=20, labelpad=15)
        ax.tick_params(axis='y', colors='white', labelsize=14)
        
        ax.legend(facecolor='#2d2d2d', edgecolor='white',
                  labelcolor='white', fontsize=10, loc='best')
        
        ax.grid(True, linestyle='-', alpha=0.25, color="#FFFFFF")
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        
        fig.tight_layout(pad=0.5)
        
    except Exception as e:
        ax.clear()
        ax.text(0.5, 0.5, f"Erreur: {str(e)[:100]}",
                ha='center', va='center', color='red', fontsize=14)
        ax.set_title('Erreur de génération', color='red', fontsize=30)
        ax.axis('off')
    
    # Export en base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, dpi=300)
    buf.seek(0)
    plt.close(fig)
    
    return base64.b64encode(buf.read()).decode('utf-8')


################################## SIMULATION HANDLER ##################################
def create_simulation_handler(page: ft.Page, dropdown_indice, input_montant,
                              input_durees, input_mois_dca, output_zone):
    def lancer_simulation(e):
        output_zone.controls.clear()
        
        ticker = dropdown_indice.value
        somme_investie = float(input_montant.value)
        durees = [int(i.strip()) for i in input_durees.value.split(",") if i.strip().isdigit()]
        mois_dca_list = [int(i.strip()) for i in input_mois_dca.value.split(",") if i.strip().isdigit()]
        
        # Loader
        output_zone.controls.append(
            ft.Container(
                content=ft.ProgressRing(color=couleur_titre_separateur, width=50, height=50),
                padding=ft.padding.only(top=20),
                alignment=ft.alignment.center
            )
        )
        page.update()
        
        # --- Calculs ---
        df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
        df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)
        
        # Retirer loader
        output_zone.controls.clear()
        
        # ======== GRAPHIQUE 1 - BARRES ======== #
        titre_graph1 = titre_separateur(
            text="📊 Gains par durée",
            padding_text_top=35,
            couleur_titre_separateur=couleur_titre_separateur
        )
        
        img_base64_1 = create_graph_barres(df_resultats, couleur_titre_separateur)
        
        graphe1_container = ft.Column([
            ft.Container(
                content=ft.Image(src_base64=img_base64_1, fit=ft.ImageFit.CONTAIN),
                padding=ft.padding.symmetric(vertical=15),
                border_radius=22,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                bgcolor='black',
            )
        ])
        
        # ======== GRAPHIQUE 2 - LIGNES ======== #
        titre_graph2 = titre_separateur(
            text="📈 Évolution de l'actif",
            padding_text_top=35,
            couleur_titre_separateur=couleur_titre_separateur
        )
        
        img_base64_2 = create_graph_ligne(df, somme_investie, couleur_titre_separateur)
        
        graphe2_container = ft.Column([
            ft.Container(
                content=ft.Image(src_base64=img_base64_2, fit=ft.ImageFit.CONTAIN),
                padding=ft.padding.symmetric(vertical=15),
                border_radius=22,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                bgcolor='black',
            )
        ])
        
        # ======== TABLEAUX ======== #
        titre_tableau = titre_separateur(
            text="📋 Résultats en tableau",
            padding_text_top=35,
            couleur_titre_separateur=couleur_titre_separateur
        )
        
        # Tableau 1
        titre_tableau1 = ft.Text(
            "Montants finaux par durée",
            weight="bold", size=18,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)
        )
        titre_tableau1_container = ft.Container(
            content=titre_tableau1,
            alignment=ft.alignment.center
        )
        
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
            content=ft.Column([ft.Row([tableau1], scroll=ft.ScrollMode.AUTO)],
                            scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,
        )
        
        # Tableau 2
        titre_tableau2 = ft.Text(
            "Évolutions temporelles",
            weight="bold", size=18,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)
        )
        titre_tableau2_container = ft.Container(
            content=titre_tableau2,
            alignment=ft.alignment.center,
            padding=ft.padding.only(top=35)
        )
        
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
            content=ft.Column([ft.Row([tableau2], scroll=ft.ScrollMode.AUTO)],
                            scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(0.5, couleur_titre_separateur),
            border_radius=10,
            padding=5,
            height=300,
        )
        
        # Ajout dans la zone d'affichage
        output_zone.controls.extend([
            *titre_graph1, graphe1_container,
            *titre_graph2, graphe2_container,
            *titre_tableau,
            titre_tableau1_container, cadre_tableau1,
            titre_tableau2_container, cadre_tableau2
        ])
        
        page.update()
    
    return lancer_simulation


################################## PAGE PRINCIPALE ##################################
def dca_lp_page(page: ft.Page):
    page.clean()
    page.title = "🏛 Simulation DCA vs Lump Sum"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    
    # Boutons
    bouton_retour_haut = bout_ret_haut(couleur_bouton_fleche, handler=lambda e: page.go("/"))
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"))
    
    # Zone output
    output_zone = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Inputs
    inputs = create_input_section()
    text_separateur_1 = inputs[0]
    text_separateur_2 = inputs[1]
    dropdown_indice = inputs[2]
    input_montant = inputs[3]
    input_durees = inputs[4]
    input_mois_dca = inputs[5]
    
    # Handler
    lancer_simulation = create_simulation_handler(
        page, dropdown_indice, input_montant, 
        input_durees, input_mois_dca, output_zone
    )
    
    # Bouton simulation
    bouton_simulation = bouton_on_click(
        "Lancer la simulation",
        lancer_simulation,
        couleur_titre_separateur,
        icon=ft.Icons.CALCULATE
    )
    
    # Colonne des contrôles
    controls_column = ft.Column(
        controls=[dropdown_indice, input_montant, input_durees, 
                 input_mois_dca, bouton_simulation],
        spacing=25,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.START,
        tight=False
    )
    
    # Ajout à la page
    page.add(
        bouton_retour_haut,
        text_separateur_1,
        text_separateur_2,
        controls_column,
        output_zone,
        bouton_acceuil
    )