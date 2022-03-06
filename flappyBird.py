import pygame
from pygame.locals import *
from PIL import Image  # to get dimentions of asset images


pygame.init()

# define framerate for the game so that events are synchronized
clock = pygame.time.Clock()
framerate = 60

# load images and their sizes
background = pygame.image.load("assets/img/background.png")
background_width, background_height = background.get_size()
base = pygame.image.load("assets/img/base.png")
base_width, base_height = base.get_size()

# set screen size based on background and base
screen_width = background_width
screen_height = background_height + base_height

# create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# define game variables
base_move = 0
move_speed = 3 # by how much pixels to move a base in a single frame
base_column_width = 24 # width of a single "column" of a base in pixels

# main game loop
run = True
while run:

    clock.tick(framerate)

    # draw background on screen
    screen.blit(background, (0, 0))

    # draw and move the base
    screen.blit(base, (base_move, background_height))
    base_move -= move_speed
    if abs(base_move) > base_column_width:
        base_move = 0

    for event in pygame.event.get():
        # stop running the game if X is pressed
        if event.type == pygame.QUIT:
            run = False

    # update everything that has happened to the game
    pygame.display.update()

pygame.quit()
