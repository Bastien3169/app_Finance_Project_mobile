import flet as ft
from src.models.users_db.models_db_users_test import AuthManager
from src.components.components_views import *

db_path = "users.db"

# Couleurs
couleur_titre_separateur = "#00B388"
couleur_bouton_fleche = "#21C4A0"

################################## CONNEXION ################################
def login_view(page: ft.Page):

    # --- Titre + séparation ---
    titre = titre_separateur("🔐 Connexion requise", couleur_titre_separateur)

    # --- Email input ---
    email_field = periode_input(text_label="📧 Email", widths=400,)

    # --- Password input ---
    password_field = periode_input(text_label="🔒 Mot de passe", passwords=True, oeil=True, widths=400,)

    # --- Feedback texte ---
    feedback = ft.Text("", color=ft.Colors.RED_300, size=12, visible=False, weight="bold",text_align=ft.TextAlign.CENTER,)

    # --- mdp oublié ---
    def on_click_mdp_oublie(e):
        page.snack_bar = ft.SnackBar(ft.Text("Redirection vers la page de mot de passe oublié..."))
        page.snack_bar.open = True
        page.go("/mdp_oublie")
        page.update()

    mdp_reset = ft.Row(controls=[ft.Text(spans=[ft.TextSpan("Mot de passe oublié ? ", ft.TextStyle(size=9)),
                                                ft.TextSpan("Clique ici",ft.TextStyle(size=9, color=couleur_titre_separateur, weight=ft.FontWeight.BOLD), on_click=on_click_mdp_oublie)], 
                                        size=12)],
                        alignment=ft.MainAxisAlignment.END,  
                        width=400)

    # --- Handler connexion ---
    def handle_login(e):
        email = email_field.value
        password = password_field.value
        auth = AuthManager(db_path)
        success, message = auth.login(email, password)

        feedback.value = message
        feedback.visible = True
        page.update()

        if success:
            page.go("/")

    # --- Bouton connexion ---
    bout_connexion = bouton_on_click("Se connecter", on_click=handle_login, icon=ft.Icons.PERSON, couleur_bouton=couleur_titre_separateur,)

    # --- Handler inscription ---
    def on_click_inscription(e):
        page.snack_bar = ft.SnackBar(ft.Text("Redirection vers la page d'inscription..."))
        page.snack_bar.open = True
        page.go("/inscription")
        page.update()

    inscription_text = ft.Text(spans=[ft.TextSpan("Pas encore inscrit ? "),
                                      ft.TextSpan("Clique ici",ft.TextStyle(color=couleur_titre_separateur, weight=ft.FontWeight.BOLD),
                                                  on_click=on_click_inscription,),],
                                size=12,)

    # --- Regroupement des champs dans une colonne ---
    form_column = ft.Column(controls=[email_field, password_field, mdp_reset, feedback, bout_connexion, inscription_text,],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,)

    # --- Contenu final ---
    contenu = contenu_widget(titre, [form_column])

    return contenu

################################### FONCTION PRINCIPALE ################################
def auth_manage_page(page: ft.Page):
    page.clean()
    page.title = "Authentification"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Vue login
    vu_login = login_view(page)

    # Bouton Retour accueil
    bouton_retour = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"),)

    page.add(vu_login, bouton_retour)
