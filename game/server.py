#!user/bin/env python3.5
"""
This module handles all of the server networking, including
receiving connections and creating a thread for each client
to handle communication between client and server.
"""

import select
import socket
import sys
import threading
import logging
import re
import command

logging.basicConfig(filename="logs/server.log", level=logging.DEBUG)

class Server:

    def __init__(self):
        self.host = self.sethost()
        self.port = self.setport()
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def setport(self):
        ''' This method sets a default port if a port is not provided on the command line. '''
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        else:
            port = 4000
        return port

    def sethost(self):
        ''' This method sets a default host if a host is not provided on the command line. '''
        if len(sys.argv) > 2:
            host = sys.argv[2]
        else:
            host = 'localhost'
        return host

    def open_socket(self):
        ''' This method trys to open a listening socket. In case of failure, it closes the socket and shuts down the server. '''
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(self.backlog)
            
            print("Server begun. Host: " + str(self.host) + " Port: " + str(self.port))
            logging.info("SERVER BEGUN. HOST: " + str(self.host) + " PORT: " + str(self.port))

        except socket.error(value,message):
            if self.server:
                self.server.close()
                print("Could not open socket: " + message)
                logging.critical("Could not open socket: " + message)
                sys.exit(1)

    def run(self):
        ''' This method runs the server loop. It opens a listening socket with open_socket(), then listens as long as running is true. '''
        self.open_socket()
        input = [self.server,sys.stdin]
        running = True
        while running:
            inputready, outputready, exceptready = select.select(input, [], [])

            for s in inputready:
                if s == self.server:
                    client, address = self.server.accept()
                    c = Client(client, address, self)
                    c.start()
                    self.threads.append(c)

                    print("New client connected: " + str(c.address))
                    logging.info("New client connected: " + str(c.address))
                elif s == sys.stdin:
                    logging.info("Server shutdown request received from server. Shutting down once all clients disconnect.")
                    junk = sys.stdin.readline()
                    running = False

        self.server.close()

        for c in self.threads:
            c.join()

    def broadcast(self, message, client, clientname, audience="allclients"):
        ''' This method sends messages to clients. The audience for the message is specified as either a single client or all connected clients. '''
        if audience == "client":
            message = message + "\n"
            try:
                client.send(message.encode())
                print("Sending message to " + clientname + ": " + message.strip('\n'))
                logging.info("Sending message to " + clientname + ": " + message.strip('\n'))
            except:
                print("Error sending message to " + clientname + ". Closing socket.")
                logging.error("Error sending message to " + clientname + ". Closing socket.")
                client.close()
                if client in self.threads:
                    self.threads.remove(client)
        else:
            message = "\n" + clientname + ": " + message + "\n>"
            print("Sending message to all clients: " + message.strip("\n> "))
            logging.info("Sending message to all clients: " + message.strip("\n> "))
            for socket in self.threads:
                if socket != self.server and socket != sys.stdin:
                    try:
                        socket.client.send(message.encode())
                    except:
                        print("Error broadcasting message to " + clientname + ". Closing socket.")
                        logging.error("Error broadcasting message to " + clientname + ". Closing socket.")
                        socket.client.close()
                        if socket in self.threads:
                            self.threads.remove(socket)

class Client(threading.Thread):

    def __init__(self, client, address, server):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.server = server
        self.size = 1024
        self.name = str(address)
        self.running = True
        self.commandlist = {'say': command.say, 'quit': command.quit}

    def run(self):
        ''' This method runs the client connection loop. '''

        while self.running:
            data = self.receiveData()
            if data:
                print("Data received from " + self.name +": " + data.strip("\n"))
                logging.info("Data received from " + self.name + ": " + data.strip("\n"))
                self.interpreter(data)
            else:
                self.client.close()
                print("Client closed: " + str(self.address))
                logging.info("Client closed: " + str(self.address))
                self.server.broadcast(self.name + " disconnected.", self.client, self.name)
                running = False

    def interpreter(self, data):
        ''' This method interprets the data received from the client. '''
        for command in self.commandlist:
            commandinput = r"^(" + command + r")(.*)"
            matchObj = re.match(commandinput, data)
            if matchObj:
                if matchObj.group(2): # If the client's command includes an argument.
                    self.commandlist[command](self, self.name, self.client, matchObj.group(2))
                    break
                else:
                    self.commandlist[command](self, self.name, self.client)
                    break
        if matchObj == None:
            self.server.broadcast("There is no such command.", self.client, self.name, 'client')

    def receiveData(self):
        data = self.client.recv(self.size)
        data = data.decode()
        data = data.strip()
        return data

        

if __name__ == "__main__":
    s = Server()
    s.run()
