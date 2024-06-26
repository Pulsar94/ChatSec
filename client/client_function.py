import shared.json_handler as jh
import base64

class func_server:
    def __init__(self, client):
        self.client = client
        self.tag = {
            "room_already_connected": self.room_already_connected,
            "connect_room": self.connect_room,
            "room_found": self.room_found,
            "room_already_created": self.room_already_created,
            "room_wrong_password": self.room_wrong_password,
            "debug": self.debug,
        }
        self.files = {}

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
    
    def debug(self, data, socket):
        print("Debug: ", data["data"])
        client_data = jh.json_encode("debug", "hello")
        self.client.sv_send(client_data)

class func_room:
    def __init__(self, client):
        self.client = client
        self.tag = {
            "room_message": self.room_message,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
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
    
    
   