# Créer un venv : python3 -m venv .venv
# L’activer : source .venv/bin/activate
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import flet as ft
from src.controllers.navigation import route_change

def main(page: ft.Page):
    # Définir la route initiale
    page.route = "/"

    # Fonction classique pour gérer le changement de route
    def on_route_change(event):
        route_change(page)

    page.on_route_change = on_route_change

    # Affichage initial
    route_change(page)

ft.app(target=main)
