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
            print('Command invalid - publish')
            return False
        elif self.arrCommand[0] == 'fetch' and len(self.arrCommand) != 2:
            print('Command invalid - fetch')
            return False
        return True
    def handlerFile(self, dircheck):
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]
        shutil.copyfile(lname, os.path.join(dircheck, fname))
    
    def publish(self, host, port):
        # get lname and fname
        lname = self.arrCommand[1]
        fname = self.arrCommand[2]

        # check dir path
        dircheck =os.path.join(os.getcwd(), 'repository')
        if not os.path.exists(dircheck):
            os.mkdir('repository')
        elif not os.path.exists(lname):
            print('the lname is a invalid path')
            return
        
        # check fname valid before sending to the server!
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sendSeg = 'publish' + sep + fname # merge sender
            sock.connect((host, port))
            sock.send(sendSeg.encode())
                
            status = sock.recv(1024).decode()
            print(status)
            if status == '200': 
                self.handlerFile(dircheck)
                print('success - fetch!')

    def fetch(self, host, port):
        pass
if __name__ == '__main__':
    host = '192.168.0.100'
    port = 12345
    print('[+] This is system for sharing file:')
    print('\t[-] Command list:')
    print('\t. publich <lname> <fname>')
    print('\t. fetch <fname>')
    print('\t. out')
    while True:
        command = input('[-] Command: ')
        server=Client(command)
        if command.startswith("publish") and server.checkvalidcommand():
            server.publish(host, port)
        elif command.startswith('fetch') and server.checkvalidcommand():
            server.fetch(host, port)
        elif command.strip() == 'out':
            shutil.rmtree('repository')
            sys.exit(1)
        else:
            print('Command invalid - no command')

    