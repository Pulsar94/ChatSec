import hashlib
import json
import string
import random

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
        token = random.choice(string.ascii_letters)
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        half_token = hashed_token[:len(hashed_token) // 2]
        return half_token


