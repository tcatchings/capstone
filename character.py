#!/usr/env/bin python3.5
import yaml

class Player:
    def __init__(self):
        f = open('player.yaml','r')
        data = yaml.load(f)
        for key, value in data.items():
            self.name = data['name']
            self.location = data['location']
            self.items = str(data['items'])
    def status(self):
        print("""Your name is """ + self.name + """, you are currently standing at \n"""
        + self.location + """. \nThis is your current inventory: \n""" + self.items)

x = Player()
x.status()