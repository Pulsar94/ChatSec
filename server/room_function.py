import server.rooms as rooms
import shared.json_handler as jh

class func:
    def __init__(self, room):
        self.room = room
        self.tag = {
            "room_disconnect": self.room_disconnect, 
            "room_message": self.handle_room_message,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
            "guest_try": self.guest_try
        }
    
    def room_disconnect(self, data, socket):
        self.room.remove_guest(socket.getpeername())
        print("Guest disconnected from room")

    def handle_room_message(self, data, socket):
        print("Adding message to ", self.room.name)
        self.room.add_message(data["data"]["message"], data["data"]["username"])

    def room_file(self, data, socket):
        print("Adding file to ", self.room.name)
        self.room.add_file(data["data"]["file_name"])
        self.room.sender_socket = socket  # Keep track of the sender's socket

    def room_file_seg(self, data, socket):
        print("Adding file segment to ", self.room.name)
        self.room.add_file_seg(data["data"]["file_name"], data["data"]["file"])

    def room_file_seg_end(self, data, socket):
        print("File segment end received")
        for guest in self.room.get_guests():
            guest_socket = list(guest.values())[0]
            if guest_socket != self.room.sender_socket:  # Skip sending to the sender
                guest_socket.send(jh.json_encode("room_file", {"file_name": data["data"]["file_name"]}).encode())
                for seg in self.room.files[data["data"]["file_name"]]:
                    guest_socket.send(jh.json_encode("room_file_seg", {"file_name": data["data"]["file_name"], "file": seg}).encode())
                guest_socket.send(jh.json_encode("room_file_seg_end", {"file_name": data["data"]["file_name"]}).encode())

    def guest_try(self, data, socket):
        print("Guest try received")
        self.room.reset_guest_try(socket.getpeername())