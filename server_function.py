import rooms
import json_handler as jh
import authenticator
import hashlib
import time
import json

class func:
    def __init__(self):
        self.rooms = rooms.Rooms()
        self.users_authentification = authenticator.Authenticator().users_authentification
        self.users_info = authenticator.Authenticator().extract_all_user_info()
        self.tag = {
            "authentification": self.authentification,
            "add_user": self.add_user,
            "create_room": self.create_room,
            "connect_room": self.connect_room,
            "room_message": self.handle_room_message,
            "room_disconnect": self.handle_room_disconnect,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
        }

    def create_room(self, data, socket):
        room = rooms.Room(data["data"]["name"], data["data"]["password"])
        if self.rooms.add_room(room):
            room.add_guest(socket, socket.getpeername())
            client_data = jh.json_encode('room_created', room.name)
        else:
            client_data = jh.json_encode('room_already_created', room.name)
        socket.send(client_data.encode())

    def connect_room(self, data, socket):
        print("Connecting to room")
        room = self.rooms.get_room(data["data"]["name"])
        if room:
            if room.add_guest(socket, socket.getpeername()):
                client_data = jh.json_encode("room_already_connected", "")
            else:
                client_data = jh.json_encode("room_connected", "")
            socket.send(client_data.encode())
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def handle_room_message(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        if room:
            client_data = jh.json_encode("room_found", "")
            socket.send(client_data.encode())

            print("Adding message to ", room.name)
            room.add_message(data["data"]["message"], data["data"]["username"])
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def handle_room_disconnect(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        if room:
            client_data = jh.json_encode("room_disconnected", "")
            socket.send(client_data.encode())
            if room.remove_guest(socket.getpeername()):
                self.rooms.del_room(room)
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def room_file(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        if room:
            client_data = jh.json_encode("room_found", "")
            socket.send(client_data.encode())

            print("Adding file to ", room.name)
            room.add_file(data["data"]["file_name"])
            room.sender_socket = socket  # Keep track of the sender's socket
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def room_file_seg(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        if room:
            print("Adding file segment to ", room.name)
            room.add_file_seg(data["data"]["file_name"], data["data"]["file"])
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def room_file_seg_end(self, data, socket):
        room = self.rooms.get_room(data["data"]["room"])
        if room:
            print("File segment end received")
            for guest in room.get_guests():
                guest_socket = list(guest.values())[0]
                if guest_socket != room.sender_socket:  # Skip sending to the sender
                    guest_socket.send(jh.json_encode("room_file", {"file_name": data["data"]["file_name"]}).encode())
                    for seg in room.files[data["data"]["file_name"]]:
                        guest_socket.send(jh.json_encode("room_file_seg", {"file_name": data["data"]["file_name"], "file": seg}).encode())
                    guest_socket.send(jh.json_encode("room_file_seg_end", {"file_name": data["data"]["file_name"]}).encode())
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())

    def authentification(self, data, socket):
        """
        This function is used to authenticate a user
        :param data:
        :param socket:
        :return:
        """
        # Check if the user exists
        if data["data"]["username"] in self.users_authentification:
            # Check if the password is correct
            if self.users_authentification[data["data"]["username"]] == data["data"]["password"]:
                # Send a message to the client that the authentication was successful
                client_data = jh.json_encode("authenticated", "")
                socket.send(client_data.encode())
                # Log the connection
                try:
                    with open('./Logs/connection.log', 'a') as file:
                        file.write(f"{time.asctime()} - {data['data']['username']} connected from IP {socket.getpeername()[0]}\n")

                except IOError as e:
                    print(e)
            else:
                # Send a message to the client that the authentication failed
                client_data = jh.json_encode("authentication_failed", "")
                socket.send(client_data.encode())
                # Log the failed connection
                try:
                    with open('./Logs/connection.log', 'a') as file:
                        file.write(f"{time.asctime()} - {data['data']['username']} failed to connect from IP {socket.getpeername()[0]}\n")
                except IOError as e:
                    print(e)
        else:
            # Send a message to the client that the authentication failed
            client_data = jh.json_encode("authentication_failed", "")
            socket.send(client_data.encode())
            # Log the failed connection
            try:
                with open('./Logs/connection.log', 'a') as file:
                    file.write(f"{time.asctime()} - {data['data']['username']} user doesn't exist. Attempted connection from IP {socket.getpeername()[0]}\n")
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
                with open('DB_authentication.json', 'w') as file:
                    json.dump({'users': self.users_info}, file, sort_keys=True, indent=3, separators=(',', ': '))
            except IOError as e:
                print(e)
            # Update the users_authentification and user_info dictionary
            self.users_authentification = authenticator.Authenticator().users_authentification
            self.users_info = authenticator.Authenticator().extract_all_user_info()
            # Send a message to the client that the user was added
            client_data = jh.json_encode("user_added", "")
            socket.send(client_data.encode())
            # Log the addition of the user
            try:
                with open('./Logs/DB_actions.log', 'a') as file:
                    file.write(f"{time.asctime()} - {data['data']['username']} added to DB\n")
            except IOError as e:
                print(e)
        else:
            # Send a message to the client that the user already exists
            client_data = jh.json_encode("user_already_exists", "")
            socket.send(client_data.encode())