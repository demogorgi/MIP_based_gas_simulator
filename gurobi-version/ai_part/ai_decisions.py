from .mcts import *
from .utils import *

class AI_Decisions(object):

    def __init__(self, gas_network, net):
        self.gas_network = gas_network
        self.net = net

    def get_decision(self):
        mcts = MCTS(self.net)
        gas_network = deepcopy(self.gas_network)
        node = TreeNode()

        best_child = mcts.search(gas_network, node, configs.temperature)
        action = best_child.action
        gas_network.apply_action(action)
        new_action_c_p = gas_network.cum_sum_penalty

        old_action = get_old_action()
        gas_network.apply_action(old_action)
        old_action_c_p = gas_network.cum_sum_penalty

        if new_action_c_p < old_action_c_p:
            decision = gas_network.generate_decision_dict(action)
            return decision
