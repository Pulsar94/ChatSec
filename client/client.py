import socket
import ssl
import threading as thread
import shared.json_handler as jh
from client.client_function import func_room, func_server
import base64
import os
import hashlib
from time import sleep
from shared.rsa_handler import RSAHandler as rsa

CERT_FILE_CLIENT = "key-client/client-cert.pem"
KEY_FILE_CLIENT = "key-client/client-key.pem"
PUB_KEY_FILE_CLIENT = "key-client/client-pub-key.pem"

CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self, controller):
        self.contr = controller
        self.rsa = rsa(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS, PUB_KEY_FILE_CLIENT)
        self.server_key = None
        self.room_list = []
        
        self.ssl_room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.func_server = func_server(self)
        self.func_room = func_room(self)
        self.user_token = ""
        self.user_mdp = ""

    def sv_token(self, token):
        self.user_token = token

    def sv_connect(self, host, port):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
            self.server_socket.send(jh.json_encode("need_pem",{}).encode())
        except:
            print("Connection failed")

    def rm_connect(self, host, port, name):
        self.room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations("key-client/"+name+"-cert.pem")
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.ssl_room_socket = self.context.wrap_socket(self.room_socket, server_hostname=host)
        try:
            self.ssl_room_socket.connect((host, port))
            print("Connected to room {} on port {}".format(name, port))
            thread.Thread(target=self.rm_listen).start()
        except:
            print("Connection to room failed")

    def rm_disconnect(self):
        self.rm_send(jh.json_encode("room_disconnect", {}))
        sleep(0.5)
        self.ssl_room_socket.close()
        self.ssl_room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sv_listen(self):
        while True:
            received = self.server_socket.recv(1024)
            if received != "":
                if self.rsa.is_encrypted(received):
                    try:
                        decrypted = self.rsa.decrypt(received)
                        data = jh.json_decode(decrypted)
                        print("Server says: ", data)

                        for tag, callback in self.func_server.tag.items():
                            if jh.compare_tag_from_socket(data, tag, callback, self.server_socket):
                                print("Executed callback for tag", tag)
                                break
                    except:
                        print("A message has been received but an error occurred while decrypting it. Ignoring message...")
                else:
                    try:
                        data = jh.json_decode(received.decode())
                        print("Server says: ", data)

                        for tag, callback in self.func_server.tag_unencrypted.items():
                            if jh.compare_tag_from_socket(data, tag, callback, self.server_socket):
                                print("Executed callback for tag", tag)
                                break
                    except:
                        print("A unencrypted message has been received but an error occurred. Ignoring message...")

    def rm_listen(self):
        if self.ssl_room_socket:
            while True:
                received = self.ssl_room_socket.recv(1024)
                print("Received: ", received)
                try:
                    if received != "":
                        data = jh.json_decode(received)
                        print("Server says: ", data)

                        for tag, callback in self.func_room.tag.items():
                            if jh.compare_tag_from_socket(data, tag, callback, self.ssl_room_socket):
                                print("Executed callback for tag", tag)
                                break
                except:
                    print("An error occurred while processing the room message. Ignoring message...")

    def sv_authentification(self, username, password):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.user_mdp = hashed_password
        self.sv_send(jh.json_encode("authentification", {"username": username, "password": hashed_password}))

    def sv_add_user(self, username, password, name):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.sv_send(jh.json_encode("add_user", {"username": username, "password": hashed_password, "name": name}))

    def sv_create_room(self, room, password):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.sv_send(jh.json_encode("create_room", {"room": room, "password": hashed_password, "token": self.user_token}))

    def sv_connect_room(self, room, password):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        print("Connecting to room")
        self.sv_send(jh.json_encode("connect_room", {"room": room, "password": hashed_password, "token": self.user_token}))
    
    def sv_get_rooms(self):
        self.sv_send(jh.json_encode("get_rooms", {}))

    def sv_send(self, message):
        try:
            self.server_key = self.rsa.get_public_key("key-client/server-pub-key.pem")
            encrypted_message = self.rsa.encrypt(message.encode(), self.server_key)
            self.server_socket.send(encrypted_message)
        except FileNotFoundError:
            print("RSA key not found.")

    def sv_send_pem(self):
        path = "key-client/client-pub-key.pem"

        self.server_socket.send(jh.json_encode("get_pem_start", {}).encode())
        with open(path, 'rb') as file:
            seg_count = 0
            seg = file.read(512)
            while seg:
                sleep(0.1)
                encoded_seg = base64.b64encode(seg).decode('utf-8')
                self.server_socket.send(jh.json_encode("get_pem", {"seg": seg_count, "file": encoded_seg}).encode())
                seg = file.read(512)
                seg_count += 1
            sleep(0.1)
            self.server_socket.send(jh.json_encode("get_pem_end", {}).encode())

    def rm_send(self, message):
        if self.ssl_room_socket:
            self.ssl_room_socket.send(message.encode())

    def rm_send_message(self, message, username):
        if self.ssl_room_socket:
            try:
                self.ssl_room_socket.send(jh.json_encode("room_message", {"username": username, "message":message}).encode())
            except:
                print("Error sending message, no room connected.")

    def rm_send_file(self, file_path, room, username):
        if self.ssl_room_socket:
            file_name = os.path.basename(file_path)
            self.ssl_room_socket.send(jh.json_encode("room_file", {"room": room, "file_name": file_name, "username": username}).encode())
            with open(file_path, 'rb') as file:
                seg_count = 0
                seg = file.read(512)
                while seg:
                    sleep(0.1)
                    print("Sending pem file segment: ", seg_count)
                    encoded_seg = base64.b64encode(seg).decode('utf-8')
                    self.ssl_room_socket.send(jh.json_encode("room_file_seg", {"room": room, "seg": seg_count, "file_name": file_name, "file": encoded_seg}).encode())
                    seg = file.read(512)
                    seg_count += 1
                sleep(0.1)
                print("Sending pem file segment: end")
                self.ssl_room_socket.send(jh.json_encode("room_file_seg_end", {"file_name": file_name}).encode())

    def rm_users(self):
        print("Getting users")

    def __del__(self):
        self.server_socket.close()
