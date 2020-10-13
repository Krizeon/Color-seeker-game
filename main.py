import arcade as ar
import pymunk as pm
import time


SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
SCREEN_TITLE = "Color seeker!"
SCALING = 1
SPRITE_SCALING = 0.5
TILE_SCALING = 0.6
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

DEFAULT_COLOR = [255,255,255,255]
RED_COLOR = [255,0,0,255]
DAMAGE_BUFFER_TIME = 1000 # time in milliseconds until player may take damage again


WINDOW_TITLE = "Cool Game!"
PLAYER_SPRITE="sprites/greenguy_walking"

# direction that the sprite is facing
LEFT_FACING = 1
RIGHT_FACING = 0

UPDATES_PER_FRAME = 15
GRAVITY = 0.5
JUMP_SPEED = 9
MOVEMENT_SPEED = 4

VIEWPORT_MARGIN_TOP = 200
VIEWPORT_MARGIN_BOTTOM = 200
VIEWPORT_RIGHT_MARGIN = 500
VIEWPORT_LEFT_MARGIN = 300

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        ar.load_texture(filename),
        ar.load_texture(filename, flipped_horizontally=True)
    ]

class Window():
    def __init__(self, window):
        pass

class PlayerCharacter(ar.Sprite):
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

    def update_animation(self, delta_time: float = 1/60):
        # figure if we need to flip left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # change to crouching sprite if holding DOWN or S
        if self.crouching and self.change_x == 0:
            # self.points = [[-40, -30], [40, -30], [40, 25], [-40, 25]]
            self.texture = self.crouching_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        if self.change_x == 0 and self.change_y == 0 and not self.crouching:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        # idle texture
        if self.change_x == 0 and not self.crouching:
            # self.points = self.default_points
            self.texture = self.idle_texture_pair[self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        # walking animation
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

    def on_show(self):
        """ This is run once when we switch to this view """
        ar.set_background_color(ar.csscolor.BLUE_VIOLET)

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
            game_view = GameView()
            self.window.show_view(game_view)

class GameView(ar.View):
    """
    Main game window
    Player moves and jumps across platforms and avoids dangerous enemies

    """

    def __init__(self):
        """Initialize the game
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


    def setup(self):
        """Get the game ready to play
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

        self.load_level(self.level)

        # check if there is a "game over"
        self.game_over = False

        # Unpause the game, reset collision timer
        self.paused = False
        self.collided = False
        self.collision_timer = 0.0

    def load_level(self, level):
        my_map = ar.tilemap.read_tmx(f"maps/map{level}.tmx")
        self.height = my_map.map_size.height
        self.width = my_map.map_size.width
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        self.wall_list = ar.tilemap.process_layer(my_map,
                                                  layer_name='Foreground',
                                                  scaling=TILE_SCALING,
                                                  use_spatial_hash=True)
        self.physics_engine = ar.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)
        self.enemies_list = ar.tilemap.process_layer(my_map,
                                                     layer_name='Enemies',
                                                     scaling=TILE_SCALING,
                                                     use_spatial_hash=True)
        self.view_left = 0
        spawn_coords = ar.get_tilemap_layer(map_object=my_map, layer_path="Player Spawn")
        self.view_bottom = 0

    def on_key_release(self, key: int, modifiers: int):
        if key == ar.key.LEFT or key == ar.key.A:
            self.player.change_x = 0
        elif key == ar.key.RIGHT or key == ar.key.D:
            self.player.change_x = 0
        elif key == ar.key.DOWN or key == ar.key.S:
            self.player.crouching = False

    def on_key_press(self, symbol: int, modifiers: int):
        """
        controls movement of player, as well as other key inputs
        :param symbol:
        :param modifiers:
        :return:
        """
        if symbol == ar.key.Q:
            # Quit immediately
            ar.close_window()

        # pause game
        if symbol == ar.key.P:
            self.paused = not self.paused
            view = PauseView()
            self.window.show_view(view)

        # jump up
        if symbol == ar.key.W or symbol == ar.key.UP:
            if not self.player.crouching:
                if self.physics_engine.can_jump():
                    self.player.change_y = JUMP_SPEED
                    self.player.jumping = True
            # self.player.change_y = 5
            # self.player.jumping = True

        # crouch (squish in half)
        if symbol == ar.key.S or symbol == ar.key.DOWN:
            if not self.player.jumping:
                self.player.crouching = True

        # move left
        if symbol == ar.key.A or symbol == ar.key.LEFT:
            if not self.player.crouching:
                self.player.change_x = -MOVEMENT_SPEED

        # move right
        if (symbol == ar.key.D or symbol == ar.key.RIGHT):
            if not self.player.crouching:
                self.player.change_x = MOVEMENT_SPEED

    def process_damage(self):
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
            self.player.center_x, self.player.center_y = self.player.spawnpoint
            self.player.health = 99

    def on_update(self, delta_time: float):
        """
        Update the positions and statuses of all game objects
        If paused, do nothing

        Arguments:
            delta_time {float} -- Time since the last update
        """

        # If paused, don't update anything
        if self.paused:
            return

        if not self.game_over:
            self.physics_engine.update()

        # Update everything
        self.player_list.update()
        self.player_list.update_animation()
        self.all_sprites.update()
        self.enemies_list.update()

        if self.player.change_y != 0:
            self.player.jumping = True

        self.process_damage()

        # if player gets to the right edge of the level, go to next level
        if self.player.right >= self.end_of_map:
            self.level += 1 # switch to next level
            self.load_level(self.level)
            self.player.spawnpoint = [100,125]
            self.player.center_x, self.player.center_y = self.player.spawnpoint

        # if the player hits the bottom of the level, player dies and respawns at the start of the level
        if self.player.bottom <= 0:
            self.level += 1 # switch to next level
            self.load_level(self.level)
            self.player.center_x, self.player.center_y = self.player.spawnpoint

        # Keep the player on screen, within the confines of the map
        # if self.player.top > self.height:
        #     self.player.top = self.height
        # if self.player.right > self.width:
        #     self.player.right = self.width
        # if self.player.bottom < 0:
        #     self.player.bottom = 0
        # if self.player.left < 0:
        #     self.player.left = 0

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

if __name__ == '__main__':
    # new_game = Game(int(SCREEN_WIDTH * SCALING), int(SCREEN_HEIGHT * SCALING), WINDOW_TITLE)
    # new_game.setup()

    window = ar.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    ar.run()
    # ar.open_window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, window_title=WINDOW_TITLE, resizable=False)
    # ar.set_background_color(ar.color.BLACK)
    # # ar.load_spritesheet(PLAYER_SPRITE, sprite_width=839, sprite_height=229, columns=5, count=5)
    # Game.setup(ar.Window)
    # ar.start_render()
    # ar.draw_circle_filled(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 20, ar.color.BLUE_GREEN)
    # ar.finish_render()
    # ar.run()
