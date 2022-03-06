import pygame
from pygame.locals import *

pygame.init()

# dimentions of background.png
screen_width = 576
screen_height = 512

# create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# load images
background = pygame.image.load("assets/img/background.png")

# create game loop
run = True
while run:

    # apply background to screen
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        # stop running the game if X is pressed
        if event.type == pygame.QUIT:
            run = False

    # update everything that has happened to the game
    pygame.display.update()

pygame.quit()
