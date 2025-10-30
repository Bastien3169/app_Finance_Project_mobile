# src/views/admin_flet.py
import flet as ft
from src.models.users_db.models_db_users import AuthManager, AdminManager
from src.models.datas_db.main_db_datas import *  # Pour les updates BDD

# Instanciations
auth_manager = AuthManager()
admin_manager = AdminManager()

# Couleurs et tailles
couleur_titre = ft.Colors.CYAN_200
couleur_bouton = ft.Colors.CYAN_700
taille_titre = 20


############################### FONCTIONS WIDGETS STATIQUES ##############################

def data_maj_widgets():
    titre = ft.Text("🔄 Mise à jour BDD datas", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    info = ft.Text("La mise à jour peut prendre entre 20 et 30 minutes", size=15)
    return [titre, separation, info]

def users_maj_widgets():
    titre = ft.Text("📝 Modifications BDD users", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    info = ft.Text("Rechercher un utilisateur par email ou username", size=15)
    return [titre, separation, info]


############################## FONCTION INTERACTIVE MAJ BDD ##############################

def add_update_database(page: ft.Page, dossier_csv: str, csv_bdd: str, db_path: str):
    progress_bar = ft.ProgressBar(width=400, value=0)
    messages = ft.Column(spacing=5)

    def on_click(e):
        messages.controls.clear()
        progress_bar.value = 0
        page.update()

        # -------- Processus de mise à jour BDD -------- #
        try:
            # Étape 1/6
            composition_indices.csv_indices(dossier_csv)
            messages.controls.append(ft.Text("✅ Étape 1/6 terminée - Scraping tickers et composition indices"))
            progress_bar.value = 0.17
            page.update()  # ← Met à jour avec le ✅

            # Étape 2/6 
            infos_stocks.infos_stocks(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 2/6 terminée - Infos entreprises"))
            progress_bar.value = 0.34
            page.update()

            # Étape 3/6
            infos_indices.infos_indices(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 3/6 terminée - Infos indices"))
            progress_bar.value = 0.50
            page.update()

            # Étape 4/6     
            hist_indices.recuperer_et_clean_indices(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 4/6 terminée - Historique indices"))
            progress_bar.value = 0.67
            page.update()

            # Étape 5/6           
            hist_stocks.recuperer_et_clean_stocks(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 5/6 terminée - Historique entreprises"))
            progress_bar.value = 0.83
            page.update()

            # Étape 6/6
            sql_datas.main_creation_db(csv_bdd, db_path)
            messages.controls.append(ft.Text("✅ Étape 6/6 terminée - Base de données enregistrée"))
            progress_bar.value = 1.0
            page.update()

            # Message final
            messages.controls.append(ft.Text("🎉 Base de données mise à jour avec succès !",
                                             weight=ft.FontWeight.BOLD,
                                             color=ft.Colors.GREEN,
                                             size=10))
            page.update()

        except Exception as ex:
            messages.controls.append(ft.Text(f"❌ Erreur : {ex}", color=ft.Colors.RED))
            progress_bar.value = 0
            page.update()

    #-------------- Bouton de mise à jour ----------------#
    bouton = ft.ElevatedButton("Cliquez ici pour mettre à jour la base de données",
                               on_click=on_click,
                               style=ft.ButtonStyle(bgcolor=couleur_bouton, color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15))
                               )

    return [bouton, progress_bar, messages]


#################################### FONCTION PRINCIPALE ####################################

def admin_flet(page: ft.Page):
    page.title = "🏛️ Administration"
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Widgets statiques
    maj_bdd = data_maj_widgets()
    user_maj = users_maj_widgets()

    # Section interactive mise à jour BDD
    update_widgets = add_update_database(page, dossier_csv="csv", csv_bdd="csv/csv_bdd", db_path="datas.bd")


    # Flèche retour
    fleche_retour = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=couleur_bouton,
        tooltip="Retour accueil",
        on_click=lambda e: page.go("/")
    )
    container_fleche = ft.Container(content=ft.Row([fleche_retour], alignment=ft.MainAxisAlignment.START), height=30)

    # Bouton retour accueil
    bouton_retour = ft.ElevatedButton(
        "Retour accueil",
        icon=ft.Icons.HOME,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=couleur_bouton, padding=ft.padding.symmetric(20, 15)),
        on_click=lambda e: page.go("/")
    )
    container_bouton = ft.Container(content=bouton_retour, alignment=ft.alignment.center, padding=ft.padding.only(top=30, bottom=20))

    # Ajout de tous les éléments
    page.add(container_fleche, *maj_bdd, *update_widgets, *user_maj, container_bouton)
