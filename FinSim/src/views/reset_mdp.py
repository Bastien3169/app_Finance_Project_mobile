import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.components.components_views import *
from src.views import inscription
import flet as ft

db_path = "users.db"

# Couleurs
couleur_titre_separateur = "#D67C7C"
couleur_bouton = "#E89292"
couleur_bouton_fleche = "#E89292"


################################## VUE RESET MDP ################################
def reset_password_view(page: ft.Page, token: str):

    auth = AuthManager(db_path=db_path)

    # --- Titre + séparation ---
    titre = titre_separateur("🔑 Réinitialisation du mot de passe", couleur_titre_separateur)

    # --- Champ mot de passe ---
    password_field = periode_input(
        text_label="🔒 Nouveau mot de passe",
        hint_texte=None,
        hint_styl=None,
        passwords=True,
        oeil=True,
        widths=400,
        fonc_ajouter_periode=None,
    )

    # --- Champ confirmation mot de passe ---
    confirm_password_field = periode_input(
        text_label="🔒 Confirmation du mot de passe",
        hint_texte=None,
        hint_styl=None,
        passwords=True,
        oeil=True,
        widths=400,
        fonc_ajouter_periode=None,
    )

    # --- Feedback (erreurs / succès) ---
    feedback = ft.Text("",
                        color=ft.Colors.RED_300,
                        size=12,
                        weight="bold",
                        text_align=ft.TextAlign.CENTER,
                        visible=False,)

    # --- Handler : validation du nouveau mdp ---
    def handle_reset_password(e):
        password = password_field.value.strip()
        confirm_password = confirm_password_field.value.strip()

        # Vérif basique champs vides
        if not password or not confirm_password:
            feedback.value = "❌ Merci de remplir tous les champs."
            feedback.color = ft.Colors.RED_300
            feedback.visible = True
            page.update()
            return

        # Vérif correspondance
        if password != confirm_password:
            feedback.value = "❌ Les mots de passe ne correspondent pas."
            feedback.color = ft.Colors.RED_300
            feedback.visible = True
            page.update()
            return

        # Appel à la méthode métier
        success, message = auth.reset_password_with_token(token, password)

        feedback.value = message
        feedback.color = ft.Colors.GREEN_300 if success else ft.Colors.RED_300
        feedback.visible = True
        page.update()

        if success:
            page.snack_bar = ft.SnackBar(
                ft.Text("✅ Mot de passe modifié avec succès !"))

            page.snack_bar.open = True
            page.update()

            # Redirection vers page de connexion / gestion auth
            page.go("/auth_manag")

    # --- Bouton Valider ---
    bouton_valider = bouton_on_click("Valider le nouveau mot de passe",
                                     on_click=handle_reset_password,
                                     icon=ft.Icons.LOCK_RESET,
                                     couleur_bouton=couleur_titre_separateur,)

    contenu = contenu_widget(titre, [password_field, confirm_password_field, bouton_valider, feedback,],)

    return contenu


################################### FONCTION PRINCIPALE ################################
def reset_mdp(page: ft.Page):
    page.clean()
    page.title = "Réinitialisation du mot de passe"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # ========= RÉCUPÉRATION DU TOKEN =========
    # CAS 1 : route du type "/reset_mdp/<token>"
    token = None
    if page.route:
        # ex: "/reset_mdp/abcdef"
        parts = page.route.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "reset_mdp":
            token = parts[1]

    # Si aucun token -> message d’erreur
    if not token:
        page.add(ft.Container(content=ft.Text("❌ Lien de réinitialisation invalide ou expiré.",
                                              size=14,
                                              weight="bold",
                                              color=ft.Colors.RED_300,
                                              text_align=ft.TextAlign.CENTER,),
                              padding=ft.padding.only(top=50)))

        # Bouton retour accueil / auth
        bouton_retour = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/auth_manag"),)

        page.add(bouton_retour)
        return

    # ========= CONTENU PRINCIPAL =========
    vue_mdp = reset_password_view(page, token)

    # Bouton Retour accueil / gestion auth
    bouton_retour = bout_ret_acceuil(
        couleur_bouton_fleche, handler=lambda e: page.go("/auth_manag"),)

    page.add(vue_mdp, bouton_retour)
