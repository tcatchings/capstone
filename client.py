#!/usr/bin/python3.5
# Brandon Randle 2016 September 20
# Last Update 2016 October 11
''' This module contains the Client class. '''

import re
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
        self.commandlist = {'say': self.say}

    def run(self):
        ''' This method runs the client connection loop. '''
        
        running = 1
        self.server.message('Please use SETNAME <yourname> to set a username.', self.client)
        while running:
            data = self.client.recv(self.size)
            data = data.decode()

            if data:
                self.interpreter(data)
                print("Data received from " + self.name + ": " + data)
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
            self.server.message("There is no such command. ", self.client)

    ### CLIENT COMMMANDS

    def say(self, data):
        self.server.broadcast(data, self.client, self.name)



if __name__ == '__main__':
    print("This is not an exectuable program. Please run server.py instead.")
