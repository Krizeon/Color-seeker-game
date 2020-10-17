from constants import SCREEN_WIDTH
from constants import SCREEN_HEIGHT
from main import GameView
import arcade as ar

# import arcade.gui
# from arcade.gui import UIManager

class MenuView(ar.View):
    """
    View to show game menu
    Displays an Arcade View window to show a menu view
    """
    def on_show(self):
        ar.set_background_color(ar.color.WHITE)

    def on_draw(self):
        ar.start_render()
        ar.draw_text("Menu Screen", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         ar.color.BLACK, font_size=50, anchor_x="center")
        ar.draw_text("Click to advance.", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-75,
                         ar.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game = GameView()
        game.setup()
        self.window.show_view(game)


class WinView(ar.View):
    """
    View to show game menu
    Displays an Arcade View window to show a menu view
    """
    def on_show(self):
        ar.set_background_color(ar.color.GREEN)

    def on_draw(self):
        ar.start_render()
        ar.draw_text("You win!!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         ar.color.BLACK, font_size=50, anchor_x="center")
        ar.draw_text("Click screen to quit.", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-75,
                         ar.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game = GameView()
        game.setup()
        self.window.show_view(game)


class InstructionView(ar.View):
    """
    View to show instructions
    Displays an Arcade View window to show an instructions view
    """

    def on_show(self):
        """ This is run once when we switch to this view """
        ar.set_background_color(ar.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        ar.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        ar.start_render()
        ar.draw_text("Use arrow keys or WASD to move", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         ar.color.WHITE, font_size=40, anchor_x="center")
        ar.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         ar.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

class PauseView(ar.View):
    """ View to show the pause screen """

    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        """ This is run once when we switch to this view """
        ar.set_background_color(ar.csscolor.BLACK)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        ar.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        ar.start_render()
        ar.draw_text("Game Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         ar.color.WHITE, font_size=40, anchor_x="center")
        ar.draw_text("Press P to resume game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         ar.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        """ If the user presses the mouse button, start the game. """
        if symbol == ar.key.P:
            self.window.show_view(self.game_view)

