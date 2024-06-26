import rooms
import json_handler as jh
import threading

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
            "file_accept_response": self.file_accept_response  # Nouvelle fonction
        }
        self.pending_files = {}

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
            file_info = {
                "file_name": data["data"]["file_name"],
                "file_data": [],
                "sender_socket": socket
            }
            self.pending_files[data["data"]["file_name"]] = file_info
            for guest in room.get_guests():
                guest_socket = list(guest.values())[0]
                if guest_socket != socket:  # Skip sending to the sender
                    guest_socket.send(jh.json_encode("file_accept_request", {"username": data["data"]["username"], "file_name": data["data"]["file_name"]}).encode())
            threading.Timer(30.0, self.drop_pending_file, args=[data["data"]["file_name"]]).start()

    def room_file_seg(self, data, socket):
        file_info = self.pending_files.get(data["data"]["file_name"])
        if file_info:
            file_info["file_data"].append(data["data"]["file"])

    def room_file_seg_end(self, data, socket):
        file_info = self.pending_files.get(data["data"]["file_name"])
        if file_info:
            file_info["file_data"].append(None)  # Indicate end of file

    def file_accept_response(self, data, socket):
        file_name = data["data"]["file_name"]
        accepted = data["data"]["accepted"]
        file_info = self.pending_files.get(file_name)
        if file_info and accepted:
            for seg in file_info["file_data"]:
                if seg is not None:
                    socket.send(jh.json_encode("room_file_seg", {"file_name": file_name, "file": seg}).encode())
                else:
                    socket.send(jh.json_encode("room_file_seg_end", {"file_name": file_name}).encode())

    def drop_pending_file(self, file_name):
        if file_name in self.pending_files:
            print(f"Dropping file {file_name} due to timeout")
            del self.pending_files[file_name]
