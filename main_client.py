from GUI.GUI import ChatApp

def main():
    print("---------------------------Starting client---------------------------")
    client = Client()
    client.sv_connect(socket.gethostname(), 5000)
    thread.Thread(target=client.sv_listen).start()
    time.sleep(1)
    client.sv_authentification("tibo@secu.hack", "1234")
    # time.sleep(1)
    # client.sv_add_user("Tom", "123", "toto")
    time.sleep(1)
    client.sv_create_room("room1", "123")
    # time.sleep(1)
    # client.rm_send_message("hello", "Tom")

    
    
    
    app = ChatApp()
    app.mainloop()


main()