import json_handler as jh

class Rooms:
    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        if not self.get_room(room.name):
            self.rooms.append(room)
        else:
            print("Room already exists")
            return False
        return True

    def get_room(self, room):
        for r in self.rooms:
            if r.name == room:
                return r

    def get_rooms(self):
        return self.rooms

    def del_room(self, room):
        self.rooms.remove(room)

class Room:
    def __init__(self, name, password=None):
        self.name = name
        self.password = password
        self.guests = []

    def add_guest(self, guest, addr):
        for sock in self.guests:
            if list(sock.keys())[0] == addr:
                print("Guest already in room")
                return False
        self.guests.append({addr: guest})
        return True

    def remove_guest(self, addr):
        for sock in self.guests:
            if list(sock.keys())[0] == addr:
                self.guests.remove(sock)
                return

    def get_guests(self):
        return self.guests

    def add_message(self, message, username):
        full_message = f"{username}: {message}"
        for sock in self.guests:
            print("Sending message to guest", list(sock.keys())[0])
            data = jh.json_encode("room_message", {"room": self.name, "username": username, "message": message})
            list(sock.values())[0].send(data.encode())
