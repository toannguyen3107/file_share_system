import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import socket
import threading
import shutil

sep = '<sep>'

class PeerGUI:
    def __init__(self, master, server_host, server_port, port_self):
        self.master = master
        self.master.title("Peer GUI")
        self.server_host = server_host
        self.server_port = server_port
        self.port_self = port_self
        self.file = []
        self.file_listbox = tk.Listbox(self.master)
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Command List:")
        self.label.pack(pady=10)

        self.publish_button = tk.Button(self.master, text="Publish", command=self.publish_file)
        self.publish_button.pack(pady=10)

        self.fetch_button = tk.Button(self.master, text="Fetch", command=self.fetch_file)
        self.fetch_button.pack(pady=10)
        
        self.fetch_button = tk.Button(self.master, text="Refresh", command=self.update_file_list)
        self.fetch_button.pack(pady=10)

        self.file_listbox.pack(pady=10)

        self.exit_button = tk.Button(self.master, text="Exit", command=self.exit_program)
        self.exit_button.pack(pady=10)

    def publish_file(self):
        file_path = filedialog.askopenfilename(title="Select a file to publish")
        if file_path:
            dir_check = os.path.join(os.getcwd(), 'repository')
            if not os.path.exists(dir_check):
                os.mkdir('repository')
            elif not os.path.exists(file_path):
                print('The lname is an invalid path')
                return
            fname = os.path.basename(file_path)
            try:
                shutil.copyfile(file_path, os.path.join(dir_check, fname))
            except FileNotFoundError:
                print(f'The file "{file_path}" does not exist.')
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                send_seg = f"publish{sep}{fname}{sep}{fname}"
                sock.send(send_seg.encode())
                status = sock.recv(1024).decode()
                print(status)
                if status == '200':
                    messagebox.showinfo("Success", "File published successfully.")
                    file_list = sock.recv(1024).decode()
                    if file_list != "":
                        file_list = file_list.strip().split(sep)
                        # Reset file in peer
                        self.file = []
                        ###
                        for file in file_list:
                            if (file != ''):
                                self.file.append(file)
                                
                        self.update_file_list()
                else:
                    messagebox.showerror("Error", "Failed to publish file.")
                sock.close()

    def fetch_file(self):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            # fname = selected_file.split(sep)[0]
            fname = selected_file.strip()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.server_port))
                send_seg = f"fetch{sep}{fname}"
                sock.send(send_seg.encode())
                mess_rcv = sock.recv(1024).decode()
                arr_mess = mess_rcv.split(sep)
                if len(arr_mess) == 3 and arr_mess[1] == '404':
                    messagebox.showerror("Error", arr_mess[2])
                else:
                    host_transfer = arr_mess[1]
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.connect((host_transfer, self.port_self))
                        sock.send(f"fetch{sep}{fname}".encode())
                        download_folder = os.path.join(os.getcwd(), 'Download')
                        if not os.path.exists(download_folder):
                            os.mkdir(download_folder)
                        with open(os.path.join(download_folder, fname), 'wb') as f:
                            while True:
                                data = sock.recv(1024)
                                if not data:
                                    break
                                f.write(data)
                    messagebox.showinfo("Success", f"File '{fname}' fetched successfully.")
                sock.close()

    def update_file_list(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.server_host, self.server_port))
            msg = "update" + sep
            sock.send(msg.encode())
            msg_recv = sock.recv(1024).decode()
            
            if (msg_recv == "empty"): 
                return
            
            mess_split = msg_recv.strip().split(sep)
            file_list = mess_split[1:]
            self.file = []
            for file in file_list:
                if (file != ''):
                    self.file.append(file)
                    
        self.file_listbox.delete(0, tk.END)
        for file in self.file:
            self.file_listbox.insert(tk.END, file)

    def exit_program(self):
        self.master.destroy()


def discover_and_update(peer_gui):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('0.0.0.0', peer_gui.port_self))
        sock.listen(5)
        sock.settimeout(1)
        discover_message = "discover" + sep
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.connect((peer_gui.server_host, peer_gui.server_port))
            server_sock.send(discover_message.encode())
            mess = server_sock.recv(1024).decode()
            print(mess)
            mess_split = mess.strip().split(sep)
            if mess_split[0] == "discover":
                file_list = mess_split[1:]
                for file in file_list:
                    if (file != ''):
                        peer_gui.file.append(file)
                peer_gui.update_file_list()


if __name__ == "__main__":
    server_host = input('Type the server hostname: ')
    server_port = 12345
    port_self = 10000

    root = tk.Tk()
    peer_gui = PeerGUI(root, server_host, server_port, port_self)

    p1 = threading.Thread(target=discover_and_update, args=(peer_gui,))
    p1.start()

    root.mainloop()
