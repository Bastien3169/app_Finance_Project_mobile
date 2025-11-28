import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.components.components_views import *
from src.views import inscription  
import flet as ft

db_path="users.db"

# Couleurs
couleur_titre_separateur = "#D67C7C"
couleur_bouton = "#E89292"
couleur_bouton_fleche = "#E89292"


################################## CONNEXION ################################
def mdp_oublie_view(page: ft.Page):

    auth = AuthManager(db_path=db_path)

    # --- Titre + séparation ---
    titre = titre_separateur("🔑 Réinitialisation mdp",couleur_titre_separateur)

    # --- Champ email ---
    email_field = periode_input(text_label="📧 Email", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None,)


    # --- Petit texte d'info / feedback ---
    feedback = ft.Text("", size=12, text_align=ft.TextAlign.CENTER, weight="bold", visible=False)

    # --- Handler bouton envoie lien mdp --- 
    def on_click_envoie_mdp(e):
        email = email_field.value.strip()

        if not email:
            feedback.value = "❌ Merci de renseigner votre email."
            feedback.color = ft.Colors.RED_300
            feedback.visible = True
            page.update()
            return

        success, message = auth.forgot_password(email)

        feedback.value = message
        feedback.color = ft.Colors.GREEN_300 if success else ft.Colors.RED_300
        feedback.visible = True
        page.update()


    # --- Bouton envoie lien ---
    bout_envoie = bouton_on_click ("Envoyer mail réinitialisation", on_click=on_click_envoie_mdp, icon=ft.Icons.EMAIL, couleur_bouton=couleur_titre_separateur)


    contenu = contenu_widget(titre, [email_field, feedback, bout_envoie])

    return contenu
    
################################### FONCTION PRINCIPALE ################################

def mdp_oublie_page(page: ft.Page):
    page.clean()
    page.title = "Réinitialisation mdp"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Contenu principal
    vue_mdp = mdp_oublie_view(page)

    # Bouton Retour accueil
    bouton_retour = bout_ret_acceuil(couleur_bouton_fleche,handler=lambda e: page.go("/"),)

    # Ajout des widgets
    page.add(vue_mdp, bouton_retour,)