import socket
import ssl
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

    def add_guest(self, guest):
        self.guests.append(guest)

    def remove_guest(self, guest):
        self.guests.remove(guest)

    def get_guests(self):
        return self.guests
    
    def add_message(self, message):
        for g in self.guests:
            print("Sending message to guest")
            data = jh.json_encode("room_message", message)
            g.send(data.encode())

    