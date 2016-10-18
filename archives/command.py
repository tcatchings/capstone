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

def interpreter(client, data):
    ''' This method interprets the data received from the client and runs the asscociated command. '''
    for command in client.commandlist:
        commandinput = r"^(" + command + r")(.*)"
        matchObj = re.match(commandinput, data)
        if matchObj:
            if matchObj.group(2): # If the client's command includes an argument.
                client.commandlist[command](client, matchObj.group(2))
                break
            else:
                client.commandlist[command](client)
                break
    if matchObj == None:
        client.server.broadcast("There is no such command.", client.client, client.name, 'client')

# COMMANDS
def say(client, data):
    ''' This function broadcasts a message to call connected clients. '''
    client.server.broadcast(data, client.client, client.name)

def quit(client):
    ''' This function disconnects the client from the server. '''
    client.server.broadcast("Disconnecting...", client.client, client.name, 'client')
    client.client.close()
    client.server.broadcast(client.name + " disconnected.", client.client, client.name)
    client.running = False
