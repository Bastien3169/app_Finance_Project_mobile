# Créer un venv : python3 -m venv .venv
# L’activer : source .venv/bin/activate
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import flet as ft
from src.controllers.navigation import route_change

def main(page: ft.Page): # “page: ft.Page“ est une annotation de type. Sert juste pour annotation et autocomplétion.
    page.clean()  # Nettoie la page au démarrage
    page.title = "Finance facile"
    page.window.width = 360   # iPhone standard de référence
    page.window.height = 640  # iPhone standard de référence
    page.window_resizable = False
    page.padding = 10
    page.spacing = 5
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"  # Permet le défilement si le contenu dépasse la hauteur de la fenêtre
    page.route = "/" # Définir la route initiale

    # Fonction de callback pour le changement de route
    def on_route_change(e):
        route_change(page) # On passe bien la page à route_change, pas l'événement
    page.on_route_change = on_route_change # On attache le handler
 
    route_change(page) # Affichage initial

    # page.on_route_change = lambda e: route_change(page) # Alternative avec lambda pour passer la page à route_change
    
ft.app(target=main) 

