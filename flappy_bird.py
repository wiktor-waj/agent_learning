""" Simple flappy bird game implementation """
import pygame
from PIL import Image  # to get dimentions of asset images


# from pygame.locals import *
pygame.init()

# define framerate for the game so that events are synchronized
clock = pygame.time.Clock()
framerate = 30

# load images and their sizes
background = pygame.image.load("assets/img/background.png")
background_width, background_height = background.get_size()
base = pygame.image.load("assets/img/base.png")
base_width, base_height = base.get_size()
bird_images = (
    "assets/img/bird_upflap.png",
    "assets/img/bird_midflap.png",
    "assets/img/bird_downflap.png",
)

# set screen size based on background and base
screen_width = background_width
screen_height = background_height + base_height

# create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bird")

# define game variables
base_move = 0
move_speed = 4  # by how much pixels to move a base in a single frame
base_column_width = 24  # width of a single "column" of a base in pixels


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for bird_image in bird_images:
            self.images.append(pygame.image.load(bird_image))
        self.image = self.images[self.index]
        # create a rectangle of boundaries based on the image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):  # overwritten sprite function
        """Handles Bird animation"""
        self.counter += 1
        flap_cooldown = 5

        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            self.index %= len(self.images)
            self.image = self.images[self.index]


bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

# main game loop
while True:

    clock.tick(framerate)

    # draw background on screen
    screen.blit(background, (0, 0))

    # draw bird
    bird_group.draw(screen)
    bird_group.update()

    # draw and move the base
    screen.blit(base, (base_move, background_height))
    base_move -= move_speed
    if abs(base_move) > base_column_width:
        base_move = 0

    for event in pygame.event.get():
        # stop running the game if ESC is pressed
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    # update everything that has happened to the game
    pygame.display.update()
