from tkinter import ttk, Toplevel
from tkinter import filedialog
import base64
from shared.json_handler import json_encode

class FileTransferDialog(Toplevel):
    def __init__(self, parent, file_name, size, client, timeout=30):
        super().__init__(parent)
        self.title("File Received")
        self.file_name = file_name
        self.timeout = timeout
        self.result = None
        self.client = client
        
        self.label = ttk.Label(self, text=f"Someone wants to send you the file {file_name} (size {size} bytes). Do you want to accept?")
        self.label.pack(pady=10)

        self.countdown_label = ttk.Label(self, text=f"Time remaining: {self.timeout} seconds")
        self.countdown_label.pack(pady=10)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        self.accept_button = ttk.Button(self.button_frame, text="Accept", command=self.accept)
        self.accept_button.grid(row=0, column=0, padx=5)
        
        self.decline_button = ttk.Button(self.button_frame, text="Decline", command=self.decline)
        self.decline_button.grid(row=0, column=1, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.decline)  # Handle window close button
        
        self.start_countdown()

        # Center the dialog on the parent window
        self.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2
        y = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def start_countdown(self):
        if self.timeout > 0:
            self.timeout -= 1
            self.countdown_label.config(text=f"Time remaining: {self.timeout} seconds")
            self.after(1000, self.start_countdown)
        else:
            self.decline()

    def accept(self):
        self.client.rm_send(json_encode("room_file_request", {"name": self.file_name}))
        self.destroy()

    def decline(self):
        self.destroy()

def on_file_received(file_name, file_data):
    save_path = filedialog.asksaveasfilename(initialfile=file_name, title="Save File As")
    if save_path:
        with open(save_path, 'wb') as file:
            for seg in file_data:
                file.write(base64.b64decode(seg))
        print("File accepted and saved")
    else:
        print("File declined")