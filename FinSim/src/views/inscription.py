import flet as ft
from src.models.users_db.models_db_users_test import AuthManager
from src.components.components_views import *

db_path = "users.db"

# Couleurs
couleur_titre_separateur = "#D67C7C"
couleur_bouton = "#E89292"
couleur_bouton_fleche = "#E89292"


################################## INSCRIPTION ################################
def register_view(page: ft.Page):

    # --- Titre + séparation ---
    titre = titre_separateur("📝 Inscription", couleur_titre_separateur)

    # --- Champ pseudo / nom d'utilisateur ---
    username_field = periode_input(text_label="👤 Nom d'utilisateur", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None,)

    # --- Champ email ---
    email_field = periode_input(text_label="📧 Email", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None,)

    # --- Champ mot de passe ---
    password_field = periode_input( text_label="🔒 Mot de passe", hint_texte=None, hint_styl=None, passwords=True, oeil=True, widths=400, fonc_ajouter_periode=None, )

    # --- Champ confirmation mot de passe ---
    confirm_password_field = periode_input(text_label="🔒 Confirmation du mot de passe", hint_texte=None, hint_styl=None, passwords=True, oeil=True, widths=400, fonc_ajouter_periode=None,)

    # --- Feedback (erreurs / succès) ---
    feedback = ft.Text("", color=ft.Colors.RED_300, size=12, weight="bold", text_align=ft.TextAlign.CENTER, visible=False)

    # --- Handler inscription ---
    def handle_register(e):
        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value
        confirm_password = confirm_password_field.value

        # Vérif rapide côté front
        if not username or not email or not password or not confirm_password:
            feedback.value = "❌ Tous les champs sont obligatoires."
            feedback.visible = True
            page.update()
            return

        if password != confirm_password:
            feedback.value = "❌ Les mots de passe ne correspondent pas."
            feedback.visible = True
            page.update()
            return

        auth = AuthManager(db_path)
        success, message = auth.register(username, email, password)

        feedback.value = message
        feedback.color = ft.Colors.GREEN_300 if success else ft.Colors.RED_300
        feedback.visible = True
        page.update()

        if success:
            # Option : rediriger vers la page de connexion
            page.snack_bar = ft.SnackBar(ft.Text("Compte créé, vous pouvez vous connecter."))
            page.snack_bar.open = True
            page.go("/auth_manag")  # adapte selon ta route de connexion
            page.update()

    # --- Bouton s'inscrire ---
    bouton_inscription = bouton_on_click("Valider l'inscription",
                                        on_click=handle_register,
                                        icon=ft.Icons.HOW_TO_REG,
                                        couleur_bouton=couleur_titre_separateur,)

    contenu = contenu_widget(titre,[username_field, email_field, password_field, confirm_password_field, feedback, bouton_inscription,],)

    return contenu


################################### FONCTION PRINCIPALE ################################
def register_page(page: ft.Page):
    page.clean()
    page.title = "Inscription"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Vue principale
    vue_register = register_view(page)

    # Bouton Retour accueil
    bouton_retour = bout_ret_acceuil(
        couleur_bouton_fleche,
        handler=lambda e: page.go("/"),
    )

    page.add(
        vue_register,
        bouton_retour,
    )
