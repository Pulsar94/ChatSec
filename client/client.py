import socket
import ssl
import threading as thread
import shared.json_handler as jh
from client.client_function import func_room, func_server
import base64
import os
import hashlib
from shared.rsa_handler import RSAHandler as rsa

CERT_FILE_SERVER = "key/server-cert.pem"
PUB_KEY_FILE_SERVER = "key/server-pub-key.pem"

CERT_FILE_CLIENT = "key/client-cert.pem"
KEY_FILE_CLIENT = "key/client-key.pem"
PUB_KEY_FILE_CLIENT = "key/client-pub-key.pem"

CERT_EXPIRATION_DAYS = 1

class Client:
    def __init__(self):
        self.rsa = rsa(CERT_FILE_CLIENT, KEY_FILE_CLIENT, CERT_EXPIRATION_DAYS, PUB_KEY_FILE_CLIENT)
        self.server_key = self.rsa.get_public_key(PUB_KEY_FILE_SERVER)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.func_server = func_server(self)
        self.func_room = func_room(self)
    
    def sv_connect(self, host, port):
        try:
            self.server_socket.connect((host, port))
            print("Connected to server {} on port {}".format(host, port))
        except:
            print("Connection failed")

    def rm_connect(self, host, port, name):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations("key/"+name+"-cert.pem")
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        
        self.ssl_room_socket = self.context.wrap_socket(self.server_socket, server_hostname=host)
        try:
            self.ssl_room_socket.connect((host, port))
            print("Connected to room {} on port {}".format(name, port))
        except:
            print("Connection to room failed")
    
    def sv_listen(self):
        while True:
            received = self.server_socket.recv(1024)
            if received != "":
                decrypted = self.rsa.decrypt(received)
                data = jh.json_decode(decrypted)
                print("Server says: ", data)

                for tag, callback in self.func_server.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, self.server_socket):
                        print("Executed callback for tag", tag)
                        break
    
    def rm_listen(self):
        while True:
            received = self.ssl_room_socket.recv(1024)
            if received != "":
                data = jh.json_decode(received)
                print("Server says: ", data)

                for tag, callback in self.func_room.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, self.ssl_room_socket):
                        print("Executed callback for tag", tag)
                        break
    
    def sv_create_room(self, room, password):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.sv_send(jh.json_encode("create_room", {"room": room, "password": hashed_password}))
    
    def sv_connect_room(self, room, password):
        hashed_password = ""
        if password != "":
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.sv_send(jh.json_encode("connect_room", {"room": room, "password": hashed_password}))
    
    def sv_send(self, message):
        encrypted_message = self.rsa.encrypt(message.encode(), self.server_key)
        self.server_socket.send(encrypted_message)

    def rm_send(self, message):
        self.ssl_room_socket.send(message.encode())
    
    def rm_send_message(self, message, username):
        self.ssl_room_socket.send(jh.json_encode("room_message", {"username": username, "message":message}).encode())
    
    def rm_send_file(self, file_path):
        file_name = os.path.basename(file_path)
        self.ssl_room_socket.send(jh.json_encode("room_file", {"file_name": "ret_"+file_name}).encode())
        with open(file_path, 'rb') as file:
            seg_count = 0
            seg = file.read(512)
            while seg:
                print("Sending file segment: ", seg_count)
                encoded_seg = base64.b64encode(seg).decode('utf-8')
                self.ssl_room_socket.send(jh.json_encode("room_file_seg", {"seg": seg_count, "file_name": "ret_"+file_name, "file": encoded_seg}).encode())
                seg = file.read(512)
                seg_count += 1
            print("Sending file segment: end")
            self.ssl_room_socket.send(jh.json_encode("room_file_seg_end", {"file_name": "ret_"+file_name}).encode())
                  
    def __del__(self):
        self.server_socket.close()
