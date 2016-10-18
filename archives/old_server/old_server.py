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
import bcrypt
import yaml

logging.basicConfig(filename='log.log', level=logging.DEBUG)

class Server:
    def __init__(self):
        self.host = self.sethost()
        self.port = self.setport()
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.users = self.loadUsers()

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
                    self.saveUsers()
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

    def loadUsers(self):
        with open('users.yaml', 'r') as users:
            userdict = yaml.load(users)
            print("Users loaded: " + str(userdict))
        return userdict

    def saveUsers(self):
        with open('users.yaml', 'w') as users:
            yaml.dump(self.users, users, default_flow_style=False)

    def loadMap(self):
        return [
                [None, location.MapTile_Plain(1,0), None],
                [None, location.MapTile_Plain(1,1), None],
                [location.MapTile_Plain(0,2), location.MapTile_Plain(1,2), location.MapTile_Plain(2,2)],
                [None, location.MapTile_Plain(1,3), None]
        ]

    def tileAt(self, x, y):
        if x < 0 or y < 0:
            return None
        try:
            return self.worldmap[y][x]
        except IndexError:
            return None


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
        self.commandlist = {
            'say': self.say, 
            'quit': self.quit, 
        }
        self.running = True


    def run(self):
        ''' This method runs the client connection loop. '''

        self.loginPrompt()

        while self.running:
            data = self.receiveData()

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
            commandinput = r'^(' + command + r')(.*)'
            # Question...weird results with setname() with (.*) matching...
            matchObj = re.match(commandinput, data)
            if matchObj:
                if matchObj.group(2):
                    self.commandlist[command](matchObj.group(2))
                    break
                else:
                    self.commandlist[command]()
                    break
        if matchObj == None:
            self.server.message("There is no such command. ", self.client, self.name)

    def loginPrompt(self):
        login_running = True
        password_running = True
        while login_running:
            self.server.message('Please enter your username: ', self.client, self.name)
            username = self.receiveData()
            pattern = r'' + username 
            if [key for key, value in self.server.users.items() if re.search(pattern, key)]: 
                while password_running:
                    self.server.message('Password: ', self.client, self.name)
                    password = self.receiveData()
                    if bcrypt.checkpw(password, self.server.users[username]):
                        self.server.message('Login successful. Welcome to the server.\n', self.client, self.name)
                        self.name = username
                        login_running = False
                        password_running = False
                    else: 
                        self.server.message('Password incorrect.', self.client, self.name)
            else:
                self.createUserPrompt(username)

    def createUserPrompt(self, username):
        self.server.message('This user does not exist. Create new user? (y/n)', self.client, self.name)
        creatingUser = True
        while creatingUser:
            data = self.receiveData()
            if data == 'y':
                self.server.message('Creating new user with username "' + username + '". \nEnter your new password: ', self.client, self.name)
                password = bcrypt.hashpw(self.receiveData().encode(), bcrypt.gensalt())
                if password:
                    self.server.users[username] = password
                    self.server.message('User created. Returning to login prompt...', self.client, self.name)
                    self.server.saveUsers()
                    creatingUser = False
            elif data == 'n':
                self.server.message('New user creation declined. Returning to login prompt.', self.client, self.name)
                creatingUser = False
            else:
                self.server.message('Input invalid. You must use y or n. ', self.client, self.name)

    def receiveData(self):
        data = self.client.recv(self.size)
        data = data.decode()
        data = data.strip()
        return data



    ### CLIENT COMMMANDS

    def say(self, data):
        self.server.broadcast(data, self.client, self.name)

    def quit(self):
        self.server.message('Disconnecting...', self.client, self.name)
        self.client.close()
        self.server.broadcast(self.name + ' disconnected.', self.client, self.name)
        self.running = False

if __name__ == "__main__":
    s = Server()
    s.run()
