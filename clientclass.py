#!/usr/bin/python3.5
# Brandon Randle 2016 September 20
# Last Update 2016 September 20
''' This module contains the Client class. '''

import threading

class Client(threading.Thread):

    # CLIENT FUNCTIONALITY

    def __init__(self, client, address, server):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.server = server
        self.size = 1024
        self.name = str(address)
        self.commands = {'hello': self.greetEarthling, 'quit': self.quit}

    def run(self):
        ''' This method runs the client connection loop. '''
        running = 1
        while running:
            data = self.client.recv(self.size)
            data = self.parser(data)

            if data:
                self.interpreter(data)
                print("Data received from " + self.name + " : " + data)
            else:
                self.client.close()
                print("Client closed: " + str(self.address))
                self.server.broadcast(self.name + ' disconnected.', self.client)
                running = 0

    def interpreter(self, data):
        ''' This method interprets commands sent from the client. If a match is found
            in the command dictionary, it is executed. Otherwise, the data is broadcast
            to all connected clients.
        '''

        if data in self.commands:
            self.commands[data]()
        else:
            self.server.broadcast(data, self.client)

    def parser(self, data):
        ''' This method parses the data received from the clent into interpretable strings. '''

        data = str(data.decode('ascii'))
        data = data.split()
        data = data[0]
        return data

    # CLIENT COMMANDS

    def greetEarthling(self):
        ''' This method sends the client a greeting. '''
        self.server.message('Greetings, Earthling.', self.client)

    def quit(self):
        ''' This method disconnects the client and notifies the server and connected clients. '''

        self.server.message('Farewell!', self.client)
        self.server.broadcast(self.name + ' disconnected.', self.client)
        self.client.close()
        print("Client closed: " + str(self.address))

if __name__ == '__main__':
    print("This is not an exectuable program. Please run server.py instead.")
