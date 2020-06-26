from .mcts import *
from .configs import *

class Evaluate(object):
    #Class to evaluate the trained model

    # def __init__(self, eval_mcts):
    #     self.eval_mcts = eval_mcts
    #     self.gas_network = gas_network

    def evaluate(self, penalty):

        wins = 0
        losses = 0

        for i in range(len(penalty)):

            if penalty[i][0] < penalty[i][1] or penalty[i][0] == 0 or penalty[i][0] < 10:
                wins += 1
            elif penalty[i][0] > penalty[i][1] or penalty[i][0] > 100:
                losses += 1
            else:
                print("Draw")
            print("\n")
        num_games = wins + losses
        if num_games == 0:
            win_ratio = 0
        else:
            win_ratio = wins / num_games

        return win_ratio
