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
        pass

    def on_draw(self):
        ar.start_render()
        # load title screen
        background = ar.load_texture("backgrounds/color_seeker_titlescreen.png")
        # ar.set_background_color(ar.color.GRAY)
        ar.draw_lrwh_rectangle_textured(0, 0,
                                        SCREEN_WIDTH, SCREEN_HEIGHT,
                                        background)

        ar.draw_text("Left and Right arrow keys to move\nDown key to roll \nUp key to jump \n"
                     "Space bar + Left/Right to dash and destroy enemies!", 50, 140,
                         ar.color.WHITE, font_size=32, anchor_x="left")

        ar.draw_text("P to pause game\n"
                     "R to restart level", 50, 50, ar.color.WHITE, font_size=24)

        ar.draw_text("Click to play!", SCREEN_WIDTH/2, 40, (200,255,255), font_size=60, anchor_x="center")

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
        ar.draw_text("Game Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2+25,
                         ar.color.WHITE, font_size=48, anchor_x="center")
        ar.draw_text("Left and Right arrow keys to move.\nDown key to roll.\nUp key to jump.\n"
                     "Space bar + Left/Right to dash and destroy enemies!\n"
                     "R to restart level.\n"
                     "Swim by repeatedly tapping arrow keys.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-125,
                     ar.color.WHITE, font_size=20, anchor_x="center", align="center")

        ar.draw_text("Press P to resume game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-175,
                         ar.color.WHITE, font_size=20, anchor_x="center")


    def on_key_press(self, symbol: int, modifiers: int):
        """ If the user presses the mouse button, start the game. """
        if symbol == ar.key.P:
            self.window.show_view(self.game_view)

