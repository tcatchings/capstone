#!/usr/env/bin python3.5

class Item( object ):
    def __init__(self):
        self.id = None
    def __call__(self, id=None):
        if id is None:
            return self.id
        else:
            self.id = id