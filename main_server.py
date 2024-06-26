from server.server import Server
import threading as thread

def main():
    print("---------------------------Starting server---------------------------")
    server = Server()
    thread.Thread(target=server.listen).start()
    

main()