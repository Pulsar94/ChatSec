import rooms
import json_handler as jh

class func:
    def __init__(self):
        self.rooms = rooms.Rooms()
        self.tag = {
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
