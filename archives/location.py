#!usr/bin/python3.5
# Brandon Randle 2016 October 11
# Last Update 2016 October 11
'''
This module contains the class for locations.
'''

class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def intro_text(self):
        raise NotImplementedError("Create a subclass instead!")

class MapTile_Plain(Location):
    def intro_text(self):
            return """
            You find yourself in the start location.
            """



if __name__ == "__main__":
    print("This module is meant to be imported to server.py, not run on its own.")
