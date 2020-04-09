import math
from .configs import CONFIGS

class TreeNode(object):

    def __init__(self, parent, psa):
        self.parent = parent

        self.states = {}
        self.children = {}

        self.Nsa = 0
        self.Wsa = 0.0
        self.Qsa = 0.0
        self.Psa = psa


    def is_not_leaf(self):
        if(len(self.children) > 0):
            return True
        return False

    def select_child(self):

        c_puct = CONFIGS.c_puct
        highest_puct = 0
        highest_index = 0

        for index, child in enumerate(self.children):

            puct = child.Qsa + c_puct * child.Psa  * (math.sqrt(self.Nsa) / (1 + child.Nsa))

            if puct > highest_puct:
                highest_puct = puct
                highest_index = index
        return self.children[highest_index]
    def expand_node(self, move_history):

        for move, psa in move_history:
            if move not in self.children:
                self.children[move] = TreeNode(self, psa)

    def add_child_node(self, parent, action, psa = 0.0):

        child_node = TreeNode(parent = parent, psa = psa)
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
        self.net = net

    def search(self, game, node, temperature):
        pass #TODO
    def add_dirichlet_noise(self, game, psa_vector):
        pass #TODO
