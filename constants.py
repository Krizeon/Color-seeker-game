"""
list of all constants used across all game python scripts
"""
from numpy import array as np

STARTING_LEVEL = 4

# screen size (currently 720p)
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280

# a 1 pixel-wide circle to be enlarged by multiplying it by a desired number size
CIRCLE = np([(1, 0), (0.966, 0.259), (0.866, 0.5), (0.707, 0.707), (0.5, 0.866), (0.259, 0.966),
                   (0, 1), (-0.259, 0.966), (-0.5, 0.866), (-0.707, 0.707), (-0.866, 0.5), (-0.966, 0.259),
                   (-1,0), (-0.966, -0.259), (-0.866, -0.5), (-0.707, -0.707), (-0.5, -0.866), (-0.259, -0.966),
                   (0,-1), (0.259, -0.966), (0.5, -0.866), (0.707, -0.707), (0.866, -0.5), (0.966, -0.259)
                   ])

CIRCLE_LARGE = list(CIRCLE*30)

# the color white in RGBA
WHITE = [255,255,255,255]

# frame rate of game (60)
FRAME_RATE = 1/60

# screen window title (working title is used
SCREEN_TITLE = "Color seeker!"

# angle offset for converting tmx angle to Sprite angles
ANGLE_OFFSET = 90

# scaling of sprites (mostly the player)
SPRITE_SCALING = 0.5

# scaling of tiles from .tmx files
TILE_SCALING = 0.5

# size of the files of sprites
SPRITE_PIXEL_SIZE = 128

# size of the grid in pixels, based on the current tile scaling
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# RGBA color constants
DEFAULT_COLOR = [255, 255, 255, 255]  # white
RED_COLOR = [255, 0, 0, 255]
BLUE_COLOR = [0, 0, 255, 255]
LIGHT_BLUE_COLOR = [102, 153, 255, 255]

# music constants
BG_MUSIC_VOLUME = 0.3

# time in milliseconds until player may take damage again
DAMAGE_BUFFER_TIME = 1000

# time in milliseconds until player can use cannon
CANNON_BUFFER_TIME = 500

WINDOW_TITLE = "Cool Game!"
PLAYER_SPRITE = "sprites/greenguy_walking"

# direction that the sprite is facing (right = 0, left=1)
LEFT_FACING = 1
RIGHT_FACING = 0

UPDATES_PER_FRAME = 8  # speed of the player animation

# physics related constants below
# gravity affects objects in the world. higher values, faster falling speeds
GRAVITY = 2800

# force of buoyancy in water
BUOYANCY_FORCE = 6050

# damping is the percentage of velocity lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.6

# friction of the player
PLAYER_FRICTION = 1.0

# mass of the player (higher values means one could push objects much easier)
PLAYER_MASS = 2.0

ENEMY_MASS = 10
ENEMY_FRICTION = 0.9

# friction of tiles that are deemed to be walls
WALL_FRICTION = 0.8

# friction of cannon block
CANNON_FRICTION = 0.2

# mass of cannons
CANNON_MASS = 30

PLAYER_MOVE_FORCE_ON_GROUND = 8000
ENEMY_MOVE_FORCE_ON_GROUND = 8000

# movement in water
PLAYER_MOVE_FORCE_IN_WATER = 200

# water friction/dampening
WATER_DAMPENING_FORCE = 400

# player water movement dead zone
WATER_DEAD_ZONE = 3

# max x/y speeds for player
PLAYER_MAX_HORIZONTAL_SPEED = 400
PLAYER_MAX_VERTICAL_SPEED = 1200

# max x speed while rolling
PLAYER_MAX_HORIZONTAL_SPEED_ROLLING = 700

PLAYER_MAX_HORIZONTAL_SPEED_IN_WATER = 250
PLAYER_MAX_VERTICAL_SPEED_IN_WATER = 250

PLAYER_HEAVY_WATER_DAMPENING = 6000

# close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# how many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 15

# force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 4000

# strength of a jump
PLAYER_JUMP_IMPULSE = 500

# strength of a jump while already in the air
PLAYER_JUMP_IMPULSE_IN_AIR = 250

# max height of a player's jump
PLAYER_MAX_JUMP_VELOCITY = 850

#force of a orb dash (spacebar+left/right)
BALL_DASH_IMPULSE = 700

# constants for player texture height, width, etc
PLAYER_IDLE_HEIGHT = 120 * SPRITE_SCALING
PLAYER_IDLE_WIDTH = 64 * SPRITE_SCALING
PLAYER_SWIM_HEIGHT = 60 * SPRITE_SCALING
PLAYER_SWIM_WIDTH = 120 * SPRITE_SCALING
PLAYER_BALL_RADIUS = 60 * SPRITE_SCALING

# strength of a cannon
CANNON_IMPULSE = 3000

# max cannon speed
CANNON_MAX_HORIZONTAL_SPEED = 1300
CANNON_MAX_VERTICAL_SPEED = 600

# boundaries of the viewport box, relative to the screen window's resolution
VIEWPORT_MARGIN_TOP = 200
VIEWPORT_MARGIN_BOTTOM = 200
VIEWPORT_RIGHT_MARGIN = 700
VIEWPORT_LEFT_MARGIN = 300
