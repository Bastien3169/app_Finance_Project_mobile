import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
import flet as ft

# Couleurs
couleur_titre_separateur = ft.Colors.GREEN_200
couleur_bouton_fleche = ft.Colors.GREEN_700

################################## CONNEXION ################################
def login_view(page: ft.Page):

    # --- Titre ---
    text_rendement = ft.Text("🔐 Connexion requise", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=21)

    # --- Séparateur ---
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur), padding=ft.padding.only(bottom=15))

    # --- Email input ---
    email_field = ft.TextField(label="📧 Email", 
                            label_style=ft.TextStyle(size=12, italic=True),
                            width=400, 
                            border_radius=8,
                            border_color=ft.Colors.WHITE30,)

    # --- mdp input ---
    password_field = ft.TextField(label="🔒 Mot de passe", 
                                password=True, 
                                label_style=ft.TextStyle(size=12, italic=True),
                                width=400, 
                                border_radius=8,
                                border_color=ft.Colors.WHITE30,)

    # --- feedback si connectio réussie ou pas ---
    feedback = ft.Text("", color=ft.Colors.RED_300)


    # --- Handler feedback ---
    def handle_login(e):
        if email_field.value == "test@test.com" and password_field.value == "1234":
            feedback.value = "✅ Connexion réussie"
            page.update()
        else:
            feedback.value = "❌ Identifiants incorrects"
            page.update()


    # --- Bouton connexion avec son handler ---
    bout_connexion = ft.ElevatedButton("Se connecter",
                                        height=40,
                                        width=400,
                                        icon=ft.Icons.PERSON,
                                        bgcolor=couleur_titre_separateur,
                                        color=ft.Colors.WHITE,
                                        on_click=handle_login,)
    
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
    return [text_rendement, separation, email_field, password_field, bout_connexion, feedback, inscription_text]
    
################################### FONCTION PRINCIPALE ################################

def auth_manage_page(page: ft.Page):
    page.clean()
    page.title = "DCA vs LS"
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
        *vu_login,
        container_bouton)
