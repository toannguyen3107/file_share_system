import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import socket
import sys
import os

sep = '<sep>'
file_map = {}  # ele follows the form: {fname: (addr, port)}
host_conn = []
exit_event = threading.Event()  # Shared event to signal all threads to exit

class MyServer:
    def __init__(self, host, port, terminal_text):
        self.file_list = ""
        self.host = host
        self.port = port
        self.connected_peers = []
        self.terminal_text = terminal_text

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)
            sock.settimeout(1)  # Set a timeout for accept

            while not exit_event.is_set():
                try:
                    conn, addr = sock.accept()
                except socket.timeout:
                    # Check for the exit event during the timeout
                    if exit_event.is_set():
                        break
                    else:
                        continue

                connection_thread = threading.Thread(target=self.handle_connection, args=(conn, addr))
                connection_thread.start()

    def handle_connection(self, conn, addr):
        send_seg = conn.recv(1024).decode()
        arr_send = send_seg.strip().split(sep)

        if arr_send[0] == 'update':
            file_list = ""
            for file in file_map:
                if (file_map[file] != addr[0]):
                    file_list += file + sep
            if (file_list != ""):
                print(file_list)
                conn.send(f"update{sep}{file_list}".encode())
            else: 
                conn.send("empty".encode())
            return
        
        if addr[0] not in host_conn:
            host_conn.append(addr[0])
            self.connected_peers.append(addr[0])

        # print connect info
        connect_info = f"\n {addr[0]} is connected"
        print(connect_info)
        self.terminal_text.insert(tk.END, connect_info + '\n')
        # check command
        if arr_send[0] == 'publish':
            # add to file list
            # self.file_list += str(arr_send[1]) + sep
            # print(self.file_list)
            #
            file_map[arr_send[1]] = addr[0]
            file_map_text = f"Current file map: {file_map}"
            print(file_map_text)
            # send file list to peer
            file_list = ""
            for file in file_map:
                if (file_map[file] != addr[0]):
                    file_list += file + sep
            ###
            self.terminal_text.insert(tk.END, file_map_text + '\n')
            conn.send('200'.encode())
            conn.send(file_list.encode())
            
        elif arr_send[0] == 'fetch':
            fname = arr_send[1]
            host = '-1' #default '-1'
            if fname in file_map:
                conn.send(f"fetch{sep}{file_map[fname]}".encode())
            else:
                conn.send(f"fetch{sep}404{sep}File Not Found!".encode())
        elif arr_send[0] == 'discover':
            file_list = ""
            for file in file_map:
                if (file_map[file] != addr[0]):
                    file_list += file + sep
            # print(file_list)
            if (file_list != ""):
                print(file_list)
                conn.send(f"discover{sep}{file_list}".encode())
    
    def ping(self, host):
        # white list - security
        if host in host_conn:
            os.system(f"ping -c 3 {host}")
        else:
            print("Host isn't connected or host error syntax ipv4!")

    def discover(self, host):
        if host in host_conn:
            discover_message = "discover"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((host, 10000))
                sock.send(discover_message.encode())

                mess = sock.recv(1024).decode()
                mess_split = mess.split(sep)
                if mess_split[0] == "discover":
                    discover_text = f"\n-----------\nList fname from {host}: {mess_split[1]}"
                    print(discover_text)
                    self.terminal_text.insert(tk.END, discover_text + '\n')


    def stop(self):
        exit_event.set()


class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Server GUI")
        self.server_thread = None

        self.create_widgets()
        self.server = MyServer('0.0.0.0', 12345, self.terminal_text)
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.start()
        self.update_peer_list()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Server Commands:")
        self.label.pack(pady=10)

        self.start_button = tk.Button(self.master, text="Refresh", command=self.update_peer_list)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.master, text="Stop Server", command=self.stop_server)
        self.stop_button.pack(pady=10)

        self.peer_listbox = tk.Listbox(self.master)
        self.peer_listbox.pack(pady=10)
        
        self.terminal_text = scrolledtext.ScrolledText(self.master, width=50, height=15)
        self.terminal_text.pack(pady=10)

        self.ping_button = tk.Button(self.master, text="Ping", command=self.ping_selected_peer)
        self.ping_button.pack(pady=5)

        self.discover_button = tk.Button(self.master, text="Discover", command=self.discover_selected_peer)
        self.discover_button.pack(pady=5)

        self.exit_button = tk.Button(self.master, text="Exit", command=self.exit_program)
        self.exit_button.pack(pady=10)

    def stop_server(self):
        if self.server_thread:
            self.server.stop()
            self.server_thread.join()
        sys.exit(0)

    def update_peer_list(self):
        self.peer_listbox.delete(0, tk.END)
        for peer in self.server.connected_peers:
            self.peer_listbox.insert(tk.END, peer)

    def ping_selected_peer(self):
        selected_index = self.peer_listbox.curselection()
        if selected_index:
            selected_peer = self.peer_listbox.get(selected_index)
            self.server.ping(selected_peer)

    def discover_selected_peer(self):
        selected_index = self.peer_listbox.curselection()
        if selected_index:
            selected_peer = self.peer_listbox.get(selected_index)
            self.server.discover(selected_peer)

    def exit_program(self):
        if self.server_thread:
            self.server.stop()
            self.server_thread.join()
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()
