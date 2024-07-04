import shared.json_handler as jh
import server.authenticator as auth

class func:
    def __init__(self, room):
        self.room = room
        self.users = auth.Authenticator().extract_all_user_info()
        self.tag = {
            "need_token": self.need_token,
            "room_disconnect": self.room_disconnect, 
            "room_message": self.handle_room_message,
            "room_file": self.room_file,
            "room_file_seg": self.room_file_seg,
            "room_file_seg_end": self.room_file_seg_end,
            "guest_try": self.guest_try,
            "room_file_request": self.room_file_request,
        }
    
    def need_token(self, data, socket):
        print("Token received: ", data["data"]["token"])
        user = self.users[data["data"]["name"]]
        if user["password"] != data["data"]["token"]:
            return
        self.room.add_guest(socket, socket.getpeername(), user["name"])
    
    def room_disconnect(self, data, socket):
        self.room.remove_guest(socket.getpeername())
        print("Guest disconnected from room")

    def handle_room_message(self, data, socket):
        print("Adding message to ", self.room.name)
        username = self.room.guests[socket.getpeername()]["username"]
        self.room.add_message(data["data"]["message"], username)

    def room_file(self, data, socket):
        print("Adding file to ", self.room.name)
        self.room.add_file(data["data"]["file_name"], socket.getpeername())
        print("File added to ", self.room.name)

    def room_file_seg(self, data, socket):
        print("Adding file segment to ", self.room.name)
        self.room.add_file_seg(data["data"]["file_name"], data["data"]["file"])

    def room_file_seg_end(self, data, socket):
        print("File segment end received")
        self.room.add_file_seg_end(data["data"]["file_name"])

    def guest_try(self, data, socket):
        self.room.reset_guest_try(socket.getpeername())
    
    def room_file_request(self, data, socket):
        print("File request accepted")
        self.room.send_file(data["data"]["name"], socket)