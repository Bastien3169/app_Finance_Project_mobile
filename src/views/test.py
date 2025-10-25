# src/views/admin_flet.py
import flet as ft
from src.models.users_db.models_db_users import AuthManager, AdminManager
from src.models.datas_db.main_db_datas import *  # si besoin pour updates DB


auth_manager = AuthManager()  # Instanciation de la classe AuthManager
admin_manager = AdminManager()  # Instanciation de la classe AdminManager

couleur_titre_separateur = ft.Colors.CYAN_200
couleur_bouton_fleche = ft.Colors.CYAN_700
titre_size = 20

################################## MAJ BDD ##################################

def data_maj():
    # Widget : titre
    text_graphique = ft.Text("🔄 Mise à jours BDD datas", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=titre_size)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur),padding=ft.padding.only(bottom=15))
    
    text_info = ft.Text("La mise à jour peut prendre entre 20 et 30 minutes", size=15)

   # ---------------- Bouton maj ---------------- #
    bouton_maj = ft.ElevatedButton(
        "Cliquez ici pour mettre à jour la BDD datas",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: print("test")  # Redirection vers la page d'accueil
    )

    # Container pour centrer le bouton retourmaj
    container_bouton_maj = ft.Container(
        content=bouton_maj,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20)  # Espacement avant et après
    )

    maj_bdd = [text_graphique, separation, text_info, container_bouton_maj]

    return maj_bdd



################################## TABLEAU ADMIN ##################################

def users_maj():
    # Widget : titre
    text_graphique = ft.Text("📝 Modifications BDD users", color=couleur_titre_separateur, weight=ft.FontWeight.BOLD, size=titre_size)

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur),padding=ft.padding.only(bottom=15))
    
    text_info = ft.Text("Rechercher un utilisateur par email ou username", size=15)

    user_maj = [text_graphique, separation, text_info]

    return user_maj


########################################################## FONCTION PRINCIPALE ########################################################## 

def admin_flet(page: ft.Page):
    page.title = "🏛️ Administration"
    page.scroll = "adaptive"


# ------------------- Mise en place des fonctions ------------------ #
    maj_bdd = data_maj()
    user_maj = users_maj()

 # -----------Flèche retour en haut à droite----------- #
    # Flèche retour en haut à droite
    fleche_retour_haut = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,  # flèche gauche
        icon_color=couleur_bouton_fleche,  # même couleur que le bouton accueil
        tooltip="Retour accueil",
        on_click=lambda e: page.go("/")
    )

    # Container pour aligner à gauche la flèche retour
    container_retour_haut = ft.Container(
        content=ft.Row([fleche_retour_haut], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.all(0),        # plus aucun padding
        height=30, 
    )

    # ---------------- Bouton Retour accueil ---------------- #
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME, # ajoute icône à gauche du texte
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=couleur_bouton_fleche,
            padding=ft.padding.symmetric(horizontal=20, vertical=15)
        ),
        on_click=lambda e: page.go("/")  # Redirection vers la page d'accueil
    )

    # Container pour centrer le bouton retour
    container_bouton = ft.Container(
        content=bouton_retour,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=30, bottom=20)  # Espacement avant et après
    )

    # ------------------- Ajout des éléments à la page ------------------ #
    page.add(container_retour_haut, *maj_bdd, *user_maj, container_bouton)

