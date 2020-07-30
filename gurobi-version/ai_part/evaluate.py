from .mcts import *
from .configs import *


class Evaluate(object):
    #Class to evaluate the trained model

    def __init__(self, net):
        self.nnet = net

    def evaluate(self):

        wins = 0
        losses = 0

        for i in range(len(penalties)):

            if penalties[i][0] < penalties[i][1] or penalties[i][0] <= 10:
                wins += 1
            elif penalties[i][0] > penalties[i][1] or penalties[i][0] > 10:
                losses += 1
            else:
                print("Draw")
            #print("\n")
        num_games = wins + losses
        if num_games == 0:
            win_ratio = 0
        else:
            win_ratio = wins / num_games

        print("Win rate: ", win_ratio)
        if win_ratio > 0.55:
            print("New model saved as the best model")
            self.nnet.save_model("best_model")
        else:
            print("New model is not the best model.")
            self.nnet.load_model()

        #return win_ratio
