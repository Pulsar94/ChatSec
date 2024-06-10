import socket   

class Client_data:
    def __init__(self):
        self.client = {}
        
    def add_client(self, socket, name, pk):
        self.client[name] = {socket:pk}
    
    def get_client(self, name):
        return self.client[name]
    
    def remove_client(self, name):
        del self.client[name]

class Server:
    def __init__(self, data = Client_data()):
        self.data = data
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((socket.gethostname(), 5000))
        self.serversocket.listen(5)
        print("Server is ready to receive a connection")
        
    def receive(self):
        (clientsocket, address) = self.serversocket.accept()
        print("Connection from", self.address)
        print("Client says: ", clientsocket.recv(1024).decode())
        return clientsocket, address
    
    def send(self, clientsocket, message):
        clientsocket.send(message.encode())
        
    def __del__(self):
        self.serversocket.close()
        
    def process_PK_request(self, clientsocket, address):
        print("Processing PK request")
        clientsocket.send("PK".encode())
        
    def process_PK_response(self, clientsocket, address):
        print("Processing PK authentification")
        decoded = clientsocket.recv(1024).decode()
        pk = decoded.split(" ")
        name = pk[0]
        self.data.add_client(clientsocket, name, pk[1])
        self.send(clientsocket, "PK received")
        
    def process_PK_request_data(self, clientsocket, address):
        print("Processing PK request from data")
        name = clientsocket.recv(1024).decode()
        data_requested = self.data.get_client(name)
        if data_requested:
            self.send(clientsocket, data_requested)
    
def main():
    server = Server()
    (clientsocket, address) = server.receive()
    server.send(clientsocket, "Hello, client!")
        
main()