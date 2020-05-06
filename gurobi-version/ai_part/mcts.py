import math
from .configs import CFG

import numpy as np
from copy import deepcopy
import random

from .sol2state import *

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

        c_puct = CFG.c_puct
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

    def search(self, gas_network, node, temperature):
        self.root = node
        self.gas_network = gas_network

        for i in range(CFG.num_mcts_sims):
            node = self.root
            gas_network = self.gas_network.clone()

            while node.is_not_leaf():
                node = node.select_child()
                gas_network.take_action(node.action)

            prob_vector, v = self.net.predict(gas_network.state)

            if node.parent is None:
                prob_vector = self.add_dirichlet_noise(gas_network, prob_vector)

            possible_decisions = gas_network.get_decisions(gas_network.agent_decisions)

            psa_vector = self.possible_decision_probabilty(gas_network, possible_decisions, prob_vector)

            psa_vector_sum = sum(psa_vector)

            if psa_vector_sum > 0:
                psa_vector /= psa_vector_sum

            node.expand_node(gas_network = gas_network, psa_vector = psa_vector)

            iteration_over, wsa = gas_network.get_reward()

            while node is not None:
                wsa = -wsa
                v = -v
                node.back_propagate(wsa, v)
                node = node.parent

        highest_nsa = 0
        highest_index = 0

        for idx, child in enumerate(self.root.children):
            temperature_exp = int(1 / temperature)

            if child.Nsa ** temperature_exp > highest_nsa:
                highest_nsa = child.Nsa ** temperature_exp
                highest_index = idx
        return self.root.children[highest_index]

    def add_dirichlet_noise(self, gas_network, psa_vector):

        dirichlet_input = [CFG.dirichlet_alpha for x in range(gas_network.action_size)]

        dirichlet_list = np.random.dirichlet(dirichlet_input)

        noisy_psa_vector = []

        for idx, psa in enumerate(psa_vector):
            noisy_psa_vector.append(
                (1 - CFG.epsilon) * psa + CFG.epsilon * dirichlet_list[idx])

        return noisy_psa_vector
    def possible_decision_probabilty(self, gas_network, possible_decisions, prob_vector):

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

        if len(psa_vector) != gas_network.action_size:
            if len(psa_vector) < gas_network.action_size:
                d = gas_network.action_size - len(psa_vector)
                psa_vector = (psa_vector + [0] * d)
            else:
                psa_vector = random.sample(psa_vector, gas_network.action_size)

        return psa_vector
