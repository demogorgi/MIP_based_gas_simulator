import math
from .configs import CONFIGS

class TreeNode(object):

    def __init__(self, parent = None, action = None, psa = 0.0, child_psas = []):
        self.Nsa = 0
        self.Wsa = 0.0
        self.Qsa = 0.0
        self.Psa = psa
        self.action = action
        self.children = []
        self.child_psas = child_psas
        self.parent = parent

    def is_not_leaf(self):
        if(len(self.children) > 0):
            return True
        return False

    def select_child(self):

        c_puct = CONFIGS.c_puct
        highest_puct = 0
        highest_index = 0

        for index, child in enumerate(self.children):

            puct = child.Qsa + child.Psa * c_puct * (math.sqrt(self.Nsa) / (1 + child.Nsa))

            if puct > highest_puct:
                highest_puct = puct
                highest_index = index
        return self.children[highest_index]
    def expand_node(self, psa_vector):
        pass #TODO

    def add_child_node(self, parent, action, psa = 0.0):

        child_node = TreeNode(parent = parent, action = action, psa = psa)
        self.children.append(child_node)
        return child_node

    def back_propagate(self, wsa, v):
        self.Nsa += 1
        self.Wsa = wsa + v
        self.Qsa = self.Wsa / self.Nsa

class MCTS(object):
    def __init__(self, net):
        self.root = None
        #self.game = None TODO
        self.net = net

    def search(self, game, node, temperature):
        pass #TODO
    def add_dirichlet_noise(self, game, psa_vector):
        pass #TODO
