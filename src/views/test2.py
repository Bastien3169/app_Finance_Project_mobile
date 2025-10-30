# src/views/admin_flet.py
import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.models.datas_db.main_db_datas import *  # Pour les updates BDD

# Instanciations
auth_manager = AuthManager()
admin_manager = AdminManager()

# Couleurs et tailles
couleur_titre = ft.Colors.CYAN_200
couleur_bouton = ft.Colors.CYAN_600
taille_titre = 20


############################### FONCTIONS POUR LES TITRES ##############################

def data_maj_widgets():
    titre = ft.Text("🔄 Mise à jour BDD datas", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    return [titre, separation]

def users_maj_widgets():
    titre = ft.Text("📝 Modifications BDD users", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    return [titre, separation]

############################## FONCTION INTERACTIVE MAJ BDD ##############################

def add_update_database(page: ft.Page, dossier_csv: str, csv_bdd: str, db_path: str):
    
    # Création de la colonne pour les messages de suivi d'avancement
    messages = ft.Column(spacing=5)
    
    def on_click(e):
        messages.controls.clear()
        messages.controls.append(ft.Text("⏳ Début des étapes de maj 1/6..."))
        progress_bar.value = 0.08
        loader.content.visible = True
        page.update()

        try:
            composition_indices.csv_indices(dossier_csv)
            messages.controls.append(ft.Text("✅ Étape 1/6 terminée - Scraping tickers et composition indices"))
            progress_bar.value = 0.17
            page.update()

            infos_stocks.infos_stocks(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 2/6 terminée - Infos entreprises"))
            progress_bar.value = 0.34
            page.update()

            infos_indices.infos_indices(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 3/6 terminée - Infos indices"))
            progress_bar.value = 0.50
            page.update()

            hist_indices.recuperer_et_clean_indices(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 4/6 terminée - Historique indices"))
            progress_bar.value = 0.67
            page.update()

            hist_stocks.recuperer_et_clean_stocks(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 5/6 terminée - Historique entreprises"))
            progress_bar.value = 0.83
            page.update()

            sql_datas.main_creation_db(csv_bdd, db_path)
            messages.controls.append(ft.Text("✅ Étape 6/6 terminée - Base de données enregistrée"))
            progress_bar.value = 1.0
            page.update()

            loader.content.visible = False
            messages.controls.append(ft.Text("🎉 Base de données mise à jour avec succès !",weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN,size=10))
            page.update()

        except Exception as ex:
            loader.visible = False
            messages.controls.append(ft.Text(f"❌ Erreur : {ex}", color=ft.Colors.RED))
            progress_bar.value = 0
            page.update()
    
    # Création du bouton de mise à jour
    bouton = ft.ElevatedButton("Cliquez pour la maj de la BDD datas",
                               on_click=on_click,
                               style=ft.ButtonStyle(bgcolor=couleur_bouton, color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15)))
    
    # Création du texte info
    info = ft.Text("La maj peut prendre entre 20 et 30 min", size=10)

    # Création de la barre de progression stylée
    progress_bar = ft.Container(content=ft.ProgressBar(width=400, height=15, value=0, bgcolor=ft.Colors.GREY_800),
                                width=400,
                                height=15,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.CYAN_700),
                                border_radius=20,  # arrondi
                                padding=ft.padding.all(2),  # petit espace intérieur
                                border=ft.border.all(1, ft.Colors.CYAN_400),  # bord coloré
                                margin=ft.margin.only(top = 10, bottom=40),)

    # Création du conteneur loader
    loader = ft.Container(content=ft.ProgressRing(color=ft.Colors.CYAN_400, width=25, height=25),
                          padding=ft.padding.symmetric(vertical=15), 
                          alignment=ft.alignment.center,
                          visible=False,)
    

    return [bouton, info, loader, progress_bar, messages]


#################################### GESTION UTILISATEURS ####################################

def users_admin_flet(page: ft.Page):
    search_field = ft.TextField(label="🔍 Rechercher par email ou username", 
                                label_style=ft.TextStyle(size=12, italic=True),
                                width=400, 
                                border_color=ft.Colors.CYAN_400,)
    
    results_column = ft.Column(spacing=15)

    edit_state = {}

    def validate_search(e):
        results_column.controls.clear()
        search = search_field.value.strip()
        if not search:
            results_column.controls.append(ft.Text("❗ Veuillez entrer un nom ou email."))
            page.update()
            return

        user = admin_manager.get_user_by_email_username(search)
        if not user:
            results_column.controls.append(ft.Text("⚠️ Aucun utilisateur trouvé."))
            page.update()
            return

        id, username, email, role, registration_date = user

        headers = ["🆔 ID", "👤 Username", "📧 Email", "🔐 Rôle", "🗓️ Date", "🗑️ Supprimer", "✏️ Modifier"]
        header_row = ft.Column(
            [ft.Text(h, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD) for h in headers],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        results_column.controls.append(header_row)

        row = ft.Column(
            [
                ft.Text(str(id)),
                ft.Text(username),
                ft.Text(email),
                ft.Text(role),
                ft.Text(str(registration_date)),
                ft.ElevatedButton("Supprimer", bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE,
                                  on_click=lambda ev, em=email, un=username: delete_user(ev, em, un)),
                ft.ElevatedButton("Modifier", bgcolor=ft.Colors.CYAN_600, color=ft.Colors.WHITE,
                                  on_click=lambda ev, em=email: toggle_edit(ev, em)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        results_column.controls.append(row)

        if edit_state.get(email, False):
            results_column.controls.append(edit_form(user))

        page.update()

    def delete_user(e, email, username):
        admin_manager.delete_user(email)
        results_column.controls.append(ft.Text(f"✅ Utilisateur {username} supprimé."))
        page.update()

    def toggle_edit(e, email):
        edit_state[email] = not edit_state.get(email, False)
        validate_search(None)

    def edit_form(user):
        id, username, email, role, registration_date = user
        new_username = ft.TextField(label="Nouveau nom d'utilisateur", value=username, width=300)
        new_role = ft.Dropdown(
            label="Nouveau rôle",
            options=[ft.dropdown.Option("admin"), ft.dropdown.Option("user")],
            value=role,
            width=200,
        )
        new_password = ft.TextField(label="Nouveau mot de passe", password=True, can_reveal_password=True)

        def reset_password(e):
            if not new_password.value:
                results_column.controls.append(ft.Text("⚠️ Entrez un mot de passe."))
            else:
                admin_manager.update_user(email=email, password=new_password.value)
                results_column.controls.append(ft.Text(f"🔑 Mot de passe de {username} réinitialisé."))
            page.update()

        def submit_changes(e):
            admin_manager.update_user(email=email, username=new_username.value, role=new_role.value)
            results_column.controls.append(ft.Text(f"✅ Utilisateur {new_username.value} modifié avec succès."))
            edit_state[email] = False
            page.update()

        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.CYAN_100),
            padding=20,
            content=ft.Column(
                [
                    ft.Text("✏️ Modification de l'utilisateur", weight=ft.FontWeight.BOLD),
                    new_username,
                    new_role,
                    ft.Row(
                        [
                            ft.ElevatedButton("Réinitialiser le mot de passe", on_click=reset_password),
                            new_password,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.ElevatedButton(
                        "Valider les modifications",
                        bgcolor=ft.Colors.CYAN_600,
                        color=ft.Colors.WHITE,
                        on_click=submit_changes,
                    ),
                ],
                spacing=10,
            ),
        )

    # Création du bouton valider
    validate_button = ft.ElevatedButton("Valider la recherche",
                                        icon=ft.Icons.SEARCH,
                                        bgcolor=ft.Colors.CYAN_700,
                                        color=ft.Colors.WHITE,
                                        on_click=validate_search,)


    return ft.Column(
    [
        ft.Column([search_field, validate_button], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        results_column,
    ],
    spacing=20,
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
)


#################################### PAGE ADMIN PRINCIPALE ####################################

def admin_flet(page: ft.Page):
    page.title = "🏛️ Administration"
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Création flèche retour
    fleche_retour = ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                  icon_color=ft.Colors.CYAN_900,
                                  tooltip="Retour accueil",
                                  on_click=lambda e: page.go("/"))

    container_fleche = ft.Container(content=ft.Row([fleche_retour], alignment=ft.MainAxisAlignment.START), height=30)


    # Section mise à jour BDD
    widget_datas_bdd = data_maj_widgets()
    maj_datas_bdd = add_update_database(page, dossier_csv="csv", csv_bdd="csv/csv_bdd", db_path="datas.bd")


    # Section gestion utilisateurs
    widget_users_bdd = users_maj_widgets()
    maj_userss_bdd = users_admin_flet(page)


    # Création bouton retour accueil
    bouton_retour = ft.ElevatedButton("Retour accueil",
                                      icon=ft.Icons.HOME,
                                      bgcolor=ft.Colors.CYAN_900,
                                      style=ft.ButtonStyle(color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15)),
                                      on_click=lambda e: page.go("/"))

    container_bouton = ft.Container(content=bouton_retour,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.only(top=30, bottom=20),)


    # Ajout de tout à la page
    page.add(container_fleche, *widget_datas_bdd, *maj_datas_bdd, *widget_users_bdd, maj_userss_bdd, container_bouton)
