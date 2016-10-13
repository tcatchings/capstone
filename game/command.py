#!/usr/bin/env python3.5
'''
This module contains all commands usable by the clients.
'''

def say(client, clientname, socket, data):
    client.server.broadcast(data, client, clientname)

def quit(client, clientname, socket):
    client.server.broadcast("Disconnecting...", socket, clientname, 'client')
    socket.close()
    client.server.broadcast(clientname + " disconnected.", socket, clientname)
    client.running = False
