import json
import os
import secrets
import jwt
import datetime

class Authenticator:
    def __init__(self):
        self.users_authentification = self.extract_user_authentification()

    def extract_user_authentification(self):
        try:
            with open('server/DB_authentication.json', 'r') as file:
                data = json.load(file)
                users = data['users']
                users_authentification = {}
                for email, user_info in users.items():
                    users_authentification[email] = user_info['password']
        except FileNotFoundError as e:
            print(e)
        return users_authentification

    def extract_all_user_info(self):
        with open('server/DB_authentication.json', 'r') as file:
            data = json.load(file)
            return data['users']

    def token(self):
        secret_key = secrets.token_urlsafe(32)
        # Définir le contenu du token
        payload = {
            'username': 'test',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        # Création du token
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        return token