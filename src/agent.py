"""Agent class"""
import json


class Agent(object):
    """
    The Agent class that applies the Qlearning logic to Flappy bird game
    After every iteration (iteration = 1 game that ends with the bird dying) updates Q values
    After every DUMPING_N iterations, dumps the  values to the local JSON file
    """

    def __init__(self, debug):
        self.game_count = 0  # Game count of current run, incremented after every death
        self.DUMPING_N = 25  # Number of iterations to dump Q values to JSON after
        self.discount = 1.0
        self.reward = {0: 1, 1: -1000}  # Reward function
        self.lr = 0.7
        self.load_qvalues()
        self.last_state = "500_280_0"
        self.last_action = 0
        self.moves = []
        self.debug = debug

    def load_qvalues(self):
        """
        Load q values from a JSON file
        """
        self.qvalues = {}
        try:
            fil = open("data/qvalues.json", "r")
        except IOError:
            return
        self.qvalues = json.load(fil)
        fil.close()

    def act(self, xdif, ydif, vel):
        """
        Chooses the best action with respect to the current state
        Chooses 0 (don't flap) to tie-break
        """
        state = self.map_state(xdif, ydif, vel)

        self.moves.append(
            (self.last_state, self.last_action, state)
        )  # Add the experience to the history

        self.last_state = state  # Update the last_state with the current state

        if self.qvalues[state][0] >= self.qvalues[state][1]:
            self.last_action = 0
            return 0
        else:
            self.last_action = 1
            return 1

    def update_scores(self, dump_qvalues=True):
        """
        Update qvalues via iterating over experiences
        """
        history = list(reversed(self.moves))

        # if bird died to collapsing into top pipe higher than 120 units mark that
        # for extra penalty
        if int(history[0][2].split("_")[1]) > 120:
            top_pipe_death = True
        else:
            top_pipe_death = False

        # Q-learning score updates
        t = 1
        for experience in history:
            state = experience[0]
            act = experience[1]
            res_state = experience[2]

            # Select reward
            if t == 1 or t == 2:
                cur_reward = self.reward[1]
            elif top_pipe_death and act:
                cur_reward = self.reward[1]
                top_pipe_death = False
            else:
                cur_reward = self.reward[0]

            # Update
            self.qvalues[state][act] = (1 - self.lr) * (
                self.qvalues[state][act]
            ) + self.lr * (cur_reward + self.discount * max(self.qvalues[res_state]))

            t += 1

        self.game_count += 1  # increase game count
        if dump_qvalues:
            self.dump_qvalues()  # Dump q values (if game count % DUMPING_N == 0)
        self.moves = []  # clear history after updating strategies

    def map_state(self, xdif, ydif, vel):
        """
        Map the (xdif, ydif, vel) to the respective state, with regards to the grids
        The state is a string, "xdif_ydif_vel"
        """
        if self.debug:
            print(f"Xdif: {xdif};  Ydif: {ydif};   Vel: {vel}")
        xdif = int(xdif) - (int(xdif) % 5)
        ydif = int(ydif) - (int(ydif) % 5)

        state = str(int(xdif)) + "_" + str(int(ydif)) + "_" + str(vel)
        if self.debug:
            print(f"Curr state: {state}")
        return state

    def dump_qvalues(self, force=False):
        """
        Dump the qvalues to the JSON file
        """
        if self.game_count % self.DUMPING_N == 0 or force:
            print(f"game count: {self.game_count}")
            fil = open("data/qvalues.json", "w")
            json.dump(self.qvalues, fil)
            fil.close()
            print("Q-values updated on local file.")
