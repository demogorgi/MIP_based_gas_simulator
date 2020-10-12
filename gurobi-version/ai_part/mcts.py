import math
from copy import deepcopy

from .functions_ai import *
from .configs import *

class TreeNode(object):
    #Class represents a state (of network) and stores statistics for action(decision) at the state
    #Attributes:
        #Nsa: visit count
        #Qsa: action value
        #Psa: prior probability

        #action: decision on the state

        #children: list of child nodes
        #child_psas: vector containing child probabilities
        #parent: node represents the node's parent

    def __init__(self, parent = None, action = None, psa = 0.0, child_psas = []):
        self.Nsa = 0
        self.Wsa = 0.0
        self.Qsa = 0.0
        self.Psa = psa

        self.children = []
        self.action = action
        self.child_psas = child_psas

        self.parent = parent


    def is_not_leaf(self):

        if(len(self.children) > 0):
            return True

        return False

    def select_child(self):

        c_puct = configs.c_puct
        highest_puct = 0
        highest_index = 0

        for index, child in enumerate(self.children):

            puct = child.Qsa + c_puct * child.Psa  * (math.sqrt(self.Nsa) / (1 + child.Nsa))

            if puct > highest_puct:
                highest_puct = puct
                highest_index = index
        return self.children[highest_index]
    def expand_node(self, gas_network, psa_vector):
        #Expanding current node by adding valid moves as children
        self.child_psas = deepcopy(psa_vector)
        valid_decisions = gas_network.get_possible_decisions()

        for idx, move in enumerate(valid_decisions):
            if move[0] is not [0]:
                action = deepcopy(move[0])
                self.add_child_node(parent = self, action = action, psa = psa_vector[idx])

    def add_child_node(self, parent, action, psa = 0.0):
        child_node = TreeNode(parent = parent, action = action, psa = psa)
        self.children.append(child_node)
        return child_node

    def back_propagate(self, wsa, v):
        self.Nsa += 1
        self.Wsa = wsa + v
        self.Qsa = self.Wsa / self.Nsa

class MCTS(object):
    #MCTS algorithm
    def __init__(self, net):
        self.root = None
        self.gas_network = None
        self.net = net

    def search(self, gas_network, node, temperature):
        self.root = node
        self.gas_network = gas_network

        for i in range(configs.num_mcts_sims):
            node = self.root
            gas_network = deepcopy(self.gas_network)

            # while node.is_not_leaf():
            #     print("Not a leaf")
            #     node = node.select_child()
            #     gas_network.apply_action(node.action)

            prob_vector, v = self.net.policy_value(gas_network.current_state)

            if node.parent is None:
                prob_vector = self.add_dirichlet_noise(prob_vector)

            possible_decisions = gas_network.get_possible_decisions()

            psa_vector = self.possible_decision_probability(gas_network, possible_decisions, prob_vector)

            psa_vector_sum = sum(psa_vector)

            if psa_vector_sum > 0: #Renormalize the psa_vector
                psa_vector /= psa_vector_sum
            node.expand_node(gas_network = gas_network, psa_vector = psa_vector)

            wsa = gas_network.get_reward()

            while node is not None:
                node.back_propagate(wsa, v)
                node = node.parent

        return self.root.select_child()

    def add_dirichlet_noise(self, psa_vector):

        dirichlet_input = [configs.dirichlet_alpha for x in range(self.gas_network.get_action_size())]
        dirichlet_list = np.random.dirichlet(dirichlet_input)

        noisy_psa_vector = []

        for idx, psa in enumerate(psa_vector):
            noisy_psa_vector.append(
                (1 - configs.epsilon) * psa + configs.epsilon * dirichlet_list[idx])

        return noisy_psa_vector

    def possible_decision_probability(self, gas_network, possible_decisions, prob_vector):
        psa_vector = []
        for i, decision in enumerate(possible_decisions):
            value = gas_network.get_reward(decision[1])
            psa_vector.append(value*prob_vector[i])

        return psa_vector
