import json_handler as jh
import base64

class func:
    def __init__(self):
        self.tag = {
            "room_created": self.room_created,
            "room_already_connected": self.room_already_connected,
            "room_connected": self.room_connected,
            "room_found": self.room_found,
            "room_message": self.room_message,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
        }
        self.files = {}
        
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
        
    
    
   