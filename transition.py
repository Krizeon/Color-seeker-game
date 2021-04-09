"""
class that holds the transition between levels screen
"""

from constants import *
import arcade.color as ar

class Transition:
    """
    Class to keep track of a ball's location and vector.
    """

    def __init__(self):
        self.center_x = 0
        self.center_y = 0
        self.width = 0
        self.height = 0
        self.change_x = 0
        self.change_y = 0
        self.color = None

    def setup(self):
        self.center_x = -SCREEN_WIDTH
        self.center_y = 0
        self.width = SCREEN_WIDTH * 2
        self.height = SCREEN_HEIGHT
        self.change_x = SCREEN_WIDTH / 20
        self.change_y = SCREEN_WIDTH / 30
        self.color = ar.AZURE