import server.rooms as rooms
import shared.json_handler as jh
import threading as thread
from os import makedirs
import base64

class func:
    def __init__(self, server):
        self.pem_file = []
        self.server = server
        self.rooms = rooms.Rooms()
        self.port = 5000
        self.tag = {
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
        self.port += 1
        room = rooms.Room(data["data"]["room"], self.port, data["data"]["password"])
        if self.rooms.add_room(room):
            thread.Thread(target=room.listen).start()
            self.server.send_pem(socket, room.name+"-cert")
            client_data = jh.json_encode("connect_room", {"name":room.name, "port":room.port}) # Here we should also send the public key
        else:
            client_data = jh.json_encode('room_already_created', room.name)
        self.server.send(socket, client_data)

    def connect_room(self, data, socket):
        print("Connecting to room")
        room = self.rooms.get_room(data["data"]["room"])
        passw = data["data"]["password"]
        client_data = ""
        if room:
            if room.password and room.password != passw and passw != "":
                client_data = jh.json_encode("room_wrong_password", "")
            else:
                self.server.send_pem(socket, room.name+"-cert")
                client_data = jh.json_encode("connect_room", {"name":room.name, "port":room.port}) # Here we should also send the public key
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
        makedirs("key-server", exist_ok=True)
        with open("key-server/"+str(socket.getpeername()[0])+"-pub-key.pem", 'wb') as file:
            for seg in self.pem_file:
                file.write(base64.b64decode(seg))
        self.pem_file = []
    
    def debug(self, data, socket):
        print("Debug: ", data["data"])
        client_data = jh.json_encode("debug", "hello")
        self.server.send(socket, client_data)
