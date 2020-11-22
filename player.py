import arcade as ar
from constants import *


class PlayerCharacter(ar.Sprite):
    """
    the main player object. it is based on an Arcade Sprite object.
    """

    def __init__(self):
        # set up parent class
        super().__init__()

        self._hit_box_algorithm = "None"
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.spawnpoint = [0, 0]
        self.health = 0
        self.default_color = [255, 255, 255, 255]
        self.color = [0, 0, 0, 0]  # color is RGBA, 4th int being opacity between 0-255
        self.took_damage = False
        self.time_last_hit = 0
        self.crouching = False  # is the player crouching?
        self.default_points = [[-40, -60], [40, -60], [40, 50], [-40, 50]]
        self.adjusted_hitbox = False  # this is a "latch", used for handling crouching.

        self.jumping = False  # is the player jumping?
        self.scale = SPRITE_SCALING

        # How far have we traveled horizontally since changing the texture
        self.x_odometer = 0

        # How far have we traveled vertically since changing the texture
        self.y_odometer = 0

        main_path = "sprites/player_sprites/player"

        # add idle texture
        self.idle_texture_pair = ar.load_texture_pair(f"{main_path}_idle.png")

        # add crouching texture
        self.crouching_texture_pair = ar.load_texture_pair(f"{main_path}_squished.png", hit_box_algorithm="None")

        # add jumping texture
        self.jumping_texture_pair = ar.load_texture_pair(f"{main_path}_jumping.png")

        # add walking sprites to list
        self.walking_textures = []
        for i in range(1, 15):
            texture = ar.load_texture_pair(f"{main_path}walking{i}.png")
            self.walking_textures.append(texture)

        self.texture = self.idle_texture_pair[0]
        self.set_hit_box(self.texture.hit_box_points)

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """
        handle animation when pymunk detects the player is moving
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
        # is_on_ground = physics_engine.is_on_ground(self)

        # Add to the odometer how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        # change to crouching sprite if holding DOWN or S
        if self.crouching:
            self.texture = self.crouching_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)

            # in order to make the player smaller when crouching for the physics engine,
            # remove the player from the physics engine and add it back right away.
            # this makes the process of recreating the physics body and shape automatic.
            if not self.adjusted_hitbox:
                physics_engine.remove_sprite(sprite=self)
                physics_engine.add_sprite(self,
                                          friction=0.2,
                                          mass=PLAYER_MASS,
                                          moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                          collision_type="player",
                                          max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                          max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
            self.adjusted_hitbox = True
            return

        # idle texture
        if abs(dx) <= DEAD_ZONE and not self.jumping:
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
                self.adjusted_hitbox = False

        # jumping texture
        if self.jumping:
            self.texture = self.jumping_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        # walking animation
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0
            # do the walking animation
            self.cur_texture += 13
            if self.cur_texture > 13 * UPDATES_PER_FRAME:
                self.cur_texture = 0
            self.texture = self.walking_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]

        # if player isn't crouching, set physics shape back to default size
        if self.adjusted_hitbox:
            physics_engine.remove_sprite(sprite=self)
            physics_engine.add_sprite(self,
                                      friction=PLAYER_FRICTION,
                                      mass=PLAYER_MASS,
                                      moment=ar.PymunkPhysicsEngine.MOMENT_INF,
                                      collision_type="player",
                                      max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                      max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)
            self.adjusted_hitbox = False


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
