"""
Main game driver (run this file to play game!)
"""
# all classes and constants from views.py and constants.py are
# going to be used in this file, so we import all of them!
import time
import views
import fsm
from constants import *
from player import *
from transition import Transition
from controls import Controls

def convert_hex_to_color(hex_string):
    """
    convert a RGBA hex to int list
    the format in Tiled's map files uses ARGB for some reason, so this function converts
    the last 3 hex values and appends the first Alpha value at the end
    :param hex_string: 4 hex-long string (ex: "#ab112244")
    :return: color list (ex: [255,255,255,255])
    """
    hexes = hex_string[3:]  # ignore the # and the first hex value (ex: "#ff"
    nums = [hexes[i:i + 2] for i in range(0, len(hexes), 2)]  # split every two elements
    for i in range(len(nums)):
        nums[i] = int(nums[i], 16)
    nums.append(int(hex_string[1:3], 16))
    return nums


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

        self.set_update_rate = None

        # Set up the empty sprite lists
        self.player_list = None
        self.enemies_list = None
        self.wall_list = None  # list of walls that an object can collide with
        self.scenery_list = None
        self.moving_platforms_list = None
        self.cannons_list = None

        self.all_sprites = ar.SpriteList()  # the list of sprites on the screen
        self.keys_list = None
        self.hidden_platform_list = None
        self.water_list = None
        self.background = None
        self.screen_wipe_rect = None
        self.update_level = False  # flag raised when the blue screen wipe is occurring to load new level
        self.key_colors = {}

        self.cannon_timer = 0
        self.cannon_timed = False
        self.current_cannon = None

        self.score = 0  # the player score
        self.player = None  # the player object
        self.physics_engine = None  # the physics engine object
        self.level = None  # the name of the level (.tmx)
        self.message = None  # message for debug purposes
        self.end_of_map = 0
        self.top_of_map = 0
        self.player_teleported = False
        self.current_map = None

        # controls
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.escape_pressed = False
        self.p_pressed = False
        self.l_pressed = False
        self.k_pressed = False
        self.m_pressed = False
        self.r_pressed = False

        # viewport window handling
        self.view_left = 0
        self.view_bottom = 0
        self.height = 0
        self.width = 0

        # sounds
        self.jump_sound = None
        self.bg_music = None
        self.playing_music = False

        # conditions
        self.game_over = False
        self.paused = False
        self.collided = False
        self.collision_timer = 0

    def setup(self):
        """
        Get the game ready to play
        """

        # Set the background color
        ar.set_background_color(ar.color.BLACK)

        # uncomment to debug the screen wipe transition
        # self.screen_wipe_rect = Rectangle()
        # self.screen_wipe_rect.setup()

        self.player_list = ar.SpriteList()
        self.level = STARTING_LEVEL
        self.player = PlayerCharacter()

        # Set up the player
        self.load_level(self.level)
        self.background = ar.load_texture("backgrounds/background1.jpg")

        self.player.health = 99
        self.player.color = DEFAULT_COLOR
        self.player_list.append(self.player)

        # check if there is a "game over"
        self.game_over = False

        # Unpause the game, reset collision timer
        self.paused = False
        self.collided = False
        self.collision_timer = 0.0

        # sound
        self.orb_touched_sound = ar.load_sound("sounds/orb_get.ogg")
        self.orb_off_sound = ar.load_sound("sounds/orb_off.ogg")
        self.jump_sound = ar.load_sound("sounds/jump1.wav")
        self.bg_music = ar.Sound("music/gamesong2.ogg", streaming=True)

    def play_music(self):
        """
        play the background music, loop on end.
        :return:
        """
        if self.bg_music and not self.playing_music:
            self.bg_music.play(volume=BG_MUSIC_VOLUME, loop=True)
            self.playing_music = True

        # fix music loop functionality
        # elif self.bg_music.is_complete():
        #     self.bg_music.play(volume=BG_MUSIC_VOLUME)


    def add_to_keys_dict(self, key, color):
        """
        adds key color to self.key_colors for future reference
        :param key: current key
        :param color: list of colors in RGBA format (255,255,255,255)
        :return: none
        """
        # color_name = key.properties["color"]
        # color_rgba = color
        self.key_colors[key] = color

    def load_level(self, level):
        """
        load a .tmx map into the game world as well as setting the appropriate physics
        for each tile and sprite that appears in that map (including the player)
        :param level: the level number as a string
        :return: n/a
        """
        # reinitialize all elements of a level
        self.view_left = 0
        self.view_bottom = 0
        self.wall_list = None
        self.enemies_list = None
        self.scenery_list = None
        self.keys_list = None
        self.moving_platforms_list = None
        self.cannons_list = None
        if self.hidden_platform_list:
            self.hidden_platform_list = None
        self.water_list = None

        self.current_cannon = None
        self.cannon_timed = None
        self.key_colors = {}

        self.player.color = DEFAULT_COLOR
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = ar.PymunkPhysicsEngine(damping=damping,
                                                     gravity=gravity)

        self.current_map = ar.tilemap.read_tmx(f"maps/map{level}.tmx")
        self.height = self.current_map.map_size.height
        self.width = self.current_map.map_size.width
        self.end_of_map = self.current_map.map_size.width * GRID_PIXEL_SIZE
        self.top_of_map = self.current_map.map_size.height * GRID_PIXEL_SIZE

        self.keys_list = ar.tilemap.process_layer(self.current_map,
                                                  layer_name='Color Orbs',
                                                  scaling=SPRITE_SCALING,
                                                  use_spatial_hash=True)

        # change the color of hidden platforms as specified in the map properties
        for key in self.keys_list:
            key_color = convert_hex_to_color(key.properties["key_color"])
            key.color = key_color
            self.add_to_keys_dict(key, key_color)

        # find the player spawnpoint in the .tmx map
        player_location = ar.tilemap.process_layer(self.current_map,
                                                   layer_name='Player Spawn',
                                                   scaling=SPRITE_SCALING,
                                                   use_spatial_hash=True)

        # handle setting the player spawnpoint
        self.player.spawnpoint = int(player_location[0].center_x), int(player_location[0].center_y)
        self.player.center_x, self.player.center_y = self.player.spawnpoint
        # the player!
        self.physics_engine.add_sprite(self.player,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
        # walls list
        self.wall_list = ar.tilemap.process_layer(self.current_map,
                                                  layer_name='Foreground',
                                                  scaling=TILE_SCALING,
                                                  use_spatial_hash=False,
                                                  hit_box_algorithm="Detailed")
        # enemies list
        self.enemies_list = ar.tilemap.process_layer(self.current_map,
                                                     layer_name='Enemies',
                                                     scaling=SPRITE_SCALING,
                                                     use_spatial_hash=True)
        # foreground objects list
        self.scenery_list = ar.tilemap.process_layer(self.current_map,
                                                     layer_name='Foreground Objects',
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        # moving platforms list
        self.moving_platforms_list = ar.tilemap.process_layer(self.current_map,
                                                              layer_name='Moving Platforms',
                                                              scaling=TILE_SCALING,
                                                              use_spatial_hash=True)
        # cannons list
        self.cannons_list = ar.tilemap.process_layer(self.current_map,
                                                     layer_name='Cannons',
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        # water list
        self.water_list = ar.tilemap.process_layer(self.current_map,
                                                     layer_name='Water',
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        # physics engine additions below
        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=ar.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(self.enemies_list,
                                            mass=ENEMY_MASS,
                                            body_type=ar.PymunkPhysicsEngine.KINEMATIC,
                                            collision_type="enemy")

        self.physics_engine.add_sprite_list(self.moving_platforms_list,
                                            friction=WALL_FRICTION,
                                            body_type=ar.PymunkPhysicsEngine.KINEMATIC,
                                            collision_type="wall")

        self.physics_engine.add_sprite_list(self.cannons_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=ar.PymunkPhysicsEngine.DYNAMIC)

        # for cannon in self.cannons_list:
        #     cannon._hit_box_algorithm = "Detailed"
        #     cannon.hit_box = [(-64,64),(-44, 64),(-44, 0), (44, 0), (44,64),(64,64),(64,-64),(-64,-64)]

    def screen_wipe(self):
        if self.screen_wipe_rect:
            ar.draw_rectangle_filled(center_x=self.screen_wipe_rect.center_x,
                                     center_y=self.screen_wipe_rect.center_y,
                                     width=self.screen_wipe_rect.width,
                                     height=self.screen_wipe_rect.height,
                                     color=self.screen_wipe_rect.color
                                     )

    def load_layer(self, layer_name, color):
        """
        load a new layer from a loaded map
        :param layer_name: name of layer in the current map
        :param color: an RGBA color list
        :return: n/a
        """
        self.hidden_platform_list = ar.tilemap.process_layer(self.current_map,
                                                             layer_name=layer_name,
                                                             scaling=TILE_SCALING,
                                                             use_spatial_hash=True)

        # change the color of hidden platforms as specified in the map properties
        for platform in self.hidden_platform_list:
            platform.color = color

        self.physics_engine.add_sprite_list(self.hidden_platform_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=ar.PymunkPhysicsEngine.STATIC)

    def on_key_release(self, key: int, modifiers: int):
        """
        check for the last key to have been released, set the respective
        instance variable to false.
        :param key: the last key on the keyboard that the user let go of
        :param modifiers: n/a
        :return: n/a
        """
        if self.player.in_water:
            # the controls in water should only register when the key is released, unlike regular controls
            Controls.handle_water_controls(self)
        Controls.handle_key_release(self, key, modifiers)

    def on_key_press(self, key: int, modifiers: int):
        """
        check for key presses, set the respective instance variable to true.
        :param key: the last key on the keyboard that the user pressed
        :param modifiers: n/a
        :return: n/a
        """
        Controls.handle_key_presses(self, key, modifiers)

    def process_damage(self):
        """
        handle the math behind damage dealt to the player, as well as
        handle what happens when the player's health reaches 0.
        :return: n/a
        """
        if self.player.took_damage:
            # start cooldown until player can take damage again
            current_time = int(round(time.time() * 1000))
            if (current_time - self.player.time_last_hit) > DAMAGE_BUFFER_TIME:
                self.player.took_damage = False
                self.player.color = self.player.default_color
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
            self.update_level = True  # raise this flag to properly restart level
            self.screen_wipe_rect = Transition()
            self.screen_wipe_rect.setup()
            self.player_teleported = True
            self.physics_engine.set_position(self.player, self.player.spawnpoint)
            self.player.health = 99

    def restart_level_toggle(self):
        if self.r_pressed:
            # kill player, trigger level to restart
            self.player.health = 0

    def track_moving_sprites(self, delta_time):
        # For each moving sprite, see if we've reached a boundary and need to
        # reverse course.
        count = 0
        for enemy_sprite in self.enemies_list:
            count += 1
            if enemy_sprite.boundary_right and enemy_sprite.change_x > 0 and enemy_sprite.right > (
                    enemy_sprite.boundary_right * SPRITE_SCALING):
                enemy_sprite.change_x *= -1
            elif enemy_sprite.boundary_left and enemy_sprite.change_x < 0 and enemy_sprite.left < (
                    enemy_sprite.boundary_left * SPRITE_SCALING):
                enemy_sprite.change_x *= -1
            if enemy_sprite.boundary_top and enemy_sprite.change_y > 0 and enemy_sprite.top > (
                    enemy_sprite.boundary_top * SPRITE_SCALING):
                enemy_sprite.change_y *= -1
            elif enemy_sprite.boundary_bottom and enemy_sprite.change_y < 0 and enemy_sprite.bottom < (
                    enemy_sprite.boundary_bottom * SPRITE_SCALING):
                enemy_sprite.change_y *= -1

            # Figure out and set our moving platform velocity.
            # Pymunk uses velocity is in pixels per second. If we instead have
            # pixels per frame, we need to convert.
            velocity = (enemy_sprite.change_x * 1 / delta_time, enemy_sprite.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(enemy_sprite, velocity)

        count = 0
        for moving_platform in self.moving_platforms_list:
            count += 1
            if moving_platform.boundary_right and moving_platform.change_x > 0 and moving_platform.right > (
                    moving_platform.boundary_right * SPRITE_SCALING):
                moving_platform.change_x *= -1
            elif moving_platform.boundary_left and moving_platform.change_x < 0 and moving_platform.left < (
                    moving_platform.boundary_left * SPRITE_SCALING):
                moving_platform.change_x *= -1
            if moving_platform.boundary_top and moving_platform.change_y > 0 and moving_platform.top > (
                    moving_platform.boundary_top * SPRITE_SCALING):
                moving_platform.change_y *= -1
            elif moving_platform.boundary_bottom and moving_platform.change_y < 0 and moving_platform.bottom < (
                    moving_platform.boundary_bottom * SPRITE_SCALING):
                moving_platform.change_y *= -1

            velocity = (moving_platform.change_x * 1 / delta_time, moving_platform.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(moving_platform, velocity)

            # force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            # self.physics_engine.apply_force(enemy_sprite, force)

    def cannon_toggle(self):
        """
        handle cannon toggle and launching
        :return:
        """
        # cannon launching handling
        # only launch cannon if player has touched a "pressure plate" (half slab block, colored white)
        current_time = 0
        if (ar.check_for_collision_with_list(self.player, self.cannons_list)):
            current_cannon = ar.check_for_collision_with_list(self.player, self.cannons_list)[0]
            if current_cannon.properties["is_trigger"]:
                current_cannon.color = ar.color.YELLOW
                # timer for when player is activating cannon
                if not self.cannon_timed:
                    # logically connect a pressure plate (trigger) with a cannon block
                    for cannon in self.cannons_list:
                        # find the trigger's corresponding cannon by finding its matching trigger code
                        if cannon.properties["trigger_code"] == current_cannon.properties["trigger_code"] and \
                                not cannon.properties["is_trigger"]:
                            self.current_cannon = cannon
                            self.current_cannon.color = ar.color.YELLOW
                    self.cannon_timer = current_time + CANNON_BUFFER_TIME
                    self.cannon_timed = True

                    # teleport back to its original position when cannon is toggled
                    self.physics_engine.remove_sprite(self.current_cannon)
                    self.current_cannon.center_x = (self.current_cannon.properties['spawn_x'] * TILE_SCALING) + \
                                                   (GRID_PIXEL_SIZE / 2)
                    self.current_cannon.center_y = self.top_of_map - (self.current_cannon.properties['spawn_y'] *
                                                                      TILE_SCALING) + (GRID_PIXEL_SIZE / 2)
                    self.current_cannon.angle = -self.current_cannon.properties['spawn_angle']
                    self.physics_engine.add_sprite(self.current_cannon,
                                                   friction=CANNON_FRICTION,
                                                   mass=CANNON_MASS,
                                                   collision_type="wall",
                                                   elasticity=0,
                                                   max_horizontal_velocity=CANNON_MAX_HORIZONTAL_SPEED,
                                                   max_vertical_velocity=CANNON_MAX_VERTICAL_SPEED,
                                                   body_type=ar.PymunkPhysicsEngine.DYNAMIC)

        current_time = int(round(time.time() * 1000))
        # do the launching if corresponding pressure plate has been toggled
        if self.current_cannon and ar.check_for_collision(self.player, self.current_cannon) and self.player.crouching:
            self.current_cannon.color = ar.color.YELLOW
            self.physics_engine.apply_impulse(self.current_cannon, (0, CANNON_IMPULSE))
            if self.current_cannon and (self.current_cannon.center_y > self.top_of_map or self.current_cannon.center_x > self.end_of_map):
                self.physics_engine.remove_sprite(self.current_cannon)
        self.cannon_timed = False

    def get_object_velocity(self, object):
        """
        get object velocities from physics engine
        :param object: a sprite object in the pymunk physics engine
        :return: (velocity x, velocity y)
        """
        return self.physics_engine.get_physics_object(object).body.velocity

    def in_water_physics(self):
        """
        handle water physics here
        :return:
        """
        if ar.check_for_collision_with_list(self.player, self.water_list):
            self.player.in_water = True
            self.physics_engine.apply_force(self.player, (0,BUOYANCY_FORCE))
        else:
            self.player.in_water = False

    def on_update(self, delta_time: float):
        """
        Update the positions and statuses of all game objects
        If paused, do nothing
        :param delta_time: Time since the last update
        """
        if not self.game_over or not self.paused:
            self.physics_engine.step()

        # handle background music
        self.play_music()

        if self.screen_wipe_rect:  # when the game is transitioning to a new level/restarting a level
            self.screen_wipe_rect.center_x += self.screen_wipe_rect.change_x
            self.screen_wipe_rect.center_y = self.view_bottom + (SCREEN_HEIGHT / 2)
            # handle loading level here, after screen is covered in blue wipe
            if (self.screen_wipe_rect.center_x > SCREEN_WIDTH) and (self.update_level):
                self.load_level(self.level)
                self.update_level = False  # lower flag when level begins to load
            if self.screen_wipe_rect.center_x > SCREEN_WIDTH * 2:
                self.screen_wipe_rect = None

        # Update everything
        self.player_list.update()
        self.all_sprites.update()
        self.enemies_list.update()
        self.moving_platforms_list.update()
        self.cannons_list.update()

        Controls.handle_control_actions(self)
        if self.player.in_water:
            Controls.handle_water_physics(self)

        self.process_damage()
        self.track_moving_sprites(delta_time)
        self.cannon_toggle()
        self.in_water_physics()

        if ar.check_for_collision_with_list(self.player, self.keys_list) and not self.update_level:
            current_key = ar.check_for_collision_with_list(self.player, self.keys_list)[0]
            if self.key_colors[current_key] == WHITE:
                # this if statement is redundant so that we don't immediately enter the else statement below
                if self.hidden_platform_list:
                    self.orb_off_sound.play(volume=0.2)
                    for platform in self.hidden_platform_list:
                        self.physics_engine.remove_sprite(platform)
                    self.hidden_platform_list = None
                self.player.color = WHITE
            else:
                if not self.hidden_platform_list:
                    self.orb_touched_sound.play(volume=0.2)
                    self.load_layer("Hidden Platforms", self.key_colors[current_key])
                    self.player.color = self.key_colors[current_key]

        # if player gets to the right edge of the level, go to next level
        if self.player.right >= self.end_of_map:
            self.update_level = True  # raise this flag to properly restart level
            self.level += 1  # switch to next level

            self.screen_wipe_rect = Transition()
            self.screen_wipe_rect.setup()
            self.player_teleported = True

            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.physics_engine.set_position(self.player, self.player.spawnpoint)

        # if the player hits the bottom of the level, player dies and respawns at the start of the level
        if self.player.bottom <= 0:
            self.update_level = True  # raise this flag to properly restart level

            self.screen_wipe_rect = Transition()
            self.screen_wipe_rect.setup()

            self.player_teleported = True

            self.physics_engine.set_horizontal_velocity(self.player, 0)
            self.physics_engine.set_position(self.player, self.player.spawnpoint)

        if self.physics_engine.is_on_ground(self.player) and self.player.jumping:
            self.player.jumping = False

        # track if we need to change the view port
        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player.left < left_bndry and self.player.left > VIEWPORT_LEFT_MARGIN:
            self.view_left -= left_bndry - self.player.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player.right > right_bndry and (self.player.right < (self.end_of_map - VIEWPORT_RIGHT_MARGIN)):
            self.view_left += self.player.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player.top > top_bndry and (self.player.top < (self.top_of_map - VIEWPORT_MARGIN_TOP)):
            self.view_bottom += self.player.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player.bottom < bottom_bndry and self.player.bottom > VIEWPORT_MARGIN_BOTTOM:
            self.view_bottom -= bottom_bndry - self.player.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        # also change viewport when player has teleported (when switching levels, respawning, etc)
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            ar.set_viewport(self.view_left,
                            SCREEN_WIDTH + self.view_left,
                            self.view_bottom,
                            SCREEN_HEIGHT + self.view_bottom)

        if self.player_teleported and self.screen_wipe_rect.center_x > SCREEN_WIDTH:
            self.view_left = 0
            self.view_bottom = 0
            ar.set_viewport(self.view_left,
                            SCREEN_WIDTH + self.view_left,
                            self.view_bottom,
                            SCREEN_HEIGHT + self.view_bottom)
            self.player_teleported = False

    def on_draw(self):
        """
        Draw the game objects
        :return:
        """
        ar.start_render()
        # draw the background texture
        ar.draw_lrwh_rectangle_textured(0, 0,
                                        self.end_of_map, self.top_of_map,
                                        self.background)
        self.all_sprites.draw()
        self.player_list.draw()
        self.wall_list.draw()
        self.enemies_list.draw()
        self.scenery_list.draw()
        self.keys_list.draw()
        self.moving_platforms_list.draw()
        self.cannons_list.draw()
        self.water_list.draw()

        if self.hidden_platform_list:
            self.hidden_platform_list.draw()
        # self.player.draw()

        # draw the transition wipe when restarting or loading a new level
        self.screen_wipe()

        # draw hitboxes for walls
        if self.l_pressed:
            for wall in self.wall_list:
                wall.draw_hit_box(RED_COLOR)
            if self.hidden_platform_list:
                for platform in self.hidden_platform_list:
                    platform.draw_hit_box(RED_COLOR)
            if self.keys_list:
                for key in self.keys_list:
                    key.draw_hit_box(RED_COLOR)
            if self.cannons_list:
                for cannon in self.cannons_list:
                    cannon.draw_hit_box(RED_COLOR)

        # draw player hitboxes and debug info
        if self.k_pressed:
            self.player.draw_hit_box(RED_COLOR)

            # get player x/setup.py velocity from the physics engine ([x,setup.py])
            player_velocities = self.physics_engine.get_physics_object(self.player).body.velocity
            velocity_x = player_velocities[0]
            velocity_y = player_velocities[1]
            is_on_ground = self.physics_engine.is_on_ground(self.player)

            msg = self.end_of_map
            msg2 = self.player.crouching
            msg3 = self.player.health
            msg4 = velocity_x
            msg5 = velocity_y
            msg6 = self.player.jumping
            msg7 = self.player.center_x
            msg8 = self.player.center_y
            msg10 = is_on_ground
            msg11 = self.player.height
            msg12 = self.player.width

            output = f"Map width: {msg:.2f}"
            output2 = f"Is crouching: {msg2}"
            output3 = f"HP: {msg3:.2f}"
            output4 = f"Player X vel: {msg4:.2f}"
            output5 = f"Player Y vel: {msg5:.2f}"
            output6 = f"Player Jumping?: {msg6}"
            output7 = f"Player X pos?: {msg7:.1f}"
            output8 = f"Player Y pos?: {msg8:.1f}"
            output10 = f"Player on ground?: {msg10}"
            output11 = f"Player height: {msg11}"
            output12 = f"Player width: {msg12}"

            ar.draw_text(text=output,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 25),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output2,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 45),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output3,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 65),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output4,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 85),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output5,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 105),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output6,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 125),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output7,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 145),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output8,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 165),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output10,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 185),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output11,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 205),
                         font_size=18,
                         color=ar.color.WHITE)
            ar.draw_text(text=output12,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 225),
                         font_size=18,
                         color=ar.color.WHITE)

        msg3 = self.player.health
        output3 = f"HP: {msg3:.2f}"
        ar.draw_text(text=output3,
                     start_x=self.view_left + 20,
                     start_y=self.view_bottom + (SCREEN_HEIGHT - 65),
                     font_size=18,
                     color=ar.color.WHITE)
        if self.screen_wipe_rect:
            msg9 = self.screen_wipe_rect.center_x
            output9 = f"screen wipe x: {msg9:.2f}"
            ar.draw_text(text=output9,
                         start_x=self.view_left + 20,
                         start_y=self.view_bottom + (SCREEN_HEIGHT - 180),
                         font_size=18,
                         color=ar.color.WHITE)


def run_game():
    window = ar.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=FRAME_RATE)
    start_view = views.MenuView()
    window.show_view(start_view)
    ar.run()


if __name__ == '__main__':
    run_game()
