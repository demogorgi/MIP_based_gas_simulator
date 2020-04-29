
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

    def __init__(self, state, decisions_dict):

        self.cols = 1 #2 #Pressure and flow of nodes
        self.row = len(state)
        self.current_agent = CFG.dispatcher
        self.action_size = self.row * self.cols
        self.state = state
        self.decisions_dict = decisions_dict
        self.agent_decisions = dispatcher_dec #{**dispatcher_dec, **trader_dec}

    def clone(self):

        state = self.state
        decisions_dict = self.decisions_dict
        network_clone = Gas_Network(state, decisions_dict)
        network_clone.state = deepcopy(self.state)
        #network_clone.current_agent = self.current_agent
        return network_clone


    #Function to get possible dispatcher decisions
    def dispatcher_decisions(self, old_decisions):
        valid_dispatcher_decisions = []

        val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))

        for l, v in old_decisions.items():
            if re.match('va', l):
                valid_dispatcher_decisions.append((l, val(v)))
            elif re.match('compressor', l):
                valid_dispatcher_decisions.append((l, val(v)))
            elif re.match('zeta', l):
                zeta = random.randrange(0, 10000) # [0, INFINITY)
                valid_dispatcher_decisions.append((l, zeta))
            elif re.match('gas', l):
                gas = round(random.uniform(0.0, 1.0), 2)
                valid_dispatcher_decisions.append((l, gas))
        #Find all possible subsets of possible dispatcher decisions
        list_valid_decisions = []
        for i in range(len(valid_dispatcher_decisions)):
            list_valid_decisions.append(subsets(valid_dispatcher_decisions,i+1))

        valid_decisions = [item for elem in list_valid_decisions for item in elem]

        return valid_decisions

    def generate_decision(self, actions): #Generate new agent_decision dictionary

        decisions_dict = self.decisions_dict

        result = lambda key: re.sub('\S*_DA\[(\S*)]', r'\1', action[1]).replace(',', '^')

        for idx, action in enumerate(actions):

            key = action[1]
            value = action[2]
            if re.search('va', key):
                decisions_dict['va']['VA'][result(key)] = value
            elif re.search('zeta', key):
                decisions_dict['zeta']['RE'][result(key)] = value
            elif re.search('gas', key):
                decisions_dict['gas']['CS'][result(key)] = value
            elif re.search('compressor', key):
                decisions_dict['compressor']['CS'][result(key)] = value
        return decisions_dict

    def get_decisions(self, agent_decisions):

        possible_decisions = self.dispatcher_decisions(agent_decisions)
        #print(possible_decisions)
        decisions = list(v for k, v in dispatcher_dec.items())
        #print(decisions)
        list_d = []
        for d in possible_decisions:
            dec = decisions.copy()
            for i in range(len(d)):

                #print(dec)
                if re.search('va', d[i][0]):
                    dec[0] = d[i][1]
                if re.search('zeta', d[i][0]):
                    dec[1] = d[i][1]
                if re.search('gas', d[i][0]):
                    dec[2] = d[i][1]
                if re.search('compressor', d[i][0]):
                    dec[3] = d[i][1]
                    #print(dec)

            list_d.append(dec)
        return list_d
