import arcade as ar
import pymunk as pm
import math
from typing import Optional
import time

# all classes and constants from views.py and constants.py are
# going to be used in this file, so we import all of them
from views import *
from constants import *


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    :param filename{string}: the name of a file
    """
    return [
        ar.load_texture(filename),
        ar.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(ar.Sprite):
    """
    the main player object. it is based on an Arcade Sprite object.
    """
    def __init__(self):
        # set up parent class
        super().__init__()

        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.spawnpoint = [300,100]
        self.health = 0
        self.color = [0,0,0,0] # color is RGBA, 4th int being opacity between 0-255
        self.took_damage = False
        self.time_last_hit = 0
        self.crouching = False
        self.default_points = [[-40, -60], [40, -60], [40, 50], [-40, 50]]

        self.jumping = False
        self.scale = SPRITE_SCALING

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0

        main_path = "sprites/player_sprites/player"
        self.idle_texture_pair = ar.load_texture_pair(f"{main_path}_idle.png")
        self.crouching_texture_pair = ar.load_texture_pair(f"{main_path}_squished.png")

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        # self.points = self.default_points
        self.texture = self.idle_texture_pair[0]

        self.set_hit_box(self.texture.hit_box_points)

        # add walking sprites to list
        self.walking_textures = []
        for i in range(1,14):
            texture = ar.load_texture_pair(f"{main_path}walking{i}.png")
            self.walking_textures.append(texture)


    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """
        handle animation when pymunk detects the player is moving
        :param physics_engine:
        :param dx:
        :param dy:
        :param d_angle:
        :return:
        """
        # figure if we need to flip left or right
        if dx < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        if dx > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Are we on the ground?
        is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx

        # change to crouching sprite if holding DOWN or S
        if self.crouching and self.change_x == 0:
            # self.points = [[-40, -30], [40, -30], [40, 25], [-40, 25]]
            self.texture = self.crouching_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        # if self.change_x == 0 and self.change_y == 0 and not self.crouching:
        #     self.texture = self.idle_texture_pair[self.character_face_direction]
        #     self.set_hit_box(self.texture.hit_box_points)
        #     return

        # idle texture
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # walking animation
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0

            # do the walking animation
            self.cur_texture += 12
            if self.cur_texture > 12 * UPDATES_PER_FRAME:
                self.cur_texture = 0
            self.texture = self.walking_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]

class Enemy(ar.Sprite):
    def __init__(self):
        # set up parent class
        super().__init__()
        self.character_face_direction = LEFT_FACING
        self.cur_texture = 0
        self.spawnpoint = [0,0]

        self.jumping = False
        self.scale = SPRITE_SCALING

        main_path = "sprites/greenguy_walking"
        self.idle_texture_pair = ar.load_texture_pair(f"{main_path}1.png")

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-75, -100], [80, -100], [80, 100], [-75, 100]]

        # add walking sprites to list
        self.walking_textures = []
        for i in range(1,6):
            texture = ar.load_texture_pair(f"{main_path}{i}.png")
            self.walking_textures.append(texture)

    def update_animation(self, delta_time: float = 1/60):
        # figure if we need to flip left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # walking animation
        self.cur_texture += 1
        if self.cur_texture > 4 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        self.texture = self.walking_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]

class GameView(ar.View):
    """
    Main game window
    Player moves and jumps across platforms and avoids dangerous enemies
    """

    def __init__(self):
        """
        Initialize the game
        """
        super().__init__()

        # Set up the empty sprite lists
        self.player_list = None
        self.enemies_list = None
        self.wall_list = None # list of walls that an object can collide with
        self.all_sprites = ar.SpriteList() # the list of sprites on the screen
        self.score = 0 # the player score
        self.player = None # the player object
        self.physics_engine = None # the physics engine object
        self.level = 1 # the name of the level (.tmx)
        self.message = None # message for debug purposes
        self.end_of_map = 0

        # controls
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.escape_pressed = False
        self.p_pressed = False

    def setup(self):
        """
        Get the game ready to play
        """
        # Set the background color
        ar.set_background_color(ar.color.BLACK)

        self.player_list = ar.SpriteList()

        # Set up the player
        self.player = PlayerCharacter()
        self.player.center_y = 200
        self.player.center_x = 200
        self.player.health = 99
        # self.player.spawnpoint = self.player.center_x, self.player.center_y
        # self.player.left = 10
        self.player.color = DEFAULT_COLOR
        self.player_list.append(self.player)
        self.player.spawnpoint = [100, 200]

        self.load_level(self.level)

        # check if there is a "game over"
        self.game_over = False

        # Unpause the game, reset collision timer
        self.paused = False
        self.collided = False
        self.collision_timer = 0.0

    def load_level(self, level):
        """
        load a .tmx map into the game world as well as setting the appropriate physics
        for each tile and sprite that appears in that map (including the player)
        :param level: the level number as a string
        :return: n/a
        """
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = ar.PymunkPhysicsEngine(damping=damping,
                                                     gravity=gravity)
        self.physics_engine.add_sprite(self.player,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

        my_map = ar.tilemap.read_tmx(f"maps/map{level}.tmx")
        self.height = my_map.map_size.height
        self.width = my_map.map_size.width
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        self.wall_list = ar.tilemap.process_layer(my_map,
                                                  layer_name='Foreground',
                                                  scaling=TILE_SCALING,
                                                  use_spatial_hash=True)

        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=ar.PymunkPhysicsEngine.STATIC)

        self.enemies_list = ar.tilemap.process_layer(my_map,
                                                     layer_name='Enemies',
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)

        self.physics_engine.add_sprite_list(self.enemies_list,
                                            friction=ENEMY_FRICTION,
                                            mass=ENEMY_MASS,
                                            moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                            collision_type="enemy")

        spawn_coords = ar.get_tilemap_layer(map_object=my_map, layer_path="Player Spawn")
        self.view_left = 0
        self.view_bottom = 0


    def on_key_release(self, key: int, modifiers: int):
        """
        check for the last key to have been released, set the respective
        instance variable to false.
        :param key: the last key on the keyboard that the user let go of
        :param modifiers: n/a
        :return: n/a
        """
        if key == ar.key.LEFT or key == ar.key.A:
            self.left_pressed = False

        elif key == ar.key.RIGHT or key == ar.key.D:
            self.right_pressed = False

        elif key == ar.key.DOWN or key == ar.key.S:
            self.down_pressed = False
            self.player.crouching = False

        elif key == ar.key.UP or key == ar.key.W:
            self.up_pressed = False
            self.player.crouching = False

        elif key == ar.key.P:
            self.p_pressed = False


    def on_key_press(self, key: int, modifiers: int):
        """
        check for key presses, set the respective instance variable to true.
        :param key: the last key on the keyboard that the user pressed
        :param modifiers: n/a
        :return: n/a
        """
        # quit immediately
        if key == ar.key.ESCAPE:
            self.escape_pressed = True
            ar.close_window()

        # pause game
        if key == ar.key.P:
            view = PauseView(self)
            self.window.show_view(view)

        if key == ar.key.W or key == ar.key.UP:
            self.up_pressed = True

        if key == ar.key.S or key == ar.key.DOWN:
            self.down_pressed = True

        if key == ar.key.A or key == ar.key.LEFT:
            self.left_pressed = True

        if (key == ar.key.D or key == ar.key.RIGHT):
            self.right_pressed = True


    def handle_key_press(self):
        """
        after the pressing of keys has been abstracted away
        into instance variables, handle the intended game
        actions here. controls movement of player, as well
        as other key inputs
        :return: a game action for any given key press (player
        movement, pause game, quit game, etc)
        """
        # move left
        if self.left_pressed:
            if not self.player.crouching:
                # Create a force to the left. Apply it.
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)

        # move right
        elif self.right_pressed:
            if not self.player.crouching:
                # Create a force to the right. Apply it.
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
                self.physics_engine.apply_force(self.player, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player, 0)

        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player, 1.0)

        # jump up
        if self.up_pressed:
            if not self.player.crouching:
                if self.physics_engine.is_on_ground(self.player):
                    impulse = (0, PLAYER_JUMP_IMPULSE)
                    self.physics_engine.apply_impulse(self.player, impulse)
                # if self.physics_engine.can_jump():
                #     self.player.change_y = JUMP_SPEED
                #     self.player.jumping = True

        # crouch (squish in half)
        if self.down_pressed:
            if not self.player.jumping:
                self.player.crouching = True

        self.physics_engine.step()


    def process_damage(self):
        """
        handle the math behind damage dealt to the player, as well as
        handle what happens when the player's health reaches 0.
        :return: n/a
        """
        if self.player.took_damage == True:
            current_time = int(round(time.time() * 1000))
            if (current_time - self.player.time_last_hit) > DAMAGE_BUFFER_TIME:
                self.player.took_damage = False
                self.player.color = DEFAULT_COLOR
                self.player.change_x = 0
                self.player.change_y = 0

            # if player hits enemy, deduce health and knock them back
        if (self.player.took_damage is False) and \
                (ar.check_for_collision_with_list(self.player, self.enemies_list)):
            self.player.change_x = -5  # bounce player back
            self.player.change_y = 5  # player jumps up a bit
            self.player.health -= 20  # reduce health
            self.player.took_damage = True  # indicate that the player just got hit (so there is a
            # buffer until player can take damage again)
            self.player.color = RED_COLOR  # tint the player red
            self.player.time_last_hit = int(round(time.time() * 1000))

            # if player dies (runs out of health), respawn at the beginning of the level
        if self.player.health <= 0:
            self.player.change_x = 0
            self.player.change_y = 0
            self.physics_engine.set_position(self.player, self.player.spawnpoint)
            self.player.health = 99

    def on_update(self, delta_time: float):
        """
        Update the positions and statuses of all game objects
        If paused, do nothing
        :param delta_time: Time since the last update
        """
        if not self.game_over:
            self.physics_engine.step()

        self.handle_key_press()

        # Update everything
        self.player_list.update()
        # self.player_list.update_animation()
        self.all_sprites.update()
        self.enemies_list.update()

        if self.player.change_y != 0:
            self.player.jumping = True

        self.process_damage()

        # if player gets to the right edge of the level, go to next level
        if self.player.right >= self.end_of_map:
            self.level += 1 # switch to next level
            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.load_level(self.level)
            if self.level == 2:
                self.player.spawnpoint = [100, 200]
            elif self.level == 3:
                self.player.spawnpoint = [50, 300]
            self.physics_engine.set_position(self.player, self.player.spawnpoint)

        # if the player hits the bottom of the level, player dies and respawns at the start of the level
        if self.player.bottom <= 0:
            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.level += 1 # switch to next level
            self.load_level(self.level)
            if self.level == 2:
                self.player.spawnpoint = [100, 100]
            self.physics_engine.set_position(self.player, self.player.spawnpoint)

        # track if we need to change the view port
        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player.left < left_bndry:
            self.view_left -= left_bndry - self.player.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player.right > right_bndry:
            self.view_left += self.player.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player.top > top_bndry:
            self.view_bottom += self.player.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            ar.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

    def on_draw(self):
        """
        Draw the game objects
        :return:
        """
        ar.start_render()
        self.all_sprites.draw()
        self.player_list.draw()
        self.wall_list.draw()
        self.enemies_list.draw()
        msg = self.end_of_map
        msg2 = self.player.change_y
        msg3 = self.player.health
        output = f"Map width: {msg:.2f}"
        output2 = f"Player Y velocity: {msg2:.2f}"
        output3 = f"HP: {msg3:.2f}"
        ar.draw_text(text=output,
                     start_x=self.view_left + (SCREEN_WIDTH - 150),
                     start_y=self.view_bottom + (SCREEN_HEIGHT - 25),
                     color=ar.color.WHITE)
        ar.draw_text(text=output2,
                     start_x=self.view_left + (SCREEN_WIDTH - 175),
                     start_y=self.view_bottom + (SCREEN_HEIGHT - 40),
                     color=ar.color.WHITE)
        ar.draw_text(text=output3,
                     start_x=self.view_left + (SCREEN_WIDTH - 125),
                     start_y=self.view_bottom + (SCREEN_HEIGHT - 55),
                     color=ar.color.WHITE)

def run_game():
    window = ar.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MenuView()
    window.show_view(start_view)
    ar.run()

if __name__ == '__main__':
    run_game()

