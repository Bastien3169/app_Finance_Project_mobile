# La même que plus haut mais améliroré. Attention, unique sur username. Je suis pas d'accord c'est su le mail

import sqlite3
import bcrypt
import re
import uuid
import smtplib
from email.message import EmailMessage
import os
import secrets  # pour générer des tokens sécurisés
from datetime import datetime, timedelta, timezone
from src.services.envoie_mails import *
import flet as ft 


############################################# CLASS BDD USERS #############################################
class BaseDBManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()

            # Table users
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    registration_date TEXT NOT NULL
                )
            ''')

            # Table session
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            # Table password_resets
            c.execute('''
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            conn.commit()


################################ CLASS wrapper ClientStorage ################################
class ClientStorageWrapper:
    def __init__(self, storage):
        self.storage = storage

    # ⬇️ important : au début, pas de gestion réelle des cookies
    def get(self, key, default=None):
        try:
            return self.storage.get(key)
        except Exception:
            return default

    # ⬇️ important : au début, pas de gestion réelle des cookies
    def set(self, key, value):
        try:
            self.storage.set(key, value)
        except Exception:
            pass

    # ⬇️ important : au début, pas de gestion réelle des cookies
    def remove(self, key):
        try:
            self.storage.remove(key)
        except Exception:
            pass



################################ CLASS AUTHMANAGER AVEC HERITAGE DE class BaseDBManager ################################
class AuthManager(BaseDBManager):

    def __init__(self, db_path="users.db", cookie_name="session_id", cookie_secret="Toulouse31"):
        super().__init__(db_path)
        self.cookie_name = cookie_name
        self.cookie_secret = cookie_secret

        # ⬇️ important : au début, pas de gestion réelle des cookies
        self.cookies = None  

        self.init_db()
        self.clean_expired_sessions()


#--------------------------- méthode pour effacer les sessions exiprées de la bdd ---------------------------#
    def clean_expired_sessions(self):
        date_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (date_now,))
            conn.commit()

    
#--------------------------- Hachage mdp ---------------------------#
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')


#--------------------------- Vérification mdp au moment de la connexion ---------------------------#
    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))


#--------------------------- Enregistrement ---------------------------#
    def register(self, username, email, password):
        
        # Nettoyage basique du username
        username = username.strip()
        if not username:
            return False, "❌ Le nom d'utilisateur est obligatoire."

        # Validation de l'email via regex : structure mail valide
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(email_pattern, email):
            return False, "❌ Email invalide"
        
        # Validation mdp via regex : 5 caractères, majuscule, minuscule, chiffre, caractère spécial
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, password):
            return False, "❌ Mot de passe trop faible. Il doit contenir au moins 5 caractères, 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial."

        # Ouverture connexion (et fermeture automatique)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Vérifie si l'email existe déjà
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchone():
                return False, "❌ Email déjà utilisé"

            # Hachage mdp
            hashed = self.hash_password(password)

            # Insertion des infos users
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO users (username, email, password, role, registration_date) VALUES (?, ?, ?, ?, ?)",
                (username, email, hashed, 'user', date)
            )

            conn.commit()

        return True, f"✅ Compte '{username}' créé avec succès !"



#--------------------------- login ---------------------------#  
    def login(self, email, password):
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Cherche le users via le mail en fonction des id et password
            c.execute("SELECT id, password FROM users WHERE email = ?", (email,))
            # récupère via la variable user la ligne unique correspondante
            user = c.fetchone()

            # On vérifie si l'utilisateur existe dans bdd
            if not user:
                return False, "❌ Utilisateur non trouvé"
            # S'il existe on vérifie le mdp
            user_id, hashed = user # unpacking du tuple pris dans "user = c.fetchone()" ou hashed = user[1]
            if not self.check_password(password, hashed):
                return False, "❌ Mot de passe incorrect"

            # Si tout est ok, on créé la persistance de session
            # Créé le token unique
            session_id = str(uuid.uuid4())
            # Créé la date d'expiration du token
            expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S") 
            # Rentre ds la bdd les infos
            c.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
                      (session_id, user_id, expires_at))
            # Enregistre ds la bdd les infos
            conn.commit()


        # Si pas de gestion de cookies, on ne tente pas d'écrire dessus
        if self.cookies is not None:
            self.cookies[self.cookie_name] = session_id
            self.cookies.save()
        return True, "✅ Connexion réussie"


