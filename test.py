from ple.games.flappybird import FlappyBird
from ple import PLE
from random import choice

class myAgent:
    def __init__(self, allowed_actions):
        self.allowed_actions = allowed_actions

    def pickAction(self, reward, observation):
        # pick random action
        return choice(self.allowed_actions)


game = FlappyBird()
p = PLE(game, fps=30, display_screen=True)
agent = myAgent(allowed_actions=p.getActionSet())

p.init()
reward = 0.0
nb_frames = 100000

for i in range(nb_frames):
   if p.game_over():
           p.reset_game()

   observation = p.getScreenRGB()
   action = agent.pickAction(reward, observation)
   reward = p.act(action)
