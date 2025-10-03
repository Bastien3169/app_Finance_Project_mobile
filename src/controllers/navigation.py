from src.views import home, indices #, stocks, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft

from src.views import home, indices, test #, stocks, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft

def route_change(page: ft.Page):  # Pas besoin de guillemets
    """Gère les changements de route de l'application"""
    page.clean()  # Nettoie la page avant d'afficher le nouveau contenu
    route = page.route

    if route == "/":
        home.main_page(page)
    elif route == "/indices":
        indices.indices_page(page)
    elif route == "/stocks":
        # stocks.main_page(page)
        page.add(ft.Text("Page Stocks - En construction"))
    elif route == "/etfs":
        # etfs.main_page(page)
        page.add(ft.Text("Page ETFs - En construction"))
    elif route == "/cryptos":
        # cryptos.main_page(page)
        page.add(ft.Text("Page Cryptos - En construction"))
    elif route == "/dca_vs_lp":
        # dca_vs_lp.main_page(page)
        page.add(ft.Text("Page DCA vs LP - En construction"))
    elif route == "/maj_bd":  
        # maj_bd.main_page(page)
        page.add(ft.Text("Page MAJ BD - En construction"))
    elif route == "/test": 
        # maj_bd.main_page(page)
        test.indices_page(page) 
    else:
        page.add(ft.Text("❌ Page introuvable", size=20))
    
    page.update()  # Met à jour la page pour refléter les changements