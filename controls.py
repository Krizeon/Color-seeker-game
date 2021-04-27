"""
class that holds all of the controls for the game (key presses, clicks, etc)
"""
import views
from constants import *
from arcade import key
from arcade import window_commands as ar
from arcade import sound
from arcade import check_for_collision_with_list


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
        if key_pressed == key.LEFT or key_pressed == key.A:
            self.left_pressed = False

        # move right
        elif key_pressed == key.RIGHT or key_pressed== key.D:
            self.right_pressed = False

        # crouch down
        elif key_pressed == key.DOWN or key_pressed == key.S:
            self.down_pressed = False
            self.player.crouching = False

        # jump up
        elif key_pressed == key.UP or key_pressed == key.W:
            self.up_pressed = False
            self.player.jumped_max_height = True

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

        if y_vel >= -PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            if self.down_pressed and not self.up_pressed:
                impulse = (0, -PLAYER_MOVE_FORCE_IN_WATER)
                self.physics_engine.apply_impulse(self.player, impulse)

        if y_vel <= PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            if self.up_pressed and not self.down_pressed:
                impulse = (0, PLAYER_MOVE_FORCE_IN_WATER)
                self.physics_engine.apply_impulse(self.player, impulse)

        if x_vel <= PLAYER_MAX_HORIZONTAL_SPEED_IN_WATER:
            if self.right_pressed and not self.left_pressed:
                impulse = (PLAYER_MOVE_FORCE_IN_WATER, 0)
                self.physics_engine.apply_impulse(self.player, impulse)

        if x_vel >= -PLAYER_MAX_HORIZONTAL_SPEED_IN_WATER:
            if self.left_pressed and not self.right_pressed:
                impulse = (-PLAYER_MOVE_FORCE_IN_WATER, 0)
                self.physics_engine.apply_impulse(self.player, impulse)
            # sound.play_sound(self.jump_sound, volume=0.4)

    def handle_water_physics(self):
        """
        simulate water physics when the player is in water (apply heavy friction)
        :return:
        """

        # the following variables are only available when player is not in water, so disable them
        self.player.jumping = False
        self.player.crouching = False

        player_velocity = self.get_object_velocity(self.player)
        x_vel = player_velocity[0]
        y_vel = player_velocity[1]

        #apply heavy dampening if the player velocity is very fast
        if y_vel < -PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            water_dampening = (0, PLAYER_HEAVY_WATER_DAMPENING)
            self.physics_engine.apply_force(self.player, water_dampening)
        if x_vel > PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            water_dampening = (-PLAYER_HEAVY_WATER_DAMPENING, 0)
            self.physics_engine.apply_force(self.player, water_dampening)
        elif x_vel < -PLAYER_MAX_VERTICAL_SPEED_IN_WATER:
            water_dampening = (PLAYER_HEAVY_WATER_DAMPENING, 0)
            self.physics_engine.apply_force(self.player, water_dampening)

        # apply counterforce on the x plane
        if x_vel >= WATER_DEAD_ZONE:
            water_counterforce = (-WATER_DAMPENING_FORCE, 0)
            self.physics_engine.apply_force(self.player, water_counterforce)
        elif x_vel <= -WATER_DEAD_ZONE:
            water_counterforce = (WATER_DAMPENING_FORCE, 0)
            self.physics_engine.apply_force(self.player, water_counterforce)

        # apply counterforce on the y plane
        if y_vel >= WATER_DEAD_ZONE:
            water_counterforce = (0, -WATER_DAMPENING_FORCE)
            self.physics_engine.apply_force(self.player, water_counterforce)
        elif y_vel <= -WATER_DEAD_ZONE:
            water_counterforce = (0, WATER_DAMPENING_FORCE)
            self.physics_engine.apply_force(self.player, water_counterforce)

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


        if not self.player.in_water:
            is_on_ground = self.physics_engine.is_on_ground(self.player)
            if not self.screen_wipe_rect:
                # sliding and moving at the same time!
                if self.down_pressed:  # (self.down_pressed and self.right_pressed) or (self.down_pressed and self.left_pressed):
                    if self.physics_engine.is_on_ground(self.player) and not self.player.jumping and not self.player.in_water:
                        self.player.crouching = True

                # jump up
                player_velocities = self.get_object_velocity(self.player)
                player_velocity_x = player_velocities[0]
                player_velocity_y = player_velocities[1]
                if self.up_pressed:
                    # don't jump when crouching
                    if not self.player.crouching:
                        self.player.jumping = True
                        self.player.current_y_velocity = player_velocity_y
                        if is_on_ground:
                            self.player.jumped_max_height = False
                            self.physics_engine.set_velocity(self.player, (player_velocity_x, 0))
                            impulse = (0, PLAYER_JUMP_IMPULSE)
                            self.physics_engine.apply_impulse(self.player, impulse)
                            sound.play_sound(self.jump_sound, volume=0.4)
                        if not is_on_ground and round(player_velocity_y) == 0:
                            self.player.jumped_max_height = True
                        elif not self.player.jumped_max_height and player_velocity_y < PLAYER_MAX_JUMP_VELOCITY:
                            # apply a smaller force while in the air to make a more realistic jump effect
                            # also allows for finer degree of control to jumping
                            impulse = (0, PLAYER_JUMP_IMPULSE_IN_AIR)
                            self.physics_engine.apply_impulse(self.player, impulse)
                        else:
                            self.player.jumped_max_height = True


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