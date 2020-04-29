import math
from .configs import CFG

import numpy as np
from copy import deepcopy

from .sol2state import *

class TreeNode(object):

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

        c_puct = CFG.c_puct
        h.action_size = sighest_puct = 0
        highest_index = 0

        for index, child in enumerate(self.children):

            puct = child.Qsa + c_puct * child.Psa  * (math.sqrt(self.Nsa) / (1 + child.Nsa))

            if puct > highest_puct:
                highest_puct = puct
                highest_index = index
        return self.children[highest_index]
    def expand_node(self, gas_network, psa_vector):
        #Expanding current node by adding valid decisions as children
        self.child_psas = deepcopy(psa_vector)
        valid_decisions = gas_network.get_decisions(gas_network.agent_decisions)

        for idx, move in enumerate(valid_decisions):
            action = deepcopy(move)
            self.add_child_node(parent = self, action = action, psa = psa_vector[idx])


    def add_child_node(self, parent, action, psa = 0.0):
        child_node = TreeNode(parent = parent, psa = psa, action = action)
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

    def search(self, gas_network, node, temperature, config, compressors, dt):
        self.root = node
        self.gas_network = gas_network

        for i in range(CFG.num_mcts_sims):
            node = self.root
            gas_network = self.gas_network.clone()

            # while node.is_not_leaf():#TODO change
            #
            #     

            possible_decisions = gas_network.get_decisions(gas_network.agent_decisions)

            for i in range(len(possible_decisions[-1])):
                gas_network.state[i] = possible_decisions[-1][i]

            prob_vector, v = self.net.predict(gas_network.state)


            if node.parent is None:
                prob_vector = self.add_dirichlet_noise(gas_network, prob_vector)

            psa_vector = self.possible_decision_probabilty(possible_decisions, prob_vector)

            psa_vector_sum = sum(psa_vector)

            if psa_vector_sum > 0:
                psa_vector /= psa_vector_sum

            node.expand_node(gas_network = gas_network, psa_vector = psa_vector)


    def add_dirichlet_noise(self, gas_network, psa_vector):

        dirichlet_input = [CFG.dirichlet_alpha for x in range(gas_network.action_size)]

        dirichlet_list = np.random.dirichlet(dirichlet_input)

        noisy_psa_vector = []

        for idx, psa in enumerate(psa_vector):
            noisy_psa_vector.append(
                (1 - CFG.epsilon) * psa + CFG.epsilon * dirichlet_list[idx])

        return noisy_psa_vector
    def possible_decision_probabilty(self, possible_decisions, prob_vector):

        old_DA = list(v for k, v in dispatcher_dec.items())
        indices = []
        for idx, decision in enumerate(possible_decisions):
            x = []
            for i in range(len(decision)):
                if old_DA[i] != decision[i]:
                    x.append(i)
            indices.append(x)
        psa_vector = []
        for index in indices:
            probability = 0
            for i in range(len(index)):
                probability += prob_vector[index[i]]
            psa_vector.append(probability)

        return psa_vector
