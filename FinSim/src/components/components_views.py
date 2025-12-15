import flet as ft
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
import io

'''
label_style → stylise le label
hint_style → stylise le placeholder
text_style → stylise le texte saisi / affiché (donc ce qui vient de value ou ce que tape l’utilisateur)
'''

# ------- titre + séparateur dans conteneur -------
def titre_separateur(text,couleur_titre_separateur, padding_text_top = 35):
    
     # Widget : titre dans container pour le padding
    text_composition = ft.Container(content=ft.Text(text,
                                                    color=couleur_titre_separateur,
                                                    weight=ft.FontWeight.BOLD,
                                                    size=21),
                                                    padding=ft.padding.only(top=padding_text_top))

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur), padding=ft.padding.only(bottom=15))
    
    return [text_composition, separation]


# ------- loader page -------
def loader_page(couleur_titre_separateur):

    loader = ft.ProgressRing(color= couleur_titre_separateur, visible=False, width=50, height=50)

    return loader


# ------- loader global -------
def loader_globale(couleur_titre_separateur):
    loader_global = ft.Container(content=ft.ProgressRing(color=couleur_titre_separateur, width=60, height=60),
                                 alignment=ft.alignment.center,
                                 margin=ft.margin.all(100),
                                 visible=True)
    return loader_global


# ------- dropdown -------
def dropdown (text, actif_default, liste_actifs, handler= None):
    dropdown_multi = ft.Dropdown(label=text,
                                label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
                                options=[ft.dropdown.Option(i) for i in liste_actifs],
                                border_radius=8,
                                border_color=ft.Colors.WHITE30,
                                on_change=handler,
                                value=actif_default,
                                expand=True,
                                width=400,)
    return dropdown_multi


# ------- input (periode actif) avec un width = 250 ! -------
def periode_input(text_label="Ex: 3, 9, 18...", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=250, icones=None, fonc_ajouter_periode=None): 
    input_periode = ft.TextField(label=text_label, 
                                label_style=ft.TextStyle(size=12, italic=True),
                                border_radius=8,
                                border_color=ft.Colors.WHITE30,
                                hint_text = hint_texte,
                                hint_style = hint_styl,
                                text_style=ft.TextStyle(size=11),
                                password=passwords,
                                can_reveal_password=oeil,
                                width=widths,
                                icon=icones,
                                keyboard_type=ft.KeyboardType.TEXT, 
                                on_submit=fonc_ajouter_periode,)
    return input_periode


# ------- input (DCAvsLS) avec des valeur mis en avance dans l'input -------
def dcavsls_input (labels, values, hint_texte):
    input_montant = ft.TextField(label=labels,
                                label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                                value=values,
                                text_style=ft.TextStyle(size=12,italic=True,weight=ft.FontWeight.BOLD,),
                                border_radius=8,
                                border_color=ft.Colors.WHITE30,
                                hint_text = hint_texte,
                                hint_style = ft.TextStyle(size=10, italic=True,),
                                width=400,
                                keyboard_type=ft.KeyboardType.TEXT,)
    return  input_montant



# ------- Regourpement des widget par section -------
def contenu_widget(titre, liste_widget):
    contenu = ft.Column(controls=[*titre,ft.Column(controls=[*liste_widget],
                                                    spacing=10,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,),],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            scroll=ft.ScrollMode.AUTO,
                            alignment=ft.MainAxisAlignment.CENTER,)
    return contenu


# ------- Bouton on_cick -------
def bouton_on_click (text, on_click, couleur_bouton, icon=None):
    bouton = ft.ElevatedButton(text,
                                on_click=on_click,
                                icon=icon,
                                style=ft.ButtonStyle(bgcolor=couleur_bouton, color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15)),
                                width=400,)
    return bouton

# ------- Bouton retour en haut à gauche -------
def bout_ret_haut(couleur_bouton_fleche, handler = None):
    bouton_retour_haut = ft.IconButton(icon=ft.Icons.ARROW_BACK,  # flèche gauche
                                        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
                                        tooltip="Retour accueil",
                                        on_click=handler)

    container_retour_haut = ft.Container(content=ft.Row([bouton_retour_haut], 
                                                        alignment=ft.MainAxisAlignment.START),
                                        padding=ft.padding.only(top=30))        # plus aucun padding
    
    return container_retour_haut


