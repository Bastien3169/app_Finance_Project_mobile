import flet as ft

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
                                keyboard_type=ft.KeyboardType.NUMBER, 
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
                                keyboard_type=ft.KeyboardType.NUMBER,)
    return  input_montant



# ------- Regourpement des widget par section -------
def contenu_widget(titre, liste_widget):
    contenu = ft.Column(controls=[*titre,ft.Column(controls=[*liste_widget],
                                                    spacing=10,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,),],
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,)
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
    bouton_retour_haut = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,  # flèche gauche
        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
        tooltip="Retour accueil",
        on_click=handler)

    container_retour_haut = ft.Container(
        content=ft.Row([bouton_retour_haut], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.all(0),        # plus aucun padding
        height=30,)
    
    return container_retour_haut


# ------- Bouton retour acceuil -------
def bout_ret_acceuil(couleur_bouton_fleche, handler = None):
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=handler)  # Redirection vers la page d'accueil
    

    container_bouton = ft.Container(content=bouton_retour,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.only(top=20, bottom=20))  # Espacement avant et après
    
    return container_bouton

