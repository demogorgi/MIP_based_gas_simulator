
import tensorflow as tf
import itertools

from copy import deepcopy

from .sol2state import *
from urmel import *

class Gas_Network(object):

    #Class level variables
    state = None
    decisions_dict = {}
    config = None
    compressors = None
    dt = 0
    penalty = [0, 0] #[Dispatcher penalty, Trader penalty]

    def __init__(self):

        self.cols = 1 #Decision values + pressures ,2 #Pressure and flow of nodes
        self.row = len(self.state)
        self.current_agent = CFG.dispatcher_agent
        self.action_size = self.row * self.cols
        self.agent_decisions = dispatcher_dec #{**dispatcher_dec, **trader_dec}
        #self.trader_dec = trader_dec


    def clone(self):

        network_clone = Gas_Network()
        network_clone.state = deepcopy(self.state)
        network_clone.decisions_dict = deepcopy(self.decisions_dict)
        return network_clone

    #Function to get possible dispatcher decisions
    def dispatcher_decisions(self, old_decisions):

        da_decisions = {}
        #valid_da_decisions = []

        val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))

        for l, v in old_decisions.items():
            if re.match('va', l):
                #va = val(v)
                da_decisions[l] = val(v)
            elif re.match('zeta', l):
                zeta = random.randint(0, CFG.zeta_upper) #[0, 10000]
                #zeta = random.randrange(0, 10000) #[0, INFINITY)
                #zeta = v
                da_decisions[l] = zeta
            elif re.match('gas', l):
                gas = round(random.uniform(0.0, 1.0), 2)
                da_decisions[l] = gas
            elif re.match('compressor', l):
                da_decisions[l] = val(v)

        for k, v in da_decisions.items():
            if re.search('compressor', k): #re.sub() TODO
                if v == 0:
                    da_decisions['gas_DA[N22,N23]'] = 0
        valid_dispatcher_decisions = [(k,v) for k, v in da_decisions.items()]

        #Find all possible subsets of possible dispatcher decisions
        list_valid_decisions = []
        for i in range(len(valid_dispatcher_decisions)):
            list_valid_decisions.append(subsets(valid_dispatcher_decisions,i+1))

        valid_decisions = [item for elem in list_valid_decisions for item in elem]

        return valid_decisions

    def generate_decision_dict(self, dispatcher_actions): #Generate new agent_decision dictionary

        decisions = self.decisions_dict
        dispatcher_actions= self.decision_to_dict(dispatcher_actions)

        result = lambda key: re.sub('\S*_DA\[(\S*)]', r'\1', key).replace(',', '^')
        for key, value in dispatcher_actions.items():

            if re.search('va', key):
                decisions['va']['VA'][result(key)] = value
            elif re.search('zeta', key):
                decisions['zeta']['RE'][result(key)] = value
            elif re.search('gas', key):
                decisions['gas']['CS'][result(key)] = value
            elif re.search('compressor', key):
                decisions['compressor']['CS'][result(key)] = value

        return decisions

    #Get a list of decisions [va, zeta, gas, compressor]
    def get_decisions(self, agent_decisions):

        possible_decisions = self.dispatcher_decisions(agent_decisions)
        #print(possible_decisions)
        decisions = list(v for k, v in dispatcher_dec.items())
        #print(decisions)
        list_d = []
        for d in possible_decisions:
            dec = decisions.copy()
            for i in range(len(d)):
                if re.search('va', d[i][0]):
                    dec[0] = d[i][1]
                if re.search('zeta', d[i][0]):
                    dec[1] = d[i][1]
                if re.search('gas', d[i][0]):
                    dec[2] = d[i][1]
                if re.search('compressor', d[i][0]):
                    dec[3] = d[i][1]
                if dec[3] == 0: dec[2] = 0
            list_d.append(dec)
        return list_d

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0

        for k, v in dispatcher_dec.items():
            dispatcher_dec[k] = da_action[i]
            i += 1
            return dispatcher_dec


    def take_action(self, da_action):

        Gas_Network.decisions_dict = self.generate_decision_dict(da_action)
        solution = simulator_step(self.config, self.decisions_dict, self.compressors, 0, self.dt)
        if solution:
            self.state = extract_from_solution(solution)
            Gas_Network.penalty = find_penalty(solution)


    def get_reward(self):

        penalty = self.penalty
        #print(penalty)

        if penalty[0] < penalty[1]: #Dispatcher won
            return True, 1
        elif penalty[0] > penalty[1]: #Trader won
            return True, -1
        elif penalty[0] == 0 and penalty[1] == 0:
            return True, 1
        else:
            return True, 0 #Draw
        #return False, 0
