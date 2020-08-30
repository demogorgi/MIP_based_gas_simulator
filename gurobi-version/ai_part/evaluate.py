from .mcts import *
from .configs import *
from params import *

class Evaluate(object):
    #Class to evaluate the trained model

    def __init__(self, net):
        self.nnet = net

    def evaluate(self):

        wins = 0
        losses = 0

        for i in range(len(c_values)):

            if i%config['decision_freq'] == 0:
                if abs(c_values[i]) < config['winning_threshold']:
                    wins += 1
                elif abs(c_values[i]) > config['winning_threshold']:
                    losses += 1
                else:
                    print("Draw")

        num_steps = wins + losses
        if num_steps == 0:
            win_ratio = 0
        else:
            win_ratio = wins / num_steps
        win_ratios.append(win_ratio)
        print("Win rate: ", win_ratio)
        if win_ratio > 0.55:
            print("New model saved as the best model")
            self.nnet.save_model("best_model")
        else:
            print("New model is not the best model.")
            self.nnet.load_model()

        #return win_ratio
