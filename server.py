import socket
import threading
import multiprocessing
import concurrent.futures

sep = '<sep>'

file_map = {} # ele follow form: {fname: (addr, port)}

class MyServer:
    
    def __init__(self, host, port, max_threads):
        self.host = host
        self.port = port
        self.max_threads = max_threads

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)

            accept_thread = threading.Thread(target=self.accept_connections, args=(sock,))
            accept_thread.start()
            accept_thread.join()

    def handle_connection(self, conn, addr):
        # Your code to handle the connection goes here
        sendSeg = conn.recv(1024).decode()
        arrSend = sendSeg.strip().split(sep)
        
        if arrSend[0] == 'publish':
            file_map[arrSend[1]] = addr[0]
        elif arrSend[0] == 'fetch':
            pass
    def accept_connections(self, sock):
        # Threadpool - using though module!
        with concurrent.futures.ThreadPoolExecutor(self.max_threads) as executor:
            while True:
                conn, addr = sock.accept()
                executor.submit(self.handle_connection, conn, addr)
def commandProcess():
    print('[+] This server-side of file transfer system')
    print('\t[-] Command List:')
    print('\t. discover <hostname>')
    print('\t. ping <hostname>')
    command = input('\t[-] Type command: ')
    if command.startswith('discover'):
        print('discover command!')
if __name__ == "__main__":
    host = '0.0.0.0'
    port = 12345
    max_threads = 10

    p1 = multiprocessing.Process(target=commandProcess())

    server = MyServer(host, port, max_threads)
    p2 = multiprocessing.Process(target=server.start())
    
    p1.start()
    p2.start()


    p1.join()
    p2.join()


