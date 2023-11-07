import socket
import sys
import os
import shutil

file_map = {}

sep = '<sep>'

class Client:

    def __init__(self, command):
        self.command = command
        self.arrCommand = command.strip().split(' ')
    def checkvalidcommand(self):
        if self.arrCommand[0] == 'publish' and len(self.arrCommand) != 3:
            print('Command invalid')
        elif len(self.arrCommand) != 2:
            print('Command invalid')
    def handlerFile(self):
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]
        currFname = './repository'+ fname
        shutil(lname, currFname)

    def publish(self, host, port):
        # get lname and fname
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]

        pathcheck = './repository/'+ lname
        if not os.path.exists(pathcheck):
            print('the lname is a invalid path')
            sys.exit(1)
        self.handlerFile()
    # check fname valid before sending to the server!
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sendSeg = 'publish' + sep + fname # merge sender
            sock.connect((host, port))
            sock.send(sendSeg.encode())
            
            status = sock.recv(1024).decode()
            if status == 'upload fname success!': 
                file_map[fname] = './repository' + lname
                print(file_map)

    def fetch(self, host, port):
        pass
if __name__ == '__main__':
    host = '192.168.0.100'
    port = 12345

    print('[+] This is system for sharing file:')
    print('\t[-] Command list:')
    print('\t. public <lname> <fname>')
    print('\t. fetch <fname>')
    print('\t. out')
    while True:
        command = input('[-] Command: ')
        server=Client(command)
        if command.startswith("publish"):
            server.checkvalidcommand()
            server.publish(host, port)
        elif command.startswith('fetch'):
            server.checkvalidcommand()
            server.fetch(host, port)
        elif command.strip() == 'out':
            sys.exit(1)
        else:
            print('Command invalid')

    print('have problem')