from .mcts import *
from .configs import *

class Evaluate(object):
    #Class to evaluate the trained model

    def __init__(self, eval_mcts, gas_network):
        #self.current_mcts = current_mcts
        self.eval_mcts = eval_mcts
        self.gas_network = gas_network

    def evaluate(self):

        wins = 0
        losses = 0

        for i in range(CFG.num_evaluation_plays):

            gas_network = self.gas_network.clone()
            iteration_over = False
            value = 0
            node = TreeNode()

            while not iteration_over:

                best_child = self.eval_mcts.search(gas_network, node, CFG.temp_final)

                action = best_child.action
                gas_network.take_action(action)

                iteration_over, value = gas_network.get_reward()

                best_child.parent = None
                node = best_child

            if value == 1:
                wins +=  1
            elif value == -1:
                losses += 1
            else:
                print("Draw")
            print("\n")

        return wins, losses
