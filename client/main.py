import socket

class Client:
    def __init__(self):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, host, port):
        self.clientsocket.connect((host, port))
        print("Connected to server")
        
    def send(self, message):
        self.clientsocket.send(message.encode())
        
    def receive(self):
        return self.clientsocket.recv(1024).decode()

    def listen(self, time):
        server_response = ""
        while time > 0:
            server_response = print(self.receive())
            if server_response:
                break
            time -= 1
        return server_response
    
    def __del__(self):
        self.clientsocket.close()

def main():
    client = Client()
    client.connect(socket.gethostname(), 5000)
    client.send("Hello, server!")
    print(client.listen(500))
    
main()