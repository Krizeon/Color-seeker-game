"""
class that holds all of the controls for the game (key presses, clicks, etc)
"""
import views
from constants import *
from arcade import key
from arcade import window_commands as ar
from arcade import sound


class Controls():

    def __init__(self, *args, **kwargs):
        super.__init__()

    def handle_key_presses(self, key_pressed: int, modifiers: int):
        """
        check for key presses, set the respective instance variable to true.
        :param key_pressed: the last key on the keyboard that the user pressed
        :param modifiers: n/a
        :return: n/a
        """

        # quit immediately
        if key_pressed == key.ESCAPE:
            self.escape_pressed = True
            ar.close_window()

        # pause game (do this here to immediately pause without interrupting game)
        if key_pressed == key.P:
            pause_view = views.PauseView(game_view=self)
            self.window.show_view(pause_view)

        if key_pressed == key.W or key_pressed == key.UP:
            self.up_pressed = True

        if key_pressed == key.S or key_pressed == key.DOWN:
            self.down_pressed = True

        if key_pressed == key.A or key_pressed == key.LEFT:
            self.left_pressed = True

        if key_pressed == key.D or key_pressed == key.RIGHT:
            self.right_pressed = True

        if key_pressed == key.R:
            self.r_pressed = True

        if key_pressed == key.M:
            self.m_pressed = True
        elif key_pressed == key.M and self.m_pressed:
            self.l_pressed = False

        # keys below are toggles for debugging purposes (drawing hitboxes, etc)
        if key_pressed == key.L and not self.l_pressed:
            self.l_pressed = True
        elif key_pressed == key.L and self.l_pressed:
            self.l_pressed = False

        if key_pressed == key.K and not self.k_pressed:
            self.k_pressed = True
        elif key_pressed == key.K and self.k_pressed:
            self.k_pressed = False

    def handle_key_release(self, key_pressed: int, modifier: int):
        """
        handle key being released
        :param key_pressed: key being released
        :param modifier: modifier key (ctrl, shift, alt, etc)
        :return:
        """
        # move left
        if key_pressed == key.LEFT or key == key.A:
            self.left_pressed = False

        # move right
        elif key_pressed == key.RIGHT or key == key.D:
            self.right_pressed = False

        # crouch down
        elif key_pressed == key.DOWN or key == key.S:
            self.down_pressed = False
            self.player.crouching = False

        # jump up
        elif key_pressed == key.UP or key == key.W:
            self.up_pressed = False

        # restart the level
        elif key_pressed == key.R:
            self.r_pressed = False

        # pause the game
        elif key_pressed == key.P:
            self.p_pressed = False

    def restart_level_toggle(self):
        """
        control to restart level. press the r key
        :return:
        """
        pass

    def mute_music(self):
        """
        pause the background music. press the m key
        :return:
        """
        pass

    def handle_water_controls(self):
        """
        handle movement when the player is in water
        :return:
        """
        player_velocity = self.get_object_velocity(self.player)
        x_vel = player_velocity[0]
        y_vel = player_velocity[1]

        if abs(y_vel) <= PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            if self.down_pressed and not self.up_pressed:
                impulse = (0, -PLAYER_MOVE_FORCE_IN_WATER)
                self.physics_engine.apply_force(self.player, impulse)

            elif self.up_pressed and not self.down_pressed:
                impulse = (0, PLAYER_MOVE_FORCE_IN_WATER)
                self.physics_engine.apply_force(self.player, impulse)

        if abs(x_vel) <= PLAYER_MAX_HORIZONTAL_SPEED_IN_WATER:
            if self.right_pressed and not self.left_pressed:
                impulse = (PLAYER_MOVE_FORCE_IN_WATER, 0)
                self.physics_engine.apply_force(self.player, impulse)

            elif self.left_pressed and not self.right_pressed:
                impulse = (-PLAYER_MOVE_FORCE_IN_WATER, 0)
                self.physics_engine.apply_force(self.player, impulse)
            # sound.play_sound(self.jump_sound, volume=0.4)

    def handle_control_actions(self):
        """
        after the pressing of keys has been abstracted away
        into instance variables, handle the intended game
        actions here. controls movement of player, as well
        as other key inputs
        :return: a game action for any given key press (player
        movement, pause game, quit game, etc)
        """
        # restart level
        if self.r_pressed:
            # kill player, trigger level to restart
            self.player.health = 0

        # mute music
        if self.m_pressed:
            self.bg_music.stop()
            self.playing_music = False

        if not self.screen_wipe_rect:
            # sliding and moving at the same time!
            if self.down_pressed:  # (self.down_pressed and self.right_pressed) or (self.down_pressed and self.left_pressed):
                if self.physics_engine.is_on_ground(self.player) and not self.player.jumping and not self.player.in_water:
                    self.player.crouching = True
                    # smoothly slide down a hill
                    # self.physics_engine.set_friction(self.player, 0.2)

            # jump up
            if self.up_pressed:
                if not self.player.crouching:
                    self.player.jumping = True
                    if self.physics_engine.is_on_ground(self.player):
                        impulse = (0, PLAYER_JUMP_IMPULSE)
                        self.physics_engine.apply_impulse(self.player, impulse)
                        sound.play_sound(self.jump_sound, volume=0.4)

            is_on_ground = self.physics_engine.is_on_ground(self.player)
            is_in_water = self.player.in_water
            # Update player forces based on keys pressed
            if self.left_pressed and not (self.right_pressed or self.down_pressed):
                # Create a force to the left. Apply it.
                if is_on_ground:
                    force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
                elif self:
                    force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)

            elif self.right_pressed and not (self.left_pressed or self.down_pressed):
                # Create a force to the right. Apply it.
                if is_on_ground:
                    force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
                else:
                    force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)
            else:
                # Player's feet are not moving. Therefore up the friction so we stop.
                self.physics_engine.set_friction(self.player, 1.0)