from src.views import home, indices #, stocks, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft

from src.views import home, indices, stocks, dca_vs_lp, cryptos, tous_actifs, admin, test, test2 #, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft



def route_change(page: ft.Page):  # Pas besoin de guillemets
    page.clean()  # Nettoie la page avant d'afficher le nouveau contenu
    route = page.route

    if route == "/":
        home.main_page(page)
    elif route == "/indices":
        indices.indices_page(page)
    elif route == "/stocks":
        stocks.stocks_page(page)
        # stocks.main_page(page)
    elif route == "/etfs":
        # etfs.main_page(page)
        page.add(ft.Text("Page ETFs - En construction"))
    elif route == "/cryptos":
        cryptos.cryptos_page(page)
    elif route == "/tous_actifs":
        tous_actifs.actifs_page(page)
    elif route == "/dca_vs_lp":
        dca_vs_lp.dca_lp_page(page)
    elif route == "/admin":  
        admin.admin_flet(page)
    elif route == "/test": 
        # maj_bd.main_page(page)
        test.admin_flet(page)
    elif route == "/test2":
        test2.admin_flet(page)
    else:
        page.add(ft.Text("❌ Page introuvable", size=20))
    
    page.update()  # Met à jour la page pour refléter les changements