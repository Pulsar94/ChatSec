import server.rooms as rooms
import shared.json_handler as jh
import threading as thread
import os
import base64
import server.authenticator as authenticator
import time
import json

class func:
    def __init__(self, server):
        self.pem_file = []
        self.token = []
        self.server = server
        self.rooms = server.rooms
        self.port = 5000
        self.users_authentification = authenticator.Authenticator().users_authentification
        self.users_info = authenticator.Authenticator().extract_all_user_info()
        self.tag = {
            "authentification": self.authentification,
            "add_user": self.add_user,
            "create_room": self.create_room,
            "connect_room": self.connect_room,
            "room_disconnect": self.handle_room_disconnect,
            "debug": self.debug,
        }
        self.tag_unencrypted = {
            "need_pem": self.need_pem,
            "get_pem_start": self.get_pem_start,
            "get_pem": self.get_pem,
            "get_pem_end": self.get_pem_end,
        }

    def create_room(self, data, socket):
        # Check if the token is valid
        if data["data"]["token"] not in self.token:
            client_data = jh.json_encode("action_impossible_authentication_failed", "")
            socket.send(client_data.encode())
            return

        self.port += 1
        room = rooms.Room(data["data"]["room"], self.port, data["data"]["password"])
        if self.rooms.add_room(room):
            self.server.send_pem(socket, room.name+"-cert")
            client_data = jh.json_encode("connect_room", {"name":room.name, "port":room.port})
        else:
            client_data = jh.json_encode('room_already_created', room.name)
        self.server.send(socket, client_data)

    def connect_room(self, data, socket):
        # Check if the token is valid
        if data["data"]["token"] not in self.token:
            client_data = jh.json_encode("action_impossible_authentication_failed", "")
            socket.send(client_data.encode())
            return

        print("Connecting to room")
        room = self.rooms.get_room(data["data"]["room"])
        passw = data["data"]["password"]
        client_data = ""
        if room:
            if room.password and room.password != passw and passw != "":
                client_data = jh.json_encode("room_wrong_password", "")
            else:
                self.server.send_pem(socket, room.name+"-cert")
                client_data = jh.json_encode("connect_room", {"name":room.name, "port":room.port})
        else:
            client_data = jh.json_encode("room_not_found", "")
        self.server.send(socket, client_data)

    def handle_room_disconnect(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        client_data = ""
        if room:
            client_data = jh.json_encode("room_disconnected", "")
            if room.remove_guest(socket.getpeername()):
                self.rooms.del_room(room)
        else:
            client_data = jh.json_encode("room_not_found", "")
        self.server.send(client_data)
    
    def need_pem(self, data, socket):
        filename = "server-pub-key"
        self.server.send_pem(socket, filename)
    
    def get_pem_start(self, data, socket):
        self.pem_file = []

    def get_pem(self, data, socket):
        self.pem_file.append(data["data"]["file"])

    def get_pem_end(self, data, socket):
        os.makedirs("key-server", exist_ok=True)
        with open("key-server/"+str(socket.getpeername()[0])+"-pub-key.pem", 'wb') as file:
            for seg in self.pem_file:
                file.write(base64.b64decode(seg))
        self.pem_file = []
    
    def debug(self, data, socket):
        print("Debug: ", data["data"])
        client_data = jh.json_encode("debug", "hello")
        self.server.send(socket, client_data)

    def authentification(self, data, socket):
        """
        This function is used to authenticate a user
        :param data:
        :param socket:
        :return:
        """
        path = "Logs"
        # Check if the directory exists
        if not os.path.exists(path):
            os.makedirs(path)
        # Check if the user exists
        if data["data"]["username"] in self.users_authentification:
            # Check if the password is correct
            if self.users_authentification[data["data"]["username"]] == data["data"]["password"]:
                # Send a message to the client that the authentication was successful
                token = authenticator.Authenticator().token()
                self.token.append(token)
                client_data = jh.json_encode("authenticated", {"token": token})
                self.server.send(socket, client_data)
                # Log the connection
                try:
                    with open('Logs/connection.log', 'a') as file:
                        file.write(
                            f"{time.asctime()} - {data['data']['username']} connected from IP {socket.getpeername()[0]}\n")

                except IOError as e:
                    print(e)
            else:
                # Send a message to the client that the authentication failed
                client_data = jh.json_encode("authentication_failed", "")
                self.server.send(socket, client_data)
                # Log the failed connection
                try:
                    with open('Logs/connection.log', 'a') as file:
                        file.write(
                            f"{time.asctime()} - {data['data']['username']} failed to connect from IP {socket.getpeername()[0]}\n")
                except IOError as e:
                    print(e)
        else:
            # Send a message to the client that the authentication failed
            client_data = jh.json_encode("authentication_failed", "")
            self.server.send(socket, client_data)
            # Log the failed connection
            try:
                with open('Logs/connection.log', 'a') as file:
                    file.write(
                        f"{time.asctime()} - {data['data']['username']} user doesn't exist. Attempted connection from IP {socket.getpeername()[0]}\n")
            except IOError as e:
                print(e)

    def add_user(self, data, socket):
        """
        This function is used to add a user to the database
        :param data:
        :param socket:
        :return: none
        """
        # Check if the user already exists
        if data["data"]["username"] not in self.users_authentification:
            # Add the user to the database
            self.users_info[data["data"]["username"]] = {"password": data["data"]["password"]}
            self.users_info[data["data"]["username"]]["name"] = data["data"]["name"]
            # Save the new user to the database
            try:
                with open('server/DB_authentication.json', 'w') as file:
                    json.dump({'users': self.users_info}, file, sort_keys=True, indent=3, separators=(',', ': '))
            except IOError as e:
                print(e)
            # Update the users_authentification and user_info dictionary
            self.users_authentification = authenticator.Authenticator().users_authentification
            self.users_info = authenticator.Authenticator().extract_all_user_info()
            # Send a message to the client that the user was added
            client_data = jh.json_encode("user_added", "")
            self.server.send(socket, client_data)
            # Log the addition of the user
            try:
                with open('Logs/DB_actions.log', 'a') as file:
                    file.write(f"{time.asctime()} - {data['data']['username']} added to DB\n")
            except IOError as e:
                print(e)
        else:
            # Send a message to the client that the user already exists
            client_data = jh.json_encode("user_already_exists", "")
            self.server.send(socket, client_data)