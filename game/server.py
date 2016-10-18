#!/usr/bin/env python3

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:4000")

while True:
    message = socket.recv()
    print("Received request: %s" % message)
    time.sleep(1)
    socket.send(b"World")
