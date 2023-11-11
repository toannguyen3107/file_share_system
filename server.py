import socket
import threading
import sys
import os
sep = '<sep>'
file_map = {}  # ele follows the form: {fname: (addr, port)}
host_conn = []
exit_event = threading.Event()  # Shared event to signal all threads to exit

class MyServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

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

        if addr[0] not in host_conn:
            host_conn.append(addr[0])

        # print connect info
        print(f"\n {addr[0]} is connected")
        # check command
        if arr_send[0] == 'publish':
            file_map[arr_send[1]] = addr[0]
            print(f"Current file map: {file_map}")
            conn.send('200'.encode())
        elif arr_send[0] == 'fetch':
            fname = arr_send[1]
            host = '-1' #default '-1'
            if file_map[fname]:
                conn.send(f"fetch{sep}{file_map[fname]}".encode())
            else:
                conn.send(f"fetch{sep}404{sep}File Not Found!")
    def ping(self, host):
        # white list - security
        if host in host_conn:
            os.system(f"ping -c 3 {host}")
        else:
            print("Host isn't connected or host error syntax ipv4!")
    def stop(self):
        exit_event.set()

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 12345

    port_self = 10000

    server = MyServer(host, port)
    p2 = threading.Thread(target=server.start)

    p2.start()

    print('[+] This is the server-side of the file transfer system')
    print('\t[-] Command List:')
    print('\t. discover <hostname>')
    print('\t. ping <hostname>')
    print('\t. out')

    while True:
        command = input('[-] Type a command (or "out" to exit): ')

        if command.startswith('ping'):
            if len(command.split()) != 2:
                continue
            else:
                hostping = command.split()[1] 
                server.ping(hostping)
        elif command.startswith('discover'):
            host_discover = command.split(' ')[1]
            print(host_discover) #test
            if host_discover in host_conn:
                discover_message = "discover"
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    print(host_discover, port_self,sep="--") #test
                    sock.connect((host_discover, port_self))
                    sock.send(discover_message.encode())

                    mess = sock.recv(1024).decode()
                    mess_split = mess.split(sep)
                    if mess_split[0] == "discover":
                        print(f"\n-----------\nList fname from {host_discover}: ",mess_split[1])
        elif command in ['out','exit','close']:
            server.stop()
            p2.join()
            sys.exit(0)
