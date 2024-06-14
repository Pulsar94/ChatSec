import rooms
import json_handler as jh

class func:
    def __init__(self):
        self.tag = {
            "create_room": self.create_room,
            "connect_room": self.connect_room,
        }
    
    def create_room(self, data, socket):
        print("Creating room")
        room = rooms.Room(data["data"]["name"], data["data"]["password"])
        self.rooms.add_room(room)
        room.add_guest(socket)

        client_data = jh.json_encode("room_created", "")
        socket.send(client_data.encode())
        socket.close()
    
    def connect_room(self, data, socket):
        print("Connecting to room")
        room = self.rooms.get_room(data["data"]["name"])
        if room:
            room.add_guest(socket)
            client_data = jh.json_encode("room_connected", "")
            socket.send(client_data.encode())
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())
        socket.close()