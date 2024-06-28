import shared.json_handler as jh
import threading as thread
import socket
import ssl
from server.room_function import func
from shared.certificate import get_or_generate_cert
from time import sleep

CERT_EXPIRATION_DAYS = 1

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

    def room_guests_checker(self):
        while True:
            sleep(10)
            for r in self.rooms:
                if r.guest_try():
                    self.del_room(r)

    def has_guests(self):
        for r in self.rooms:
            return len(r.guests) > 0

    def del_room(self, room):
        room.room_socket.close()
        self.rooms.remove(room)

class Room:
    def __init__(self, name, port, password=None):
        self.name = name
        self.password = password
        self.port = port
        self.guests = {}
        self.files = {}

        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        cert, key = "key-server/"+name+"-cert.pem", "key-server/"+name+"-server.pem"
        get_or_generate_cert(cert, key, CERT_EXPIRATION_DAYS)
        self.context.load_cert_chain(certfile=cert, keyfile=key)
        
        self.func = func(self)
        
        self.room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room_socket.bind((socket.gethostname(), self.port))
        self.room_socket.listen(5)
        thread.Thread(target=self.listen).start()
        print("Room: "+name+" is ready to receive a connection")

    def listen(self):
        while True:
            print("Waiting for connection")
            (clientsocket, address) = self.room_socket.accept()
            print("Connection from", address, ". Creating new thread")
            stream = self.context.wrap_socket(clientsocket, server_side=True)
            thread.Thread(target=self.handle_client_room, args=(stream, address)).start()
            self.add_guest(stream, stream.getpeername())
    
    def handle_client_room(self, stream, address):
        while True:
            received = stream.recv(1024).decode()
            if received != "":
                self.reset_guest_try(address)
                data = jh.json_decode(received)
                print("Client says: ", data)

                for tag, callback in self.func.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, stream):
                        print("Executed callback for tag", tag)
                        break
    
    def reset_guest_try(self, addr):
        for key, data in self.guests.items():
            if key == addr:
                data["try"] = 3

    def guest_try(self):
        for key, s_data in self.guests.items():
            s_data["try"] -= 1
            if s_data["try"] == 0:
                self.remove_guest(key)
                print("Guest kicked")
            else:
                data = jh.json_encode("guest_try", {})
                s_data["socket"].send(data.encode())
        
        return self.guests == 0

    def add_guest(self, guest, addr):
        for key, data in self.guests.items():
            if key == addr:
                print("Guest already in room")
                return False
        self.guests[addr] = {"socket": guest, "try": 3}
        return True

    def remove_guest(self, addr):
        for key, data in self.guests.items():
            if key == addr:
                data["socket"].close()
                self.guests.pop(key)
        return self.guests == 0

    def get_guests(self):
        return self.guests

    def add_message(self, message, username):
        for key, data in self.guests.items():
            print("Sending message to guest", key)
            data_to_send = jh.json_encode("room_message", {"room": self.name, "username": username, "message": message})
            data["socket"].send(data_to_send.encode())

    def add_file(self, filename):
        self.files[filename] = []

    def add_file_seg(self, filename, segment):
        self.files[filename].append(segment)

    def add_file_seg_end(self, filename):
        for key, s_data in self.guests.items():
            seg_count = 0
            s_data["socket"].send(jh.json_encode("room_file", {"file_name": filename}).encode())
            for seg in self.files[filename]:
                sleep(0.1)
                print("Sending file segment to guest", key)
                data = jh.json_encode("room_file_seg", {"file_name": filename, "seg": seg_count, "file": seg})
                s_data["socket"].send(data.encode())
                seg_count += 1
            sleep(0.1)
            s_data["socket"].send(jh.json_encode("room_file_seg_end", {"file_name": filename}).encode())
