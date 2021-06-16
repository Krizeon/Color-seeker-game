import arcade as ar
from constants import *
from random import randint

# coordinates to make a circular hitbox for when player is "crouching"
CIRCLE2 = [(-30,0), (-28,10),(-20,22),(-10,28),
          (0,30),(10,28),(20,22),(28,10),
          (30,0),(28,-10),(20,-22),(10,-28),
          (0,-30),(-10,-28),(-20,-22),(-28,-10)]


# class CircleSprite(ar.Sprite):
#     def __init__(self, filename, pymunk_shape):
#         super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.setup.py)
#         self.width = pymunk_shape.radius * 2
#         self.height = pymunk_shape.radius * 2
#         self.pymunk_shape = pymunk_shape

class PlayerCharacter(ar.Sprite):
    """
    the main player object. it is based on an Arcade Sprite object.
    """

    def __init__(self):
        # set up parent class
        super().__init__()

        self._hit_box_algorithm = "Detailed"
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.spawnpoint = [0, 0]
        self.health = 0
        self.default_color = [255, 255, 255, 255]
        self.color = [0, 0, 0, 0]  # color is RGBA, 4th int being opacity between 0-255
        self.took_damage = False
        self.time_last_hit = 0
        self.time_last_launched = 0
        self.crouching = False  # is the player crouching?
        self.default_points = [[-40, -60], [40, -60], [40, 50], [-40, 50]]
        self.adjusted_hitbox = False  # this is a "latch", used for handling crouching.
        self.current_y_velocity = 0
        self.is_touching_ground = True

        self.ball_dashing = False # do ball dashing when true
        self.ball_dash_released = True # toggle True if player has let go of key combo for dashing
        self.ball_dash_reset = False

        # toggle player's high jump ability (permanent after collecting a specific item)
        self.hi_jump = True

        # toggle the player's gliding ability (permanent after collecting a specific item)
        self.glider = False

        self.collision_radius = 0
        self.angle = 0

        self.in_water = False

        self.jumping = False  # is the player jumping?
        self.jumped_max_height = False
        self.scale = SPRITE_SCALING

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0

        # How far have we traveled vertically since changing the texture
        self.y_odometer = 0

        main_path = "sprites/player_sprites/player"

        # add idle texture
        self.idle_texture_pair = ar.load_texture_pair(f"{main_path}_idle.png")

        # add crouching texture
        self.crouching_texture_pair = ar.load_texture_pair(f"{main_path}_ball.png")

        # add jumping texture
        self.jumping_texture_pair = ar.load_texture_pair(f"{main_path}_jumping.png")

        # add swimming texture
        self.swimming_textures = []
        for i in range(1, 5):
            texture = ar.load_texture_pair(f"{main_path}_swimming{i}.png")
            self.swimming_textures.append(texture)

        # add dashing sprites to list
        self.dashing_textures = []
        for i in range(1, 12):
            texture = ar.load_texture_pair(f"{main_path}_dashing{i}.png")
            self.dashing_textures.append(texture)

        # add walking sprites to list
        self.walking_textures = []
        for i in range(1, 15):
            texture = ar.load_texture_pair(f"{main_path}walking{i}.png")
            self.walking_textures.append(texture)

        self.texture = self.idle_texture_pair[0]
        self.set_hit_box(self.texture.hit_box_points)

        # load sounds
        self.footstep_sound = ar.load_sound("sounds/footstep.wav")
        self.jump_sound = ar.load_sound("sounds/jump1.wav")
        self.dash_sound = ar.load_sound(("sounds/dash_whoosh.ogg"))

    def is_on_floor(self, physics_engine, dy):
        """
        a more elaborate way to detect if the player is really on the physical floor. this is
        necessary to avoid game-breaking glitches where the player can wall-jump endlessly.
        How it achieves this: consult with the physics engine if the player is touching a "ground",
        and then do a seperate check for the player's y velocity (should be
        :param physics_engine: Pymunk physics engine
        :param dy: current y velocity
        :return:
        """
        is_on_ground = physics_engine.is_on_ground(self)
        if is_on_ground and dy == 0:
            self.is_touching_ground = True
        else:
            self.is_touching_ground = False

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """
        Handle animation when Pymunk detects the player is moving
        Below there is lots of manual configuration of the height of the textures. This is necessary in order to
        prevent graphical glitches when switching textures.
        :param physics_engine: Pymunk physics engine
        :param dx: current x velocity
        :param dy: current y velocity
        :param d_angle: current angle
        :return: n/a (used to end function)
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
        self.y_odometer += dy

        vel = physics_engine.get_physics_object(self).body.velocity

        # change to crouching sprite if holding DOWN or S
        if self.crouching and not self.in_water:
            self.texture = self.crouching_texture_pair[self.character_face_direction]
            self.set_hit_box(CIRCLE_LARGE)
            # in order to make the player smaller when crouching for the physics engine,
            # remove the player from the physics engine and add it back right away.
            # this makes the process of recreating the physics body and shape automatic.
            # however, the texture height and width must be set manually to prevent
            # graphical glitches.
            if not self.adjusted_hitbox:
                # continue walking momentum when walking then crouching (left/right + down)
                physics_engine.remove_sprite(sprite=self)
                physics_engine.add_sprite(self,
                                          max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
                                          max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED_ROLLING,
                                          friction=0)
                physics_engine.apply_impulse(self, vel)
                self.texture = self.crouching_texture_pair[self.character_face_direction]
                self.set_hit_box(CIRCLE_LARGE)

                # remove these hardcoded numbers later (still debugging crouching)
                self.center_y -= 16
                self.height = PLAYER_BALL_RADIUS
                self.width = PLAYER_BALL_RADIUS
            self.adjusted_hitbox = True
            return

        # handle swimming textures
        if self.in_water and not is_on_ground:
            self.angle = 0
            self.set_hit_box(self.texture.hit_box_points)
            self.height = PLAYER_SWIM_HEIGHT
            self.width = PLAYER_SWIM_WIDTH
            if self.adjusted_hitbox:
                physics_engine.remove_sprite(sprite=self)
                physics_engine.add_sprite(self,
                                          moment=ar.PymunkPhysicsEngine.MOMENT_INF)
                self.width = PLAYER_SWIM_WIDTH
                self.height = PLAYER_SWIM_HEIGHT
            self.adjusted_hitbox = False

            # handle swimming animation below
            self.cur_texture += 1 # speed of animation
            if self.cur_texture >= 4 * UPDATES_PER_FRAME: # prevent out of bounds exception
                self.cur_texture = 0
            if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE or abs(self.y_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
                self.x_odometer = 0
                self.y_odometer = 0
                self.texture = self.swimming_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]
            return

        # do the dashing animation
        if self.ball_dashing and self.ball_dash_released:
            if not self.ball_dash_reset:
                self.cur_texture = 0
                self.ball_dash_reset = True
                ar.play_sound(self.dash_sound, volume=0.4)
            self.angle = 0
            self.x_odometer = 0
            # do the walking animation
            self.cur_texture += 11
            self.color = (randint(50,255),randint(50,255),randint(50,255))
            if self.cur_texture >= (11 * UPDATES_PER_FRAME) or (abs(vel[0]) < (50)):
                self.cur_texture = 0
                self.ball_dashing = False
                self.ball_dash_released = False
                self.ball_dash_reset = False
                self.color = WHITE
                # switch textures here
            self.texture = self.dashing_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]
            # self.height = PLAYER_IDLE_HEIGHT
            # self.width = PLAYER_IDLE_WIDTH
            return

        # idle texture
        if abs(dx) <= DEAD_ZONE and not self.jumping and not self.crouching and not self.in_water:
            self.angle = 0
            self.texture = self.idle_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            if self.adjusted_hitbox:
                physics_engine.remove_sprite(sprite=self)
                physics_engine.add_sprite(self,
                                          friction=PLAYER_FRICTION,
                                          mass=PLAYER_MASS,
                                          moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                          collision_type="player",
                                          max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                          max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
                self.height = PLAYER_IDLE_HEIGHT
                self.width = PLAYER_IDLE_WIDTH
            self.adjusted_hitbox = False
            return

        # jumping texture
        if self.jumping and not self.crouching and not self.in_water:
            self.angle = 0
            self.texture = self.jumping_texture_pair[self.character_face_direction]
            self.height = PLAYER_IDLE_HEIGHT
            self.width = PLAYER_IDLE_WIDTH
            self.set_hit_box(self.texture.hit_box_points)
            return

        # walking animation
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE and not self.crouching and not self.in_water:
            self.angle = 0
            self.x_odometer = 0
            # do the walking animation
            self.cur_texture += 14
            if self.cur_texture >= 14 * UPDATES_PER_FRAME:
                self.cur_texture = 0
            # play a sound effect when the character's foot is touching the ground (5th frame)
            if self.cur_texture // UPDATES_PER_FRAME == 5 and is_on_ground:
                ar.play_sound(self.footstep_sound, volume=0.1)
            self.texture = self.walking_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]
            self.height = PLAYER_IDLE_HEIGHT
            self.width = PLAYER_IDLE_WIDTH
            return

        # if player isn't crouching, set physics shape back to default size
        if self.adjusted_hitbox and not self.crouching and not self.in_water and not self.jumping:
            print("resetting")
            self.angle = 0
            self.center_y += 16
            self.texture = self.idle_texture_pair[self.character_face_direction]

            physics_engine.remove_sprite(sprite=self)
            physics_engine.add_sprite(self,
                                      friction=PLAYER_FRICTION,
                                      mass=PLAYER_MASS,
                                      moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                      collision_type="player",
                                      max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                      max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
            self.height = PLAYER_IDLE_HEIGHT
            self.width = PLAYER_IDLE_WIDTH

# class Enemy():
#     """
#     This class was supposed to be similar to Player, but is now defunct. Will probably
#     delete soon and make an inherited version from Player class soon.
#     """
#
#     def __init__(self):
#         # set up parent class
#         super().__init__()
#         self.character_face_direction = LEFT_FACING
#         self.cur_texture = 0
#         self.spawnpoint = [0, 0]
#
#         self.jumping = False
#         self.scale = SPRITE_SCALING
#
#         main_path = "sprites/greenguy_walking"
#         self.idle_texture_pair = ar.load_texture_pair(f"{main_path}1.png")
#
#         # Adjust the collision box. Default includes too much empty space
#         # side-to-side. Box is centered at sprite center, (0, 0)
#         self.points = [[-75, -100], [80, -100], [80, 100], [-75, 100]]
#
#         # add walking sprites to list
#         self.walking_textures = []
#         for i in range(1, 6):
#             texture = ar.load_texture_pair(f"{main_path}{i}.png")
#             self.walking_textures.append(texture)
#
#     def update_animation(self, delta_time: float = 1 / 60):
#         # figure if we need to flip left or right
#         if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
#             self.character_face_direction = LEFT_FACING
#         if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
#             self.character_face_direction = RIGHT_FACING
#
#         if self.change_x == 0 and self.change_y == 0:
#             self.texture = self.idle_texture_pair[self.character_face_direction]
#             return
#
#         # walking animation
#         self.cur_texture += 1
#         if self.cur_texture > 4 * UPDATES_PER_FRAME:
#             self.cur_texture = 0
#         self.texture = self.walking_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]
