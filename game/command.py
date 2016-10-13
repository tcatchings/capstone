#!/usr/bin/env python3.5
'''
This module contains all commands usable by the clients.
'''

import re

# FUNCTIONALITY
def commandlist():
    ''' This function returns a list of commands for the client to use. '''
    commandlist = {'say': say, 'quit': quit}
    return commandlist

def interpreter(client, clientname, socket, data):
    ''' This method interprets the data received from the client and runs the asscociated command. '''
    for command in client.commandlist:
        commandinput = r"^(" + command + r")(.*)"
        matchObj = re.match(commandinput, data)
        if matchObj:
            if matchObj.group(2): # If the client's command includes an argument.
                client.commandlist[command](client, clientname, socket, matchObj.group(2))
                break
            else:
                client.commandlist[command](client, clientname, socket)
                break
    if matchObj == None:
        client.server.broadcast("There is no such command.", socket, clientname, 'client')

# COMMANDS
def say(client, clientname, socket, data):
    ''' This function broadcasts a message to call connected clients. '''
    client.server.broadcast(data, client, clientname)

def quit(client, clientname, socket):
    ''' This function disconnects the client from the server. '''
    client.server.broadcast("Disconnecting...", socket, clientname, 'client')
    socket.close()
    client.server.broadcast(clientname + " disconnected.", socket, clientname)
    client.running = False
