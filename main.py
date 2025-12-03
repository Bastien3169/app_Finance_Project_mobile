# Créer un venv : python3 -m venv .venv
# L’activer : "source .venv/bin/activate" ou "source venv/bin/activate"
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import os
import flet as ft

# Configurer matplotlib pour Android
os.environ['MPLCONFIGDIR'] = '/data/user/0/com.flet.flet_temp/cache/matplotlib'


from src.controllers.navigation import route_change
from src.models.users_db.models_db_users_test import AuthManager, ClientStorageWrapper 


# Instance globale d'AuthManager (une seule fois)
auth_manager = AuthManager()  


def main(page: ft.Page):  # “page: ft.Page“ = annotation de type (pour l'IDE / autocomplete)
    page.clean()  # Nettoie la page au démarrage
    page.title = "Finance facile"
    page.window.width = 360    # iPhone standard de référence
    page.window.height = 640   # iPhone standard de référence
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 10
    page.spacing = 5
    page.scroll = "auto"       # Permet le défilement si le contenu dépasse la hauteugit r
    page.theme_mode = ft.ThemeMode.DARK

    # 🔑 On branche le stockage client Flet dans l'AuthManager
    # (si ton AuthManager attend un paramètre "storage" ou "cookies", adapte ici)
    auth_manager.cookies = ClientStorageWrapper(page.client_storage)

    # 🔑 Vérifier la session au démarrage
    current_user = auth_manager.get_current_user()

    if current_user:
        # ✅ Session encore valide → on va sur la home
        page.route = "/"
    else:
        # ❌ Pas de session / session expirée → page d'authentification
        page.route = "/auth_manag"

    # Fonction de callback pour le changement de route
    def on_route_change(e):
        # Si tu veux que route_change connaisse l'utilisateur courant,
        # tu peux lui passer current_user en paramètre
        route_change(page)

    page.on_route_change = on_route_change  # On attache le handler

    # Affichage initial
    route_change(page)


ft.app(target=main)

'''ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,  # ouvre dans le navigateur
    port=8550)                     # important : même port que dans l'email
'''
