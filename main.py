# Créer un venv : python3 -m venv .venv
# L’activer : "source .venv/bin/activate" ou "source venv/bin/activate"
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import os
import flet as ft

# Configurer matplotlib pour Android pour ne qu'il créer son dossier de config dans un répertoire accessible en écriture
os.environ['MPLCONFIGDIR'] = '/data/user/0/com.flet.flet_temp/cache/matplotlib'

from src.controllers.navigation import route_change
from src.models.users_db.models_db_users_test import AuthManager, ClientStorageWrapper 
from src.services.auth_instance import auth_manager 


def main(page: ft.Page):
    page.clean()
    page.title = "Finance facile"
    page.window.width = 360
    page.window.height = 640
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 10
    page.spacing = 5
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.DARK

    # 🔑 IMPORTANT : Brancher les cookies
    auth_manager.cookies = ClientStorageWrapper(page.client_storage)

    # 🔑 Vérifier la session au démarrage
    current_user = auth_manager.get_current_user()
    
    if current_user:
        page.route = "/"
    else:
        page.route = "/auth_manag"

    def on_route_change(e):
        route_change(page)

    page.on_route_change = on_route_change
    route_change(page)

ft.app(target=main)

'''ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,  # ouvre dans le navigateur
    port=8550)                     # important : même port que dans l'email
'''
