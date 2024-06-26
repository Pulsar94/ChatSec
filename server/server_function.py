import server.rooms as rooms
import shared.json_handler as jh
import threading as thread

class func:
    def __init__(self, server):
        self.server = server
        self.rooms = rooms.Rooms()
        self.port = 5000
        self.tag = {
            "create_room": self.create_room,
            "connect_room": self.connect_room,
            "room_disconnect": self.handle_room_disconnect,
            "debug": self.debug,
        }

    def create_room(self, data, socket):
        self.port += 1
        room = rooms.Room(data["data"]["room"], self.port, data["data"]["password"])
        if self.rooms.add_room(room):
            thread.Thread(target=room.listen).start()
            client_data = jh.json_encode('room_created', {"name":room.name, "port":self.port})
        else:
            client_data = jh.json_encode('room_already_created', room.name)
        self.server.send(socket, client_data)

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
    
    def debug(self, data, socket):
        print("Debug: ", data["data"])
        client_data = jh.json_encode("debug", "hello")
        self.server.send(socket, client_data)
