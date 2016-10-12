#!/usr/env/bin python3.5

class Item:
    def __init__(self, desc, uuid):
        self.desc = desc #item's description (name)
        self.uuid = uuid #item's unique user ID
    def itemsList(self):
        print("Name: ",self.desc, "\nID: ",self.uuid)

#I think this is what u wanted, eh?
#x = Item('potion', '000001')
#print(x.itemsList())