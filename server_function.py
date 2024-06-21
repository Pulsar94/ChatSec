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

        client_data = jh.json_encode('room_created', '')
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
            room.add_message(data["data"]["message"])
            
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
            room.add_file_seg_end(data["data"]["file_name"])
        else:
            client_data = jh.json_encode("room_not_found", "")
            socket.send(client_data.encode())