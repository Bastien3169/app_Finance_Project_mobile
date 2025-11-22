import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.components.components_views import *
from src.views import inscription
import flet as ft

db_path = "users.db"

# Couleurs
couleur_titre_separateur = ft.Colors.GREEN_200
couleur_bouton_fleche = ft.Colors.GREEN_700

################################## CONNEXION ################################


def login_view(page: ft.Page):

    # --- Titre + séparation ---
    titre = titre_separateur("🔐 Connexion requise",
                             couleur_titre_separateur)

    # --- Email input ---
    email_field = periode_input(text_label="📧 Email", hint_texte=None, hint_styl=None,
                                passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None)

    # --- mdp input ---
    password_field = periode_input(text_label="🔒 Mot de passe", hint_texte=None,
                                   hint_styl=None, passwords=True, oeil=True, widths=400, fonc_ajouter_periode=None)

    # --- feedback si connectio réussie ou pas ---
    feedback = ft.Text("", color=ft.Colors.RED_300, size=12,
                       weight="bold", text_align=ft.TextAlign.CENTER)

    # --- Handler feedback ---
    def handle_login(e):
        email = email_field.value
        password = password_field.value

        auth = AuthManager(db_path)  # chemin correct vers ta BDD
        # utilise la méthode login de AuthManager
        success, message = auth.login(email, password)

        feedback.value = message
        page.update()

        if success:
            page.go("/")  # Redirection vers la page home

    # --- Handler mdp oublié --

    def on_click_mdp_oublie(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Redirection vers la page de mot de passe oublié..."))
        page.snack_bar.open = True
        page.go("/mdp_oublie")   # ⬅️ redirection vers la route /mdp_oublie
        page.update()

  # --- Mdp oublié ---
    mdp_reset = ft.Row(controls=[ft.Text(spans=[ft.TextSpan("Mot de passe oublié ? ",
                                                            ft.TextStyle(size=9),),
                                                ft.TextSpan("Clique ici",
                                                            ft.TextStyle(size=9,
                                                                         color=couleur_titre_separateur,
                                                                         weight=ft.FontWeight.BOLD,),
                                                            on_click=on_click_mdp_oublie,),])],
                       alignment=ft.MainAxisAlignment.END)

    # --- Bouton connexion avec son handler ---
    bout_connexion = bouton_on_click(
        "Se connecter", on_click=handle_login, icon=ft.Icons.PERSON, couleur_bouton=couleur_titre_separateur)

    # --- Handler inscription --
    def on_click_inscription(e):
        page.snack_bar = ft.SnackBar(
            ft.Text("Redirection vers la page d'inscription..."))
        page.snack_bar.open = True
        page.go("/inscription")   # ⬅️ redirection vers la route /inscription
        page.update()

    # --- Bouton inscription (avec son handler) ---
    inscription_text = ft.Text(spans=[ft.TextSpan("Pas encore inscrit ? "),
                                      ft.TextSpan("Clique ici",
                                                  ft.TextStyle(color=couleur_titre_separateur,
                                                               weight=ft.FontWeight.BOLD,),
                                                  on_click=on_click_inscription,),])

    contenu = contenu_widget(titre, [
                             email_field, password_field, mdp_reset, bout_connexion, feedback, inscription_text])

    return contenu

################################### FONCTION PRINCIPALE ################################


def auth_manage_page(page: ft.Page):
    page.clean()
    page.title = "Authentification"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Récupère tous les éléments
    vu_login = login_view(page)

    # Bouton Retour accueil
    bouton_retour = bout_ret_acceuil(
        couleur_bouton_fleche, handler=lambda e: page.go("/"))

    page.add(
        vu_login,
        bouton_retour)
