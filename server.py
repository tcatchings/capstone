#!/usr/bin/python3.5
# Brandon Randle 2016 February 10
# Last Update 2016 October 11
'''
This module hosts a threaded server, where the Server object creates new Client objects that
run on their own threads.
'''

import select
import socket
import sys
import threading
import re
import logging

logging.basicConfig(filename='server.log', level=logging.DEBUG)

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
            logging.info('SERVER BEGUN. HOST: ' + str(self.host) + ' PORT: ' + str(self.port))
        except socket.error(value,message):
            if self.server:
                self.server.close()
                print("Could not open socket: " + message)
                logging.critical('Could not open socket: ' + message)
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
                    logging.info('New client connected: ' + str(c.address))
                elif s == sys.stdin:
                    logging.info('Server shutdown request received from server. Shutting down once all clients disconnect.')
                    junk = sys.stdin.readline()
                    running = 0

        self.server.close()

        for c in self.threads:
            c.join()

    def broadcast(self, message, client, clientname):
        ''' This method broadcasts a message to all clients currently connected. '''
        message = "\n" +clientname + ": " + message + '\n>' #Adds a newline to every message sent to client.
        print('Sending message to all clients: ' + message.strip('\n> '))
        logging.info('Sending message to all clients: ' + message.strip('\n> '))
        for socket in self.threads:
            if socket != self.server and socket != sys.stdin:
                try:
                    socket.client.send(message.encode())
                except:
                    print('Error broadcasting message from ' + clientname + '. Closing socket.')
                    logging.error('Error broadcasting message from ' + clientname + '. Closing socket.')
                    socket.client.close()
                    if socket in self.threads:
                        self.threads.remove(socket)

    def message(self, message, client, clientname):
        ''' This method sends a message to only the client specified. '''
        message = message + '\n'
        try:
            client.send(message.encode())
            print('Sending message to ' + clientname + ": " + message.strip('\n'))
            logging.info('Sending message to ' + clientname + ': ' + message.strip('\n'))
        except:
            print('Error sending message to ' + clientname + '. Closing socket.')
            logging.error('Error sending message to ' + clientname + '. Closing socket.')
            client.close()
            if client in self.threads:
                self.threads.remove(client)

# CLIENT CLASS

class Client(threading.Thread):

    # CLIENT FUNCTIONALITY

    def __init__(self, client, address, server):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.server = server
        self.size = 1024
        self.name = str(address)
        self.commandlist = {'say': self.say}


    def run(self):
        ''' This method runs the client connection loop. '''

        running = 1
        self.server.message('Please use SETNAME <yourname> to set a username.', self.client, self.name)
        while running:
            data = self.client.recv(self.size)
            data = data.decode()

            if data:
                print("Data received from " + self.name + ": " + data.strip('\n'))
                logging.info('Data received from ' + self.name + ': ' + data.strip('\n'))
                self.interpreter(data)
            else:
                self.client.close()
                print("Client closed: " + str(self.address))
                self.server.broadcast(self.name + ' disconnected.', self.client, self.name)
                running = 0

    def interpreter(self, data):

        for command in self.commandlist:
            commandinput = r'^(' + command + r') (.*)'
            # Question...weird results with setname() with (.*) matching...
            matchObj = re.match(commandinput, data)
            if matchObj:
                self.commandlist[command](matchObj.group(2))
                break
        if matchObj == None:
            self.server.message("There is no such command. ", self.client, self.name)

    ### CLIENT COMMMANDS

    def say(self, data):
        self.server.broadcast(data, self.client, self.name)

if __name__ == "__main__":
    s = Server()
    s.run()
