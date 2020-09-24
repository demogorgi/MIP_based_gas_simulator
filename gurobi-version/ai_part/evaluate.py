from .mcts import *
from .configs import *
from params import *
from .functions_ai import *

class Evaluate(object):
    #Class to evaluate the trained model

    def __init__(self, current_mcts, eval_mcts, gas_network):
        self.nnet = current_mcts
        self.eval_net = eval_mcts
        self.gas_network = gas_network

    def evaluate(self):
        wins_da1 = 0
        wins_da2 = 0

        for i in range(configs.nums_eval_plays):

            node = TreeNode()
            gas_network = deepcopy(self.gas_network)
            c_value_da2 = 0
            a = random.randrange(0, 1100, 50)

            gas_network.set_nominations(a)
            gas_network.possible_decisions = gas_network.get_valid_actions()

            for player in range(configs.num_players):
                k = 0
                decisions = deepcopy(gas_network.decisions_dict)
                if player == 0:
                    mcts = self.eval_net
                else:
                    c_value_da2 = c_value
                    mcts = self.nnet

                while(k+2 <= config['number_of_decisions']):
                    best_child = mcts.search(gas_network, node, configs.temperature)
                    action = best_child.action
                    decisions = gas_network.generate_decision_dict(action, decisions)
                    c_value = gas_network.get_value(decisions, k)
                    k += 2

            if c_value == 1:
                wins_da1 += 1
            if c_value_da2 == 1:
                wins_da2 += 1
        print("evaluation finished")
        return wins_da1, wins_da2
