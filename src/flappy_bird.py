# pylint:disable=E1101
""" Simple flappy bird game implementation """
import sys
import random
import pygame
import argparse
import matplotlib
import matplotlib.pyplot as plt
from agent import Agent

# settings for matplotlib so we can export graphs to latex
matplotlib.use("pgf")
matplotlib.rcParams.update(
    {
        "pgf.texsystem": "pdflatex",
        "font.family": "serif",
        "text.usetex": True,
        "pgf.rcfonts": False,
    }
)


# load images and their sizes
BACKGROUND = pygame.image.load("assets/img/background.png")
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = BACKGROUND.get_size()
BASE_IMAGE = pygame.image.load("assets/img/base.png")
BASE_IMAGE_WIDTH, BASE_IMAGE_HEIGHT = BASE_IMAGE.get_size()
BIRD_IMAGES_PATH = (
    "assets/img/bird_upflap.png",
    "assets/img/bird_midflap.png",
    "assets/img/bird_downflap.png",
)
PIPE_IMAGE_PATH = "assets/img/pipe.png"
RESTART_IMAGE_PATH = "assets/img/restart.png"
RESTART_IMAGE = pygame.image.load(RESTART_IMAGE_PATH)

# set screen size based on background and base
SCREEN_WIDTH = BACKGROUND_WIDTH
SCREEN_HEIGHT = BACKGROUND_HEIGHT + BASE_IMAGE_HEIGHT


def main():
    global FRAMERATE, CLOCK, SCREEN, ITER, DEBUG, agent
    pygame.init()

    # parse command line arguments
    parser = argparse.ArgumentParser("flappy_bird.py")
    parser.add_argument(
        "--iter", type=int, default=1000, help="number of game iterations to run"
    )
    parser.add_argument(
        "--debug", action="store_true", help="output debug logs to stdout"
    )
    parser.add_argument(
        "--fps",
        type=int,
        choices=[30, 60, 120],
        default=120,
        help="Frames per second; 30 = normal, 60 = fast, 120 = very fast",
    )
    arguments = parser.parse_args()

    # define framerate for the game so that events are synchronized
    CLOCK = pygame.time.Clock()
    FRAMERATE = arguments.fps
    DEBUG = arguments.debug
    ITER = arguments.iter

    # initialize the agent
    agent = Agent(DEBUG)

    # create game window
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")

    mainGame()


def draw_text(text, font, text_color, x, y):
    """Function used to draw text on top of the screen"""
    img = font.render(text, True, text_color)
    SCREEN.blit(img, (x, y))


def reset_game(flappy, bottom_pipe_group, top_pipe_group):
    """Restarting game variables, flappy bird position and re-generating pipes"""
    game_over = False
    # clear all the pipes
    bottom_pipe_group.empty()
    top_pipe_group.empty()
    # repostion the flappy bird to the starting position
    flappy.rect.x = 100
    flappy.rect.y = int(SCREEN_HEIGHT / 2)
    flappy.velocity = 0

    score = 0
    return game_over, score


def append_scores(scores, scores_avarages, score):
    scores.append(score)
    scores_avarages.append(sum(scores) / len(scores))


def end_game(scores, scores_avarages):
    """Dumping agent's qvalues, creating plotted graphs and ending the game"""
    agent.dump_qvalues(force=True)
    pygame.quit()
    y = scores
    x = [i + 1 for i in range(len(y))]
    max_score = max(scores)
    max_game_index = scores.index(max_score) + 1
    if DEBUG:
        print(f"Max score {max_score} at game {max_game_index}")
        print(f"Avarage at the end: {scores_avarages[-1]}")
    plt.scatter(x, y, color="black", marker=".", s=40)
    plt.scatter(
        max_game_index,
        max_score,
        color="red",
        marker=".",
        s=60,
        label=f"Max score",
    )
    plt.plot(x, scores_avarages, color="blue", label="Avarage", linewidth=2)
    plt.xlabel("Game")
    plt.ylabel("Score")
    # plt.xticks(x)
    # plt.yticks(scores)
    plt.legend()
    plt.savefig("data/scores.png", dpi=400)
    plt.savefig("data/scores.pgf")
    with open("data/scores.txt", 'w', encoding = 'utf-8') as f:
        f.write(f"Max score: {max_score} at game: {max_game_index}\n")
        f.write(f"Avarage at the end: {scores_avarages[-1]}\n")
        f.write("Scores:\n")
        f.write(f"{scores}\n")
        f.write("Avarages:\n")
        f.write(f"{scores_avarages}")
    sys.exit()


def generate_pipes(bottom_pipe_group, top_pipe_group, PIPE_GAP):
    """Generates two new pipes"""
    pipe_height = random.randint(-100, 100)
    bottom_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, -1, PIPE_GAP)
    top_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, 1, PIPE_GAP)
    bottom_pipe_group.add(bottom_pipe)
    top_pipe_group.add(top_pipe)