#--------------------------- logout ---------------------------#   
    def logout(self):

        # Si aucun système de cookies n'est branché, on considère qu'il n'y a pas de session
        if self.cookies is None:
            return
        
        # Cherche si l’utilisateur a un cookie de session
        session_id = self.cookies.get(self.cookie_name)
        
        # Si session_id existe, on efface de la bdd
        if session_id:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                
            #Vide le cookie
            self.cookies[self.cookie_name] = ""
            # Enregistre le cookie vide dans le navigateur
            self.cookies.save()

#--------------------------- Vérifie si cookie de session valide ---------------------------#   
    def get_current_user(self):
        
        # Si aucun système de cookies n'est branché, on considère qu'il n'y a pas de session
        if self.cookies is None:
            return None
        
        # récupère le cookie de session du navigateur
        session_id = self.cookies.get(self.cookie_name)

        # Si session-id vide ( "" ) pas connecté.
        if not session_id:
            return None
        
        date_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Si "session_id" existe, vérifie si "session_id" non expirée
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT u.id, u.username, u.email, u.role FROM users u JOIN sessions s ON u.id = s.user_id WHERE s.session_id = ? AND s.expires_at > ?''', (session_id, date_now))
            user_session = c.fetchone()

            # Si session_id valide on se connecte
            if user_session:
                # On pourrait return True mais ici on prend les infos afin de savoir qui est connecté et pourvoir s'en servir si on veut
                return {"id": user_session[0], "username": user_session[1], "email": user_session[2], "role": user_session[3]}
            else:
                return None


#--------------------------- mdp oublié : création du mdp tokenisé ---------------------------#   
    def create_password_reset_token(self, email):
        
        with sqlite3.connect(self.db_path) as conn:
            
            # Cherche l'utilisateur
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?", (email,)) 
            user = c.fetchone()
            if not user:
                return False, "❌ Aucun utilisateur trouvé avec cet email"
            user_id = user[0]

            # Génère un token aléatoire sécurisé
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            # Insère le token dans la table password_resets
            c.execute(
                "INSERT INTO password_resets (user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (user_id, token, expires_at, created_at))
            
            conn.commit()

        # Retourne le token (il servira dans le lien d'email)
        return True, token


#--------------------------- mdp oublié : envoie mail avec lien ---------------------------#   
    def forgot_password(self, email):
        # 1. On crée (ou pas) un token pour cet email
        success, result = self.create_password_reset_token(email)

        if not success:
            # result contient le message d’erreur (ex: "Aucun utilisateur trouvé")
            return False, result

        token = result  # ici, result = token si success == True

        # 2. On envoie le mail avec le lien
        envoie_password_reset_email(email, token)

        # 3. On répond à l'appelant (la view par ex.)
        return True, "✅ Email de réinitialisation envoyé !"




#########################################################################################################################
################################ CLASS ADMINMANAGER AVEC HERITAGE DE class BaseDBManager ################################

class AdminManager(BaseDBManager):
#--------------------------- Initialisation et et lancement de "super().init_db()" ---------------------------#
    def __init__(self, db_path="users.db"):
        super().__init__(db_path) # appelle init_db via la classe parente

   
#--------------------------- Hachage du mot de passe ---------------------------#
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')


#--------------------------- Afficher tous les utilisateurs ---------------------------#
    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users")
            return c.fetchall()

    
#--------------------------- Trouver un utilisateur par email/username ---------------------------#
    def get_user_by_email_username(self, search):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users WHERE email = ? OR username = ?", (search, search))
            return c.fetchone()  # Récupère l'utilisateur par son email

     
#--------------------------- Modifier un utilisateur ---------------------------#
    def update_user(self, email, username=None, password=None, role=None):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Requête de mise à jour pour un utilisateur en fonction de l'email
            fields = []
            values = []
    
            if username:
                fields.append("username = ?")
                values.append(username)
            if password:
                hashed = self.hash_password(password)
                fields.append("password = ?")
                values.append(hashed)
            if role:
                fields.append("role = ?")
                values.append(role)
    
            # Vérification si au moins un champ a été modifié
            if not fields:
                return "Aucune modification à effectuer."
    
            # Ajout de l'email pour effectuer la mise à jour sur l'utilisateur trouvé par email
            values.append(email)
            query = f"UPDATE users SET {', '.join(fields)} WHERE email = ?"
            c.execute(query, values)
            conn.commit()
            return f"✅ Utilisateur avec l'email '{email}' modifié avec succès."

    
#--------------------------- Supprimer un utilisateur ---------------------------#
    def delete_user(self, email):
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute("DELETE FROM users WHERE email = ?", (email,))
            
            conn.commit()
            return f"🗑️ Utilisateur avec email {email} supprimé."
