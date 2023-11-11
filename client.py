import socket
import threading
import sys
import os
import shutil

file_map = {}
exit_event = threading.Event()
sep = '<sep>'

# role server to listen discover from server-side and fetch for transfer file with other client!
class Server:

    def __init__(self, server_host, server_port):
        self.file_map = {}
        self.host = server_host
        self.port = server_port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)
            sock.settimeout(1)

            while not exit_event.is_set():
                try:
                    conn, addr = sock.accept()
                except socket.timeout:
                    if exit_event.is_set():
                        break
                    else:
                        continue

                connection_thread = threading.Thread(target=self.handle_connection, args=(conn, addr))
                connection_thread.start()

    def handle_connection(self, conn, addr):
        mess = conn.recv(1024).decode()
        mess_arr = mess.split(sep)
        print(mess)
        
        if mess_arr[0] == "discover":
            file_list = []
            path_check = os.path.join(os.getcwd(), 'repository')
            if os.path.exists(path_check):
                file_list = os.listdir(path_check)

            conn.send(f"discover{sep}{file_list}".encode())
        elif mess_arr[0] == 'fetch':
            fname = mess_arr[1]
            # send file with size = 1024
            with open(os.path.join('repository', fname), 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    else:
                        conn.send(data)
        else:
            conn.send(f"discover{sep}Have error!".encode())

        conn.close()

# role act some command require in client-side!
class Client:

    def __init__(self, command):
        self.command = command
        self.arrCommand = command.strip().split(' ')

    def check_valid_command(self): # Is command valid?
        if self.arrCommand[0] == 'publish' and len(self.arrCommand) != 3:
            print('Command invalid - publish')
            return False
        elif self.arrCommand[0] == 'fetch' and len(self.arrCommand) != 2:
            print('Command invalid - fetch')
            return False
        return True

    def handler_file(self, dir_check):
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]
        try:
            shutil.copyfile(lname, os.path.join(dir_check, fname))
        except FileNotFoundError:
            print(f'The file "{lname}" does not exist.')

    def publish(self, host, port):
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]

        dir_check = os.path.join(os.getcwd(), 'repository')
        if not os.path.exists(dir_check):
            os.mkdir('repository')
        elif not os.path.exists(lname):
            print('The lname is an invalid path')
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            send_seg = 'publish' + sep + fname
            sock.connect((host, port))
            sock.send(send_seg.encode())

            status = sock.recv(1024).decode()
            print(status)
            if status == '200':
                self.handler_file(dir_check)
                print('Success - fetch!')
            sock.close()

    def fetch(self, host, port, port_transfer):
        fname = self.arrCommand[1]
        hostname_fname = '-1' # default value
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.send(f"fetch{sep}{fname}".encode())

            mess_rcv = sock.recv(1024).decode() # if file is have in remote, it send rcv form: fetch<sep>hostname like fetch<sep>192.168.1.9
            arr_mess = mess_rcv.split(sep)
            if len(arr_mess) == 3 and arr_mess[1] == '404':
                print(arr_mess[2])
            else:
                hostname_fname = arr_mess[1]
        if hostname_fname == '-1':
            print('------------')
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((hostname_fname, port_transfer))
                sock.send(f"fetch{sep}{fname}".encode())
                # if dont have Download folder, create Download folder
                download_folder = os.path.join(os.getcwd(), 'Download')
                if not os.path.exists(download_folder):
                    os.mkdir(download_folder)
                with open(os.path.join(download_folder, fname), 'wb') as f:
                    while True:
                        data = sock.recv(1024) 
                        if not data:
                            break
                        f.write(data)


if __name__ == '__main__':
    host = input('Type the server hostname: ') #the server hostname
    port = 12345 # port connect with server 

    host_self = '0.0.0.0' # listen hostname
    port_self = 10000 #port for listen! transfer file(fetch) and discover(from server)!

    print('[+] This is a system for sharing files:')
    print('\t[-] Command list:')
    print('\t. publish <lname:link to file> <fname>')
    print('\t. fetch <fname>')
    print('\t. out')

    server = Server(host_self, port_self)
    

    p1 = threading.Thread(target=server.start)
    p1.start()

    while True:
        command = input('[-] Command: ')
        client = Client(command)
        if command.strip() == 'out':
            if os.path.exists(os.path.join(os.getcwd(), 'repository')):
                shutil.rmtree('repository')
            exit_event.set()
            p1.join()
            sys.exit(1)
        elif client.check_valid_command():
            if command.startswith("publish"):
                client.publish(host, port)
            elif command.startswith('fetch'):
                client.fetch(host, port, port_self)
        else:
            print('Command invalid - no command')
