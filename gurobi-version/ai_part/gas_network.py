
import sys

import tensorflow as tf
import numpy as np
import re
import random
import itertools

from copy import deepcopy

from .configs import *
from .sol2state import *
from urmel import *

class Gas_Network(object):

    def __init__(self, state, agent_decisions):

        self.cols = 2 #Pressure and flow of nodes
        self.row = len(state)
        self.current_agent = CFG.dispatcher
        self.action_size = self.row * self.cols
        self.state = state
        self.agent_decisions = agent_decisions


    def clone(self):

        state = self.state
        agent_decisions = self.agent_decisions
        network_clone = Gas_Network(state, agent_decisions)
        network_clone.state = deepcopy(self.state)
        #network_clone.current_agent = self.current_agent
        return network_clone


    #Function to get possible dispatcher decisions
    def get_dispatcher_decisions(self, old_decisions):
        valid_dispatcher_decisions = []

        val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))

        for l, v in old_decisions.items():
            if re.match('va', l):
                valid_dispatcher_decisions.append((1, l, val(v)))
            elif re.match('compressor', l):
                valid_dispatcher_decisions.append((1, l, val(v)))
            elif re.match('zeta', l):
                zeta = random.randrange(0, 10000) # [0, INFINITY)
                valid_dispatcher_decisions.append((1, l, zeta))
            elif re.match('gas', l):
                gas = round(random.uniform(0.0, 1.0), 2)
                valid_dispatcher_decisions.append((1, l, gas))
        #Find all possible subsets of possible dispatcher decisions
        list_valid_decisions = []
        for i in range(len(valid_dispatcher_decisions)):
            list_valid_decisions.append(subsets(valid_dispatcher_decisions,i))

        valid_decisions = [item for elem in list_valid_decisions for item in elem]

        return random.choice(valid_decisions)

    def generate_decision(self, actions): #Generate new agent_decision dictionary
        decisions_dict = self.agent_decisions

        result = lambda key: re.sub('\S*_DA\[(\S*)]', r'\1', action[1]).replace(',', '^')

        for action in actions:
            key = action[1]
            vaconfig, compressors, dtlue = action[2]
            if re.search('va', key):
                decisions_dict['va']['VA'][result(key)] = value
            elif re.search('zeta', key):
                decisions_dict['zeta']['RE'][result(key)] = value
            elif re.search('gas', key):
                decisions_dict['gas']['CS'][result(key)] = value
            elif re.search('compressor', key):
                decisions_dict['compressor']['CS'][result(key)] = value
        return decisions_dict
