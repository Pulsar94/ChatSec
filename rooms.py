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
        self.files = {}

    def add_guest(self, guest, addr):
        for sock in self.guests:
            if list(sock.keys())[0] == addr:
                print("Guest already in room")
                return False
        self.guests.append({addr:guest})
        return True

    def remove_guest(self, addr):
        for sock in self.guests:
            if list(sock.keys())[0] == addr:
                self.guests.remove(sock)
                return
        
        return self.guests == 0

    def get_guests(self):
        return self.guests
    
    def add_message(self, message):
        for sock in self.guests:
            print("Sending message to guest", list(sock.keys())[0])
            data = jh.json_encode("room_message", message)
            list(sock.values())[0].send(data.encode())
    
    def add_file(self, filename):
        self.files[filename] = []
    
    def add_file_seg(self, filename, segment):
        self.files[filename].append(segment)
    
    def add_file_seg_end(self, filename):
        for sock in self.guests:
            seg_count = 0
            list(sock.values())[0].send(jh.json_encode("room_file", {"file_name": filename}).encode())
            for seg in self.files[filename]:
                print("Sending file segment to guest", list(sock.keys())[0])
                data = jh.json_encode("room_file_seg", {"file_name": filename, "seg": seg_count, "file": seg})
                list(sock.values())[0].send(data.encode())
                seg_count += 1
            list(sock.values())[0].send(jh.json_encode("room_file_seg_end", {"file_name": filename}).encode())
            
            
        

    