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

    # dict-like getitem
    def __getitem__(self, key):
        try:
            return self.storage.get(key)
        except Exception:
            return None

    # dict-like setitem
    def __setitem__(self, key, value):
        try:
            # stockage persistant côté client
            self.storage.set(key, value)
        except Exception:
            pass

    # dict-like delitem
    def __delitem__(self, key):
        try:
            self.storage.remove(key)
        except Exception:
            pass

    # méthode get (comme avant)
    def get(self, key, default=None):
        try:
            val = self.storage.get(key)
            return default if val is None else val
        except Exception:
            return default

    # méthode set (comme avant)
    def set(self, key, value):
        try:
            self.storage.set(key, value)
        except Exception:
            pass

    # méthode remove (comme avant)
    def remove(self, key):
        try:
            self.storage.remove(key)
        except Exception:
            pass

    # save() pour compatibilité avec ton ancien code ; page.client_storage n'a pas besoin d'un commit,
    # on met un no-op pour éviter les appels à .save() qui cassent.
    def save(self):
        # page.client_storage est déjà persistant, donc pas d'action à faire
        return



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



# --------------------------- login ---------------------------#
    def login(self, email, password, stay_connected=False):  # ⬅️ Nouveau paramètre
        user_role = None
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute("SELECT id, password, role FROM users WHERE email = ?", (email,))
            user = c.fetchone()

            if not user:
                return False, "❌ Utilisateur non trouvé", None

            user_id, hashed, user_role = user 
            
            if not self.check_password(password, hashed):
                return False, "❌ Mot de passe incorrect", None

            # Créé le token unique
            session_id = str(uuid.uuid4())

            # Durée selon stay_connected
            if stay_connected:
                # Session longue : 30 jours
                expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Session courte : 1 jour
                expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

            # SUPPRIME toutes les anciennes sessions de cet utilisateur
            c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

            # INSÈRE la nouvelle session proprement
            c.execute(
                "INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
                (session_id, user_id, expires_at)
            )

            conn.commit()

        # Écriture côté client
        if self.cookies is not None:
            try:
                self.cookies[self.cookie_name] = session_id
                if hasattr(self.cookies, "save"):
                    self.cookies.save()
            except Exception:
                pass

        return True, "✅ Connexion réussie", user_role


# --------------------------- logout ---------------------------#
    def logout(self):
        # Si aucun système de cookies n'est branché, on considère qu'il n'y a pas de session
        if self.cookies is None:
            return

        # Cherche si l’utilisateur a un cookie de session
        try:
            session_id = None
            # prend en charge les deux APIs : dict-like ou .get()
            if hasattr(self.cookies, "__getitem__"):
                session_id = self.cookies.get(self.cookie_name) if hasattr(self.cookies, "get") else self.cookies[self.cookie_name]
            else:
                session_id = self.cookies.get(self.cookie_name)
        except Exception:
            session_id = None

        # Si session_id existe, on efface de la bdd
        if session_id:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()

        # Supprime du stockage client (remove de préférence)
        try:
            if hasattr(self.cookies, "remove"):
                self.cookies.remove(self.cookie_name)
            elif hasattr(self.cookies, "__delitem__"):
                del self.cookies[self.cookie_name]
            # compat save no-op
            if hasattr(self.cookies, "save"):
                self.cookies.save()
        except Exception:
            pass


# --------------------------- get_current_user ---------------------------#
    def get_current_user(self):
        if self.cookies is None:
            return None

        # Obtenir session id depuis le wrapper (supporte .get() ou dict-like)
        try:
            if hasattr(self.cookies, "get"):
                session_id = self.cookies.get(self.cookie_name)
            else:
                session_id = self.cookies[self.cookie_name]
        except Exception:
            session_id = None

        if not session_id:
            return None

        date_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''SELECT u.id, u.username, u.email, u.role
                        FROM users u
                        JOIN sessions s ON u.id = s.user_id
                        WHERE s.session_id = ? AND s.expires_at > ?''', (session_id, date_now))
            user_session = c.fetchone()

        if user_session:
            return {"id": user_session[0], "username": user_session[1], "email": user_session[2], "role": user_session[3]}

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


#--------------------------- mdp oublié : vérifier token + changer mdp ---------------------------#   
    def reset_password_with_token(self, token, new_password):
        
        # Vérifier le format du mot de passe (même règle que register)
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, new_password):
            return False, "❌ Mot de passe trop faible. Il doit contenir au moins 5 caractères, 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial."

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()

            # 1. Vérifier que le token existe et n'est pas expiré
            c.execute("""SELECT pr.user_id FROM password_resets pr WHERE pr.token = ? AND pr.expires_at > ?""",(token, now))
            row = c.fetchone()

            if not row:
                return False, "❌ Lien de réinitialisation invalide ou expiré."

            user_id = row[0]

            # 2. Mettre à jour le mot de passe de l'utilisateur
            hashed = self.hash_password(new_password)
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))

            # 3. (Optionnel mais conseillé) supprimer tous les tokens pour cet utilisateur
            c.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))

            conn.commit()

        return True, "✅ Mot de passe réinitialisé avec succès."




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
