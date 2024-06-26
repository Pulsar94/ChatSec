import server.rooms as rooms
import shared.json_handler as jh

class func:
    def __init__(self, server):
        self.server = server
        self.rooms = rooms.Rooms()
        self.port = 5000
        self.tag = {
            "create_room": self.create_room,
            "connect_room": self.connect_room,
            "room_disconnect": self.handle_room_disconnect,
        }

    def create_room(self, data, socket):
        self.port += 1
        room = rooms.Room(data["data"]["room"], self.port, data["data"]["password"])
        if self.rooms.add_room(room):
            room.add_guest(socket, socket.getpeername())
            client_data = jh.json_encode('room_created', room.name)
        else:
            client_data = jh.json_encode('room_already_created', room.name)
        socket.send(client_data.encode())

    def connect_room(self, data, socket):
        print("Connecting to room")
        room = self.rooms.get_room(data["data"]["room"])
        passw = data["data"]["password"]
        if room:
            if room.password and room.password != passw and passw != "":
                client_data = jh.json_encode("room_wrong_password", "")
            elif room.add_guest(socket, socket.getpeername()):
                client_data = jh.json_encode("room_already_connected", "")
            else:
                client_data = jh.json_encode("room_connected", "")
            socket.send(client_data.encode())
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
