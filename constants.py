"""
list of all constants used across all game python scripts
"""
# screen size (currently 720p)
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280

# screen window title (working title is used
SCREEN_TITLE = "Color seeker!"

SCALING = 1  # might be useful to remove this

# scaling of sprites (mostly the player)
SPRITE_SCALING = 0.6

# scaling of tiles from .tmx files
TILE_SCALING = 0.6

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

WINDOW_TITLE = "Cool Game!"
PLAYER_SPRITE = "sprites/greenguy_walking"

# direction that the sprite is facing (right = 0, left=1)
LEFT_FACING = 1
RIGHT_FACING = 0

UPDATES_PER_FRAME = 10  # may not be necessary anymore?

# physics related constants below
# gravity affects objects in the world. higher values, faster falling speeds
GRAVITY = 2400

# damping is the percentage of velocity lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# friction of the player
PLAYER_FRICTION = 1.0

# mass of the player (higher values means one could push objects much easier)
PLAYER_MASS = 2.0

ENEMY_MASS = 10
ENEMY_FRICTION = 0.9

# friction of tiles that are deemed to be walls
WALL_FRICTION = 0.8

PLAYER_MOVE_FORCE_ON_GROUND = 8000
ENEMY_MOVE_FORCE_ON_GROUND = 8000

# max x/y speeds
PLAYER_MAX_HORIZONTAL_SPEED = 600
PLAYER_MAX_VERTICAL_SPEED = 1300

# close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# how many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 15

# force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 3000

# strength of a jump
PLAYER_JUMP_IMPULSE = 2000

# boundaries of the viewport box, relative to the screen window's resolution
VIEWPORT_MARGIN_TOP = 200
VIEWPORT_MARGIN_BOTTOM = 200
VIEWPORT_RIGHT_MARGIN = 500
VIEWPORT_LEFT_MARGIN = 300
