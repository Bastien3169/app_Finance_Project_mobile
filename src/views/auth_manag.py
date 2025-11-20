import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.components.components_views import *
import flet as ft

db_path="users.db"

# Couleurs
couleur_titre_separateur = ft.Colors.GREEN_200
couleur_bouton_fleche = ft.Colors.GREEN_700

################################## CONNEXION ################################
def login_view(page: ft.Page):

    # --- Titre + séparation ---
    titre = titre_separateur("🔐 Connexion requise",couleur_titre_separateur, padding_text_top = 35)

    # --- Email input ---  
    email_field = periode_input(text_label="📧 Email", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None)

    # --- mdp input ---
    password_field = periode_input(text_label="🔒 Mot de passe", hint_texte=None, hint_styl=None, passwords=True, oeil=True, widths=400, fonc_ajouter_periode=None)

    # --- feedback si connectio réussie ou pas ---
    feedback = ft.Text("", color=ft.Colors.RED_300, size=12, weight="bold", text_align=ft.TextAlign.CENTER)

    # --- Handler feedback ---
    def handle_login(e):
        email = email_field.value
        password = password_field.value
        
        auth = AuthManager(db_path)  # chemin correct vers ta BDD
        success, message = auth.login(email, password)      # utilise la méthode login de AuthManager

        feedback.value = message
        page.update()

        if success:
            page.go("/")  # Redirection vers la page home

    # --- Bouton connexion avec son handler ---
    bout_connexion = bouton_on_click ("Se connecter", on_click=handle_login, icon=ft.Icons.PERSON, couleur_bouton=couleur_titre_separateur)
    
    # --- Handler inscription -- 
    def on_click_inscription(e):
        page.snack_bar = ft.SnackBar(ft.Text("Redirection vers la page d'inscription..."))
        page.snack_bar.open = True
        page.update()

    # --- Bouton s'incrire avec son handler ---
    inscription_text = ft.Text(spans=[ft.TextSpan("Pas encore inscrit ? "),
                                      ft.TextSpan("Clique ici", 
                                                  ft.TextStyle(color=couleur_titre_separateur,
                                                               weight=ft.FontWeight.BOLD,),
                                                 on_click=on_click_inscription,),])

    #return ft.Column([text_rendement, separation, email_field, password_field, bout_connexion, feedback, inscription_text],horizontal_alignment=ft.CrossAxisAlignment.CENTER,)
    #return titre + [email_field, password_field, bout_connexion, feedback, inscription_text]

    contenu = contenu_widget(titre, [email_field, password_field, bout_connexion, feedback, inscription_text])

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


    # Bouton retour en haut à droite
    bouton_retour_haut = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,  # flèche gauche
        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
        tooltip="Retour accueil",
        on_click=lambda e: page.go("/"))

    container_retour_haut = ft.Container(
        content=ft.Row([bouton_retour_haut], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.all(0),        # plus aucun padding
        height=30,)


    # Bouton Retour accueil
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/"))  # Redirection vers la page d'accueil

    container_bouton = ft.Container(
        content=bouton_retour,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20))  # Espacement avant et après
    
    
    page.add(
        container_retour_haut,
        vu_login,
        container_bouton)
