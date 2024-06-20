import json_handler as jh

class func:
    def __init__(self):
        self.tag = {
            "room_created": self.room_created,
            "room_already_connected": self.room_already_connected,
            "room_connected": self.room_connected,
            "room_found": self.room_found,
            "room_message": self.room_message,
            "room_already_created": self.room_already_created,
        }

    def room_created(self, data, socket):
        print("Room created")

    def room_already_connected(self, data, socket):
        print("Room already connected")

    def room_connected(self, data, socket):
        print("Room connected")

    def room_found(self, data, socket):
        print("Room found")

    def room_message(self, data, socket):
        print("message received: ", data["data"])
    
    def room_already_created(self, data, socket):
        print("Room already created")
        room = data["data"]
        client_data = jh.json_encode("connect_room", {"name": room})
        socket.send(client_data.encode())

    
    
   