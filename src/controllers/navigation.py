from src.views import home, indices #, stocks, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft

def route_change(page: "ft.Page"):
    page.clean()  # Nettoie la page avant d'afficher le nouveau contenu
    route = page.route

    if route == "/":
        home.main_page(page)
    elif route == "/indices":
        indices.main_page(page)
    else:
        page.add(ft.Text("Page not found"))    
        # Vous pouvez ajouter d'autres routes ici
        # elif route == "/stocks":
        #     stocks.main_page(page)
        # elif route == "/etfs":
        #     etfs.main_page(page)
        # elif route == "/cryptos":
        #     cryptos.main_page(page)
        # elif route == "/dca_vs_lp":
        #     dca_vs_lp.main_page(page)
        # elif route == "/maj_bd":  
        #     maj_bd.main_page(page)
        # else:
        #     page.add(ft.Text("Page not found"))
    page.update()  # Met à jour la page pour refléter les changements

# Page principale (accueil)
def main(page: ft.Page):
    page.route = "/"
    page.on_route_change = lambda e: route_change(page)  # garde juste cette petite lambda ici
    route_change(page)  # affichage initial
    page.update()

    