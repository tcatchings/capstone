#!/usr/bin/python3.4
# Brandon Randle 2016 February 12
# Last Update 2016 February 12
# A program for playing with game elements.

import logging
logging.basicConfig(filename='gamelog.log', filemode='w', level=logging.DEBUG)

class Player:
    def __init__(self):
        self.inventory = [Dagger(), 'Gold(5)', 'Crusty Bread']

    def print_inventory(self):
        logging.info('Player viewed Inventory')
        print("Inventory: ")
        for item in self.inventory:
            print("* " + str(item))

class Weapon:
    def __init__(self):
        raise NotImplementedError("Do not create raw Weapon objects.")

    def __str__(self):
        return self.name

class Dagger(Weapon):
    def __init__(self):
        self.name = "Rusty Dagger"
        self.description = "A small dagger with some rust. " \
			   "Somewhat more dangerous than a rock."
        self.damage = 10
'''
class MapTile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
	
    def intro_text(self):
	raise NotImplementedError("Create a subclass instead!")

class StartTile(MapTile):
    def intro_text(self):
	return """
		You find yourself in a cave with a flickering torch on the wall.
		You can make out four paths, each equally as dark and foreboding.
               """

class BoringTile(MapTile):
    def intro_text(self):
	return """
		This is a very boring part of the cave.
               """

class VictoryTile(MapTile):
    def intro_text(self):
	return """
		You see a bright light in the distance...
		...it grows as you get closer! It's sunlight!

		Victory is yours!
		"""
'''
def play():
    print("Escape from Cave Terror!")
    player = Player()
    running = 1
	
    while running:
        action_input = get_player_command()
        if action_input in ['n', 'N']:
            logging.info('Player has gone north')
            print("Go north!")
        elif action_input in ['s', 'S']:
            print("Go south!")
        elif action_input in ['e', 'E']:
            print("Go east!")
        elif action_input in ['w', 'W']:
            print("Go west!")
        elif action_input in ['i', 'I']:
            player.print_inventory()
        elif action_input in ['quit', 'exit', 'q','qq']:
            print("Farewell for now!")
            running = 0
        else:
            print("Invalid action!")

def get_player_command():
    return input("Action: ")

play()
