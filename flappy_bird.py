# pylint:disable=E1101
""" Simple flappy bird game implementation """
import sys
import random
import pygame

# load images and their sizes
background = pygame.image.load("assets/img/background.png")
background_width, background_height = background.get_size()
base_image = pygame.image.load("assets/img/base.png")
base_image_width, base_image_height = base_image.get_size()
bird_images_path = (
    "assets/img/bird_upflap.png",
    "assets/img/bird_midflap.png",
    "assets/img/bird_downflap.png",
)
PIPE_IMAGE_PATH = "assets/img/pipe.png"
RESTART_IMAGE_PATH = "assets/img/restart.png"
restart_image = pygame.image.load(RESTART_IMAGE_PATH)

# set screen size based on background and base
screen_width = background_width
screen_height = background_height + base_image_height

def main():
    global FRAMERATE, CLOCK, SCREEN, font, white
    pygame.init()

    # define framerate for the game so that events are synchronized
    CLOCK = pygame.time.Clock()
    FRAMERATE = 30


    # create game window
    SCREEN = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Flappy Bird")

    # define font for displaying score
    font = pygame.font.SysFont("Fira Mono", 60)


    # define colors
    white = (255, 255, 255)

    mainGame()


def draw_text(text, font, text_color, x, y):
    """Function used to draw text on top of the screen"""
    img = font.render(text, True, text_color)
    SCREEN.blit(img, (x, y))


def reset_game(flappy, pipe_group):
    """Restarting game variables and flappy bird position"""
    game_over = False
    # clear all the pipes
    pipe_group.empty()
    # repostion the flappy bird to the starting position
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)

    score = 0
    return game_over, score


class Bird(pygame.sprite.Sprite):
    """Bird Sprite that is controlled by the player"""

    def __init__(self, x, y):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for bird_image_path in bird_images_path:
            self.images.append(pygame.image.load(bird_image_path))
        self.image = self.images[self.index]
        # create a rectangle of boundaries based on the image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        # set starting velocity to zero
        self.velocity = 0
        self.lmb_pressed = False

    def update(self, game_over, flying, DEBUG):  # overwritten sprite function
        """Handles Bird animation and movement"""

        # movement handling
        # gravity
        if flying is True:
            self.velocity += 1
            # set a velocity limit
            self.velocity = min(self.velocity, 8)
            if self.rect.bottom < background_height:
                self.rect.y += int(self.velocity)

        if game_over is False and flying is True:
            # flying up
            # lmb clicked
            if pygame.mouse.get_pressed()[0] == 1 and self.lmb_pressed is False:
                self.lmb_pressed = True
                self.velocity = -10

            if pygame.mouse.get_pressed()[0] == 0:
                self.lmb_pressed = False

            if DEBUG is True:
                print(
                    f"({pygame.time.get_ticks() / 1000}) Current velocity : {self.velocity}"
                )

            # animation handling
            self.counter += 1
            flap_cooldown = 2

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                self.index %= len(self.images)
            self.image = self.images[self.index]

            # rotate the bird
            self.image = pygame.transform.rotate(
                self.images[self.index], self.velocity * -2
            )
        # "dead" bird effect when game is over
        elif game_over is True:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        # correct rotation when game has been restarted
        elif game_over is False and flying is False:
            self.image = pygame.transform.rotate(self.images[self.index], 0)


class Pipe(pygame.sprite.Sprite):
    """Class representing Pipes"""

    def __init__(self, x, y, position, PIPE_GAP):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(PIPE_IMAGE_PATH)
        self.rect = self.image.get_rect()
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            # flip the pipe
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(PIPE_GAP / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(PIPE_GAP / 2)]

    def update(self, MOVE_SPEED):
        """Overload of Sprite class Update method used to move pipe to the left
        and delete it if it goes out of screen"""
        self.rect.x -= MOVE_SPEED
        if self.rect.right < 0:
            self.kill()


