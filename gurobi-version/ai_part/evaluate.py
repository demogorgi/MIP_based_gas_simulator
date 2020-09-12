from .mcts import *
from .configs import *
from params import *
from .functions_ai import *

class Evaluate(object):
    #Class to evaluate the trained model

    def __init__(self, current_mcts, decisions, gas_network):
        self.nnet = current_mcts
        self.gas_network = gas_network
        self.decisions = decisions

    def evaluate(self):
        wins = 0
        losses = 0
        step = self.gas_network.next_step

        for i in range(configs.nums_eval_plays):
            node = TreeNode()
            gas_network = deepcopy(self.gas_network)
            k = 0

            a = random.randrange(0, 1100, 50)
            gas_network.nom_EN, gas_network.nom_EH = a, 1100-a
            decisions = gas_network.set_nominations(gas_network.nom_EH)
            gas_network.possible_decisions = gas_network.get_valid_actions()

            while(k+2 <= config['decision_freq']):
                best_child = self.nnet.search(gas_network, node, configs.temperature)
                action = best_child.action
                decisions = gas_network.generate_decision_dict(action, decisions)
                c_value = gas_network.get_value(decisions, k)
                k += 2

            if c_value == 1:
                wins += 1
            elif c_value == -1:
                losses += 1
            else:
                print("Draw")

        return wins, losses
