#!/usr/bin/env python3

import zmq

context = zmq.Context()

print("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:4000")

for request in range(10):
    print("Senidng request %s ..." % request)
    socket.send(b"Hello")

    message = socket.recv()
    print("Recieved reply %s [ %s ]" % (request, message))
