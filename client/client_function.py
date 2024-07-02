import shared.json_handler as jh
import base64
from os import makedirs
import base64

class func_server:
    def __init__(self, client):
        self.client = client
        self.pem_file, self.filename = [], ""
        self.tag = {
            "room_already_connected": self.room_already_connected,
            "connect_room": self.connect_room,
            "room_found": self.room_found,
            "room_already_created": self.room_already_created,
            "room_wrong_password": self.room_wrong_password,
            "debug": self.debug,
            "authenticated": self.token,
            "get_rooms": self.get_rooms,

        }
        self.tag_unencrypted = {
            "need_pem": self.need_pem,
            "get_pem_start": self.get_pem_start,
            "get_pem": self.get_pem,
            "get_pem_end": self.get_pem_end,
        }
        self.files = {}

    def get_rooms(self, data, socket):
        print("Rooms: ", data["data"])
        self.client.room_list = data["data"]

    def room_already_connected(self, data, socket):
        print("Room already connected")

    def connect_room(self, data, socket):
        host = socket.getpeername()[0]
        port = data["data"]["port"]
        name = data["data"]["name"]
        self.client.rm_connect(host, port, name)
    
    def room_wrong_password(self, data, socket):
        print("Wrong password")

    def room_found(self, data, socket):
        print("Room found")
        
    def room_already_created(self, data, socket):
        print("Room already exists")
    
    def need_pem(self, data, socket):
        filename = "client-pub-key"
        self.client.server_socket.send(jh.json_encode("need_pem",{}).encode())
    
    def get_pem_start(self, data, socket):
        self.filename = data["data"]["file_name"]
        self.pem_file = []

    def get_pem(self, data, socket):
        self.pem_file.append(data["data"]["file"])

    def get_pem_end(self, data, socket):
        makedirs("key-client", exist_ok=True)
        with open("key-client/"+self.filename+".pem", 'wb') as file:
            for seg in self.pem_file:
                file.write(base64.b64decode(seg))
        self.filename = ""
        self.pem_file = []
        self.client.sv_send_pem()
    
    def debug(self, data, socket):
        print("Debug: ", data["data"])
        client_data = jh.json_encode("debug", "hello")
        self.client.sv_send(client_data)

    def token(self, data, socket):
        print("Token received: ", data["data"]["token"])
        self.client.sv_token(data["data"]["token"])

class func_room:
    def __init__(self, client):
        self.client = client
        self.tag = {
            "room_message": self.room_message,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
            "guest_try": self.guest_try,
        }
        self.files = {}

    def room_message(self, data, socket):
        print("message received: ", data["data"])

    def room_file(self, data, socket):
        print("file received")
        file_name = data["data"]["file_name"]
        self.files[file_name] = []
    
    def room_file_seg(self, data, socket):
        print("file segment received")
        file_name = data["data"]["file_name"]
        self.files[file_name].append(data["data"]["file"])
    
    def room_file_seg_end(self, data, socket):
        print("file segment end received")
        with open(data["data"]["file_name"], 'wb') as file:
            for seg in self.files[data["data"]["file_name"]]:
                file.write(base64.b64decode(seg))
    
    def guest_try(self, data, socket):
        client_data = jh.json_encode("guest_try", {})
        self.client.rm_send(client_data)
    
    
   