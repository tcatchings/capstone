#!/usr/bin/python3.5
# Brandon Randle 2016 February 10
# Last Update 2016 September 13 
# A script to play with threaded servers.
'''
This module hosts a threaded server, where the Server object creates new Client objects that
run on their own threads.
'''

import select
import socket
import sys
import threading

class Server:
    def __init__(self):
        self.host = self.sethost()
        self.port = self.setport()
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def setport(self):
        ''' This method sets a default port if a port is not provided on the command line.'''
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 4000 
        return port

    def sethost(self):
        ''' This method sets a default host if a host is not provided on the command line.'''
        if len(sys.argv) > 2: 
            host = sys.argv[2]
        else:
            host = 'localhost'
        return host

    def open_socket(self):
        ''' This method trys to open a listening socket. In case of failure, it closes the socket and shuts down the server.'''
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(self.backlog)
            print("Server begun. Host: " + str(self.host) + " Port: " + str(self.port))
        except socket.error(value,message):
            if self.server:
                self.server.close()
                print("Could not open socket: " + message)
                sys.exit(1)

    def run(self):
        ''' This method runs the server loop. It opens a listening socket with open_socket(), then listens as long as running is true. '''
        self.open_socket()
        input = [self.server,sys.stdin]
        running = 1
        while running:
            inputready, outputready, exceptready = select.select(input, [], [])

            for s in inputready:
                if s == self.server:
                    client, address = self.server.accept()
                    c = Client(client, address, self)
                    c.start()
                    self.threads.append(c)
                    print("New client connected: " + str(c.address))
                elif s == sys.stdin:
                    junk = sys.stdin.readline()
                    running = 0

        self.server.close()

        for c in self.threads:
            c.join()

    def broadcast(self, message, client):
        ''' This method broadcasts a message to all clients currently connected. '''
        for socket in self.threads:
            if socket != self.server and socket != sys.stdin:
                try:
                    socket.client.send(message)
                except:
                    socket.client.close()
                    if socket in self.threads:
                        self.threads.remove(socket)


class Client(threading.Thread):
    def __init__(self,client,address,server):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.server = server
        self.size = 1024
        self.name = str(address)

    def run(self):
        ''' This method runs the client connection loop. It will close the client socket when it detects no incoming data. '''
        running = 1
        while running:
            data = self.client.recv(self.size)
            if data:
                self.server.broadcast(data, self.client)
                print("Data Received: " + str(data.decode('ascii')))
            else:
                self.client.close()
                print("Client closed: " + str(self.address))
                running = 0

if __name__ == "__main__":
    s = Server()
    s.run()
