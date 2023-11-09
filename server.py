import socket
import threading
import sys
import time

sep = '<sep>'
file_map = {}  # ele follows the form: {fname: (addr, port)}
exit_event = threading.Event()  # Shared event to signal all threads to exit

class MyServer:
    def __init__(self, host, port, max_threads):
        self.host = host
        self.port = port
        self.max_threads = max_threads

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

        # print connect info
        print(f"\n{conn} -- {addr}")
        # check command
        if arr_send[0] == 'publish':
            file_map[arr_send[1]] = addr[0]
            print(f"\n--{addr}--")
            conn.send('200'.encode())
        elif arr_send[0] == 'fetch':
            pass

    def stop(self):
        exit_event.set()

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 12345
    max_threads = 10

    server = MyServer(host, port, max_threads)
    p2 = threading.Thread(target=server.start)

    p2.start()

    print('[+] This is the server-side of the file transfer system')
    print('\t[-] Command List:')
    print('\t. discover <hostname>')
    print('\t. ping <hostname>')
    print('\t. out')

    while True:
        command = input('[-] Type a command (or "out" to exit): ')

        if command.startswith('discover'):
            print('you type the discover command')
        elif command == 'out':
            server.stop()
            p2.join()
            sys.exit(0)
