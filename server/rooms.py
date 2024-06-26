import shared.json_handler as jh
import threading as thread
import socket
import ssl
from server.room_function import func
from shared.certificate import get_or_generate_cert

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

    def del_room(self, room):
        self.rooms.remove(room)

class Room:
    def __init__(self, name, port, password=None):
        self.name = name
        self.password = password
        self.guests = []
        self.files = {}

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cert, key = "key/"+name+"-cert.pem", "key/"+name+"-server.pem"
        get_or_generate_cert(cert, key, CERT_EXPIRATION_DAYS)
        self.context.load_cert_chain(certfile=cert, keyfile=key)
        
        self.func = func(self)
        
        self.room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room_socket.bind((socket.gethostname(), port))
        self.room_socket.listen(5)
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
                data = jh.json_decode(received)
                print("Client says: ", data)

                for tag, callback in self.func.tag.items():
                    if jh.compare_tag_from_socket(data, tag, callback, stream):
                        print("Executed callback for tag", tag)
                        break

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
        return self.guests == 0

    def get_guests(self):
        return self.guests

    def add_message(self, message, username):
        for sock in self.guests:
            print("Sending message to guest", list(sock.keys())[0])
            data = jh.json_encode("room_message", {"room": self.name, "username": username, "message": message})
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