# ------- Bouton retour acceuil -------
def bout_ret_acceuil(couleur_bouton_fleche, text="Retour accueil", handler = None, icons=ft.Icons.HOME):
    bouton_retour = ft.ElevatedButton(text,
                                    icon=icons, # ajoute icône à gauche du texte
                                    style=ft.ButtonStyle(color=ft.Colors.WHITE,
                                                        bgcolor=couleur_bouton_fleche,
                                                        padding=ft.padding.symmetric(horizontal=20, vertical=15)),
                                    on_click=handler)  # Redirection vers la page d'accueil
    

    container_bouton = ft.Container(content=bouton_retour,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.only(top=20, bottom=20))  # Espacement avant et après
    
    return container_bouton


# ------- Structure tableau + cadre -------

def tableau_cadre(expands=False, couleur=ft.Colors.WHITE, heights=None):
    table = ft.DataTable(expand=expands,
                        column_spacing=10,
                        heading_row_height=30,
                        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
                        data_row_min_height=35,
                        data_row_max_height=35,
                        divider_thickness=0.5,
                        columns=[],
                        rows=[],)

    # ✅ Scroll horizontal (pour les colonnes larges)
    horizontal_scroll = ft.Row(controls=[table], scroll=ft.ScrollMode.AUTO,)

    # ✅ Scroll vertical (pour les nombreuses lignes)
    vertical_scroll = ft.Column(controls=[horizontal_scroll],
                                scroll=ft.ScrollMode.AUTO,
                                horizontal_alignment=ft.CrossAxisAlignment.START,)

    # ✅ Cadre final
    cadre_tableau = ft.Container(content=vertical_scroll,
                                border=ft.border.all(1, couleur),
                                border_radius=10,
                                height=heights,
                                padding=5,)
    
    return table, cadre_tableau


# ------- graphique matplotlib actif -------
def graphique_matplot_actif(page, couleur_titre_separateur, loader, chart_container, datas_actifs,dropdown_actif):  
    loader.visible = True
    page.update()

    selected_actif = dropdown_actif.value
    df = datas_actifs.get_prix_date(selected_actif)

    if df.empty:
        chart_container.content = ft.Text("Aucune donnée disponible", color="red")
        loader.visible = False
        page.update()
        return

    # -------- MATPLOTLIB --------
    fig, ax = plt.subplots(figsize=(12, 8))

    # ✅ Fond transparent
    ax.plot(df['Date'], df['Close'], color=couleur_titre_separateur, linewidth=3)

    # ✅ Titre
    ax.set_title(f'Évolution du prix de {selected_actif}', color='white', fontsize=30,)

    # ✅ Axe X
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlabel('Date', color='white', fontsize=20, labelpad=15)
    ax.tick_params(axis='x', colors='white', labelsize=14, rotation=45)

    # ✅ Axe Y
    ax.set_ylabel('Prix', color='white', fontsize=20, labelpad=0)
    ax.tick_params(axis='y', colors='white', labelsize=14, rotation=45)

    # ✅ Grille sobre
    ax.grid(True, axis='y', linestyle='-', alpha=0.25, color="#FFFFFF")

    # ✅ Suppression des bordures graphiques
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # ✅ IMPORTANT : évite la coupe des labels
    fig.tight_layout(pad=0.5)

    # ✅ Export image transparente (sans couper les axes)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', transparent=True, dpi=300)
    buf.seek(0)
    plt.close(fig)

    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    # -------- FLET --------
    chart_container.content = ft.Column([ft.Container(content=ft.Image(src_base64=img_base64,
                                                                    fit=ft.ImageFit.CONTAIN,
                                                                    expand=True),
                                                    expand=True,
                                                    padding=0.5,
                                                    # ✅ Bords arrondis
                                                    border_radius=22,
                                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                                    # ✅ Fond glossy sombre
                                                    bgcolor='black',),],
                                        expand=True,)
        
    loader.visible = False
    page.update()