class Bird(pygame.sprite.Sprite):
    """Bird Sprite that is controlled by the player"""

    def __init__(self, x, y):
        # call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for bird_image_path in BIRD_IMAGES_PATH:
            self.images.append(pygame.image.load(bird_image_path))
        self.image = self.images[self.index]
        # create a rectangle of boundaries based on the image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        # set starting velocity to zero
        self.velocity = 0
        self.lmb_pressed = False

    def update(self, game_over, flying, agent_clicked):  # overwritten sprite function
        """Handles Bird animation and movement"""

        # movement handling
        # gravity
        if flying is True:
            self.velocity += 1
            # set a velocity limit
            self.velocity = min(self.velocity, 8)
            if self.rect.bottom < BACKGROUND_HEIGHT:
                self.rect.y += int(self.velocity)

        if game_over is False and flying is True:
            # flying up
            # lmb clicked
            # if pygame.mouse.get_pressed()[0] == 1 and self.lmb_pressed is False:
            #    self.lmb_pressed = True
            #    self.velocity = -10

            # if pygame.mouse.get_pressed()[0] == 0:
            #    self.lmb_pressed = False

            # if agent_clicked is True:
            #    agent_clicked = False
            #    self.velocity = -10

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
    MOVE_SPEED = 7  # by how much pixels to move a base in a single frame
    BASE_COLUMN_WIDTH = 24  # width of a single "column" of a base in pixels
    PIPE_GAP = 150  # the size of gap between top and bottom pipes
    PIPE_FREQUENCY = 900 * (30 / FRAMERATE)  # 900ms between generating new pipes
    score = 0
    scores = []
    scores_avarages = []
    last_pipe = pygame.time.get_ticks() - PIPE_FREQUENCY
    game_over = False
    agent_clicked = False
    flying = True  # bool for checking flying animation
    WAS_PIPE_PASSED = (
        False  # variable for tracking score, tracks wheter bird passed a pipe
    )
    # define font for displaying score
    font = pygame.font.SysFont("Fira Mono", 60)
    # define colors
    white = (255, 255, 255)

    bird_group = pygame.sprite.Group()
    top_pipe_group = pygame.sprite.Group()
    bottom_pipe_group = pygame.sprite.Group()
    last_pipe = pygame.time.get_ticks() - PIPE_FREQUENCY
    closest_pipe = None

    flappy = Bird(100, int(SCREEN_HEIGHT / 2))

    bird_group.add(flappy)

    restart_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, RESTART_IMAGE)

    # main game loop
    while True:

        CLOCK.tick(FRAMERATE)

        # draw background on screen
        SCREEN.blit(BACKGROUND, (0, 0))

        # draw pipes
        top_pipe_group.draw(SCREEN)
        bottom_pipe_group.draw(SCREEN)

        # generate new pipes
        if flying is True:
            time_now = pygame.time.get_ticks()
            # enough time has passed to generate a new pipe
            if time_now - last_pipe > PIPE_FREQUENCY:
                generate_pipes(bottom_pipe_group, top_pipe_group, PIPE_GAP)
                last_pipe = time_now

        # check what pipe to the right is the closes to flappy bird
        # it can be either 1st pipe on the list or the 2nd
        if len(bottom_pipe_group) > 0:
            if -flappy.rect.centerx + bottom_pipe_group.sprites()[0].rect.centerx > -30:
                closest_pipe = bottom_pipe_group.sprites()[0]
            else:
                closest_pipe = bottom_pipe_group.sprites()[1]

        # agent action check
        if agent.act(
            -flappy.rect.centerx + closest_pipe.rect.centerx,
            -flappy.rect.centery + closest_pipe.rect.centery,
            flappy.velocity,
        ):
            agent_clicked = True
            flappy.velocity = -10
            if DEBUG:
                print("Agent clicked")

        # draw and update bird
        bird_group.draw(SCREEN)
        bird_group.update(game_over, flying, agent_clicked)

        # draw the ground
        SCREEN.blit(BASE_IMAGE, (BASE_MOVE, BACKGROUND_HEIGHT))

        # check score
        if len(bottom_pipe_group) > 0:  # some pipes have been created
            if (
                bird_group.sprites()[0].rect.left
                > bottom_pipe_group.sprites()[0].rect.left
                and bird_group.sprites()[0].rect.right
                < bottom_pipe_group.sprites()[0].rect.right
                and WAS_PIPE_PASSED is False
            ):  # bird is between top and bottom pipe
                WAS_PIPE_PASSED = True
            if WAS_PIPE_PASSED is True:
                # and if bird has left the area between top and bottom pipe
                if (
                    bird_group.sprites()[0].rect.left
                    > bottom_pipe_group.sprites()[0].rect.right
                ):
                    score += 1
                    WAS_PIPE_PASSED = False
        draw_text(str(score), font, white, int(SCREEN_WIDTH / 2), 30)

        # check if any collision occured
        if (
            pygame.sprite.groupcollide(bird_group, bottom_pipe_group, False, False)
            or pygame.sprite.groupcollide(bird_group, top_pipe_group, False, False)
            or flappy.rect.top < 0
        ):
            game_over = True

        # check if the bird hit the ground
        if flappy.rect.bottom >= BACKGROUND_HEIGHT:
            game_over = True
            # flying = False

        if game_over is False and flying is True:
            # draw and move the base
            BASE_MOVE -= MOVE_SPEED
            if abs(BASE_MOVE) > BASE_COLUMN_WIDTH:
                BASE_MOVE = 0
            # update pipes
            bottom_pipe_group.update(MOVE_SPEED)
            top_pipe_group.update(MOVE_SPEED)

        if game_over is True:
            if DEBUG:
                print("Game over, updating scores")
            agent.update_scores()
            append_scores(scores, scores_avarages, score)
            game_over, score = reset_game(flappy, bottom_pipe_group, top_pipe_group)
            # restart_button.draw()
            # if restart_button.is_button_clicked() is True:
            #    game_over, score = reset_game(flappy, bottom_pipe_group, top_pipe_group)

        # event handling
        for event in pygame.event.get():
            # stop running the game if ESC is pressed
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                append_scores(scores, scores_avarages, score)
                end_game(scores, scores_avarages)
            # start game
            # if (
            #    event.type == pygame.MOUSEBUTTONDOWN
            #    and flying is False
            #    and game_over is False
            # ):
            #    flying = True

        # end game if we have reached game iterations
        if agent.game_count == ITER:
            end_game(scores, scores_avarages)

        # update everything that has happened to the game
        pygame.display.update()


if __name__ == "__main__":
    main()
