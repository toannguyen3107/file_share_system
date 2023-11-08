import socket
import threading
import multiprocessing
import concurrent.futures
import queue
sep = '<sep>'

file_map = {}  # ele follow form: {fname: (addr, port)}


class MyServer:

    def __init__(self, host, port, max_threads):
        self.host = host
        self.port = port
        self.max_threads = max_threads

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)

            accept_thread = threading.Thread(
                target=self.accept_connections, args=(sock,))
            accept_thread.start()
            accept_thread.join()

    def handle_connection(self, conn, addr):
        # Your code to handle the connection goes here
        sendSeg = conn.recv(1024).decode()
        arrSend = sendSeg.strip().split(sep)

        if arrSend[0] == 'publish':
            file_map[arrSend[1]] = addr[0]
            print(f"--{addr}--")
            conn.send('200'.encode())
        elif arrSend[0] == 'fetch':
            pass

    def accept_connections(self, sock):
        # Threadpool - using though module!
        with concurrent.futures.ThreadPoolExecutor(self.max_threads) as executor:
            while True:
                conn, addr = sock.accept()
                executor.submit(self.handle_connection, conn, addr)


command_queue = queue.Queue()


def commandProcess(command_queue):
    print('[+] This is the server-side of the file transfer system')
    print('\t[-] Command List:')
    print('\t. discover <hostname>')
    print('\t. ping <hostname>')
    print('\t. out')

    while True:
        try:
            # Check if there are commands in the queue
            command = command_queue.get_nowait()
            print(f"[-] Received command: {command}")
            if command.startswith('discover'):
                print('discover command!')
        except queue.Empty:
            # No command in the queue, you can do other processing here if needed
            pass


if __name__ == "__main__":
    host = '0.0.0.0'
    port = 12345
    max_threads = 10

    p1 = multiprocessing.Process(target=commandProcess, args=(command_queue,))
    server = MyServer(host, port, max_threads)
    p2 = multiprocessing.Process(target=server.start)

    p2.start()
    p1.start()

    while True:
        # Allow the user to input commands and put them in the queue
        user_input = input('[-] Type a command (or "out" to exit): ')
        command_queue.put(user_input)

        if user_input == 'out':
            break

    p1.join()
    p2.join()
