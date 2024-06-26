import json_handler as jh
import json


class Authenticator:
    def __init__(self):
        self.users_authentification = self.extract_user_authentification()

    def extract_user_authentification(self):
        with open('DB_authentication.json', 'r') as file:
            data = json.load(file)
            users = data['users']
            users_authentification = {}
            for email, user_info in users.items():
                users_authentification[email] = user_info['password']
        return users_authentification

    def extract_all_user_info(self):
        with open('DB_authentication.json', 'r') as file:
            data = json.load(file)
            return data['users']
