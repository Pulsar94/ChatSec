import socket
from shared.rsa_handler import RSAHandler as rsa
import server.rooms as rooms
import shared.json_handler as jh
import threading as thread
from server.server_function import func
from time import sleep
import base64

CERT_FILE_SERVER = "key-server/server-cert.pem"
KEY_FILE_SERVER = "key-server/server-key.pem"
PUB_KEY_FILE_SERVER = "key-server/server-pub-key.pem"

CERT_EXPIRATION_DAYS = 1

class Server:
    def __init__(self):
        self.rooms = rooms.Rooms()
        self.rsa = rsa(CERT_FILE_SERVER, KEY_FILE_SERVER, CERT_EXPIRATION_DAYS, PUB_KEY_FILE_SERVER)
        self.session_handler = {} # Store client ip, public key, and session time
        
        self.func = func(self)
        
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")

    def listen(self):
        while True:
            print("Waiting for connection")
            (clientsocket, address) = self.serversocket.accept()
            print("Connection from", address, ". Creating new thread")

            thread.Thread(target=self.handle_client, args=(clientsocket, address)).start()
    
    def handle_client(self, stream, address):
        while True:
            received = stream.recv(1024)
            if received != "":
                if self.rsa.is_encrypted(received):
                    print(received)
                    try:
                        decrypted = self.rsa.decrypt(received)
                        data = jh.json_decode(decrypted)
                        print("Client says: ", data)
                    except:
                        print("A message has been received but an error occurred while decrypting it.")
                        self.send(stream, jh.json_encode("error", "An error occurred while decrypting the message."))
                    
                    try:
                        for tag, callback in self.func.tag.items():
                            if jh.compare_tag_from_socket(data, tag, callback, stream):
                                print("Executed callback for tag", tag)
                                break
                    except:
                        print("An error occurred while executing the callback. ")
                else:
                    data = jh.json_decode(received.decode())
                    for tag, callback in self.func.tag_unencrypted.items():
                        if jh.compare_tag_from_socket(data, tag, callback, stream):
                            print("Executed callback for tag", tag)
                            break
                

    def send(self, connstream, message):
        public_key = self.rsa.get_public_key("key-server/"+str(connstream.getpeername()[0])+"-pub-key.pem")
        crypted_message = self.rsa.encrypt(message.encode(), public_key)
        connstream.send(crypted_message)
    
    def send_pem(self, connstream, filename):
        path = "key-server/"+filename+".pem"

        connstream.send(jh.json_encode("get_pem_start", {"file_name": filename}).encode())
        sleep(0.1)
        with open(path, 'rb') as file:
            seg_count = 0
            seg = file.read(512)
            while seg:
                sleep(0.1)
                print("Sending file segment: ", seg_count)
                encoded_seg = base64.b64encode(seg).decode('utf-8')
                print("Sending file segment: ", encoded_seg)
                connstream.send(jh.json_encode("get_pem", {"seg": seg_count, "file_name": filename, "file": encoded_seg}).encode())
                seg = file.read(512)
                seg_count += 1
            sleep(0.1)
            print("Sending file segment: end")
            connstream.send(jh.json_encode("get_pem_end", {"file_name": filename}).encode())

    def __del__(self):
        self.serversocket.close()