class Button:
    """Class representing a button used only by restart button in our case"""

    def __init__(self, x_coord, y_coord, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_coord, y_coord)
        self.image_width, self.image_height = self.image.get_size()
        self.image_width /= 2
        self.image_height /= 2
        self.lmb_pressed = False

    def draw(self):
        """Function to draw button on the screen roughly in the middle"""
        SCREEN.blit(
            self.image,
            (self.rect.x - self.image_width, self.rect.y - self.image_height),
        )

    def is_button_clicked(self):
        """Predicate determining whether the button has been clicked"""
        action = False
        if pygame.mouse.get_pressed()[0] == 1 and self.lmb_pressed is False:
            action = True
            self.lmp_pressed = True
        elif pygame.mouse.get_pressed()[0] == 0:
            self.lmb_pressed = False
        return action


def mainGame():
    # define game variables
    BASE_MOVE = 0
    MOVE_SPEED = 6  # by how much pixels to move a base in a single frame
    BASE_COLUMN_WIDTH = 24  # width of a single "column" of a base in pixels
    PIPE_GAP = 150  # the size of gap between top and bottom pipes
    PIPE_FREQUENCY = 900  # 900ms between generating new pipes
    last_pipe = pygame.time.get_ticks() - PIPE_FREQUENCY
    score = 0
    game_over = False
    flying = False  # bool for checking flying animation
    WAS_PIPE_PASSED = (
        False  # variable for tracking score, tracks wheter bird passed a pipe
    )
    DEBUG = False
    if "debug" in sys.argv:
        DEBUG = True

    bird_group = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()

    flappy = Bird(100, int(screen_height / 2))

    bird_group.add(flappy)

    restart_button = Button(screen_width / 2, screen_height / 2, restart_image)

    # main game loop
    while True:

        CLOCK.tick(FRAMERATE)

        # draw background on screen
        SCREEN.blit(background, (0, 0))

        # draw bird
        bird_group.draw(SCREEN)
        bird_group.update(game_over, flying, DEBUG)

        # draw pipes
        pipe_group.draw(SCREEN)

        # draw the ground
        SCREEN.blit(base_image, (BASE_MOVE, background_height))

        # check score
        if len(pipe_group) > 0:  # some pipes have been created
            if (
                bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left
                and bird_group.sprites()[0].rect.right
                < pipe_group.sprites()[0].rect.right
                and WAS_PIPE_PASSED is False
            ):  # bird is between top and bottom pipe
                WAS_PIPE_PASSED = True
            if WAS_PIPE_PASSED is True:
                # and if bird has left the area between top and bottom pipe
                if (
                    bird_group.sprites()[0].rect.left
                    > pipe_group.sprites()[0].rect.right
                ):
                    score += 1
                    WAS_PIPE_PASSED = False
        draw_text(str(score), font, white, int(screen_width / 2), 30)

        # check if any collision occured
        if (
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False)
            or flappy.rect.top < 0
        ):
            game_over = True

        # check if the bird hit the ground
        if flappy.rect.bottom >= background_height:
            game_over = True
            flying = False

        if game_over is False and flying is True:
            # generate new pipes
            time_now = pygame.time.get_ticks()
            # enough time has passed to generate a new pipe
            if time_now - last_pipe > PIPE_FREQUENCY:
                pipe_height = random.randint(-100, 100)
                bottom_pipe = Pipe(
                    screen_width, int(screen_height / 2) + pipe_height, -1, PIPE_GAP
                )
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1, PIPE_GAP)
                pipe_group.add(bottom_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            # draw and move the base
            BASE_MOVE -= MOVE_SPEED
            if abs(BASE_MOVE) > BASE_COLUMN_WIDTH:
                BASE_MOVE = 0
            # update pipes
            pipe_group.update(MOVE_SPEED)

        if game_over is True:
            restart_button.draw()
            if restart_button.is_button_clicked() is True:
                if DEBUG is True:
                    print(
                        f"({pygame.time.get_ticks() / 1000}) Restart button has been clicked!"
                    )
                game_over, score = reset_game(flappy, pipe_group)

        # event handling
        for event in pygame.event.get():
            # stop running the game if ESC is pressed
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            # start game
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and flying is False
                and game_over is False
            ):
                flying = True

        # update everything that has happened to the game
        pygame.display.update()


if __name__ == "__main__":
    main()
