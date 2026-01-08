from src.views import home, indices #, stocks, etfs, cryptos, dca_vs_lp, maj_bd
import flet as ft

from src.views import home, indices, stocks, ETFs, dca_vs_lp, cryptos, tous_actifs, admin, auth_manag, inscription, mdp_oublie, reset_mdp, test #, etfs, cryptos, dca_vs_lp, maj_bd
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
    elif route == "/ETFs":
        ETFs.etf_page(page)
    elif route == "/cryptos":
        cryptos.cryptos_page(page)
    elif route == "/tous_actifs":
        tous_actifs.actifs_page(page)
    elif route == "/dca_vs_lp":
        dca_vs_lp.dca_lp_page(page)
    elif route == "/admin":  
        admin.admin_flet(page)
    elif route == "/auth_manag":  
        auth_manag.auth_manage_page(page)
    elif route == "/inscription":  
        inscription.register_page(page)
    elif route == "/mdp_oublie":  
        mdp_oublie.mdp_oublie_page(page)
    elif route == "/reset_mdp":  
        reset_mdp.reset_mdp(page)
    elif route == "/test": 
        test.cryptos_page(page)
    else:
        page.add(ft.Text("❌ Page introuvable", size=20))
    
    page.update()  # Met à jour la page pour refléter les changements