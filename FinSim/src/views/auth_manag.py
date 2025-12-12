import flet as ft
from src.components.components_views import *
from src.services.auth_instance import auth_manager 

db_path = "users.db"

# Couleurs
couleur_titre_separateur = "#00B388"
couleur_bouton_fleche = "#21C4A0"

################################## CONNEXION ################################
def login_view(page: ft.Page):
    titre = titre_separateur("🔐 FinSim : Connexion requise", couleur_titre_separateur, padding_text_top = 45)
    email_field = periode_input(text_label="📧 Email", widths=400,)
    password_field = periode_input(text_label="🔒 Mot de passe", passwords=True, oeil=True, widths=400,)
    feedback = ft.Text("", color=ft.Colors.RED_300, size=12, visible=False, weight="bold", text_align=ft.TextAlign.CENTER,)

    def on_click_mdp_oublie(e):
        page.snack_bar = ft.SnackBar(ft.Text("Redirection vers la page de mot de passe oublié..."))
        page.snack_bar.open = True
        page.go("/mdp_oublie")
        page.update()

    # Checkbox "Rester connecté" en dehors de la Row pour récupération de sa valeur dans le handler
    stay_connected_checkbox_control = ft.Checkbox(value=False,
                                                  fill_color=ft.Colors.BLACK,
                                                  check_color=couleur_titre_separateur,)
    
    # Row Checkbox pour personaliser l'alignement
    stay_connected_checkbox = ft.Row(controls=[stay_connected_checkbox_control,
                                               ft.Text("Rester connecté",size=9,)],
                                     alignment=ft.MainAxisAlignment.START,
                                     spacing=0,)
    
    # Row avec checkbox à gauche et "Mot de passe oublié" à droite
    staytune_resetMdP = ft.Row(controls=[stay_connected_checkbox,  # ← À gauche
                                        ft.Container(expand=True),  # ← Espace entre les deux
                                        ft.Text(spans=[ft.TextSpan("Mot de passe oublié ? ", ft.TextStyle(size=9)),
                                                       ft.TextSpan("Clique ici", ft.TextStyle(size=9, color=couleur_titre_separateur, weight=ft.FontWeight.BOLD), 
                                                                   on_click=on_click_mdp_oublie)],
                                                size=12)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                width=400)

    # --- Handler connexion CORRIGÉ ---
    def handle_login(e):
        email = email_field.value.lower()
        password = password_field.value
        stay_connected = stay_connected_checkbox_control.value  # ✅ Récupère l'état de la checkbox
        
        # Le login retourne maintenant 3 valeurs : success, message, role
        success, message, user_role = auth_manager.login(email, password, stay_connected)
        
        feedback.value = message
        feedback.visible = True
        page.update()
        
        if success:
            page.go("/")

    bout_connexion = bouton_on_click("Se connecter", on_click=handle_login, icon=ft.Icons.PERSON, couleur_bouton=couleur_titre_separateur,)

    def on_click_inscription(e):
        page.snack_bar = ft.SnackBar(ft.Text("Redirection vers la page d'inscription..."))
        page.snack_bar.open = True
        page.go("/inscription")
        page.update()

    inscription_text = ft.Text(
        spans=[
            ft.TextSpan("Pas encore inscrit ? "),
            ft.TextSpan("Clique ici", ft.TextStyle(color=couleur_titre_separateur, weight=ft.FontWeight.BOLD), on_click=on_click_inscription,),
        ],
        size=12,
    )

    form_column = ft.Column(
        controls=[email_field, password_field, staytune_resetMdP, feedback, bout_connexion, inscription_text,],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    contenu = contenu_widget(titre, [form_column])
    return contenu

################################### FONCTION PRINCIPALE ################################
def auth_manage_page(page: ft.Page):
    page.clean()
    page.title = "Authentification"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    vu_login = login_view(page)
    bouton_retour = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"),)

    page.add(vu_login, bouton_retour)