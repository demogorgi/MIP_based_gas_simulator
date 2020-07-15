
import tensorflow as tf
import itertools

from copy import deepcopy

from .sol2statepenalty import *
from urmel import *

class Gas_Network(object):

    #Class level variables
    state = None
    decisions_dict = {}
    penalty = [0, 0] #[Dispatcher penalty, Trader penalty]
    exp_penalty = [0,0]
    step = 0
    penalties = []

    def __init__(self):

        self.row = len(self.state)
        self.current_agent = CFG.dispatcher_agent
        self.action_size = self.row
        self.agent_decisions = dispatcher_dec #{**dispatcher_dec, **trader_dec}

    def clone(self):

        network_clone = Gas_Network()
        network_clone.state = deepcopy(self.state)
        network_clone.decisions_dict = deepcopy(self.decisions_dict)
        return network_clone

    #Function to get possible dispatcher decisions
    def dispatcher_decisions(self, old_decisions):
        cs = None
        zeta = None
        gas = None
        da_decisions = {}

        val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))
        rnd_value = lambda: round(random.uniform(0,1), 2)

        for i, k in trader_dec.items():
            if re.search('entry_nom', i):
                res = re.sub('entry_nom\[(\S*)]', r'\1', i)
                if re.search('EN', res) and k > 0:
                    cs = 1
                    gas = rnd_value()
                if re.search('EH', res) and k > 0:
                    cs = 0
                    zeta = rnd_value()*(CFG.zeta_ub-CFG.zeta_lb)+CFG.zeta_lb
                    #zeta = random.randint(100, 1200) #[100,1200]

        for l, v in old_decisions.items():
            if re.match('va', l):
                da_decisions[l] = val(v)
            elif re.match('zeta', l):
                da_decisions[l] = zeta if zeta else v
            elif re.match('gas', l):
                da_decisions[l] = gas if gas is not None else v
            elif re.match('compressor', l):
                da_decisions[l] = cs if cs is not None else v

        valid_dispatcher_decisions = [(k,v) for k, v in da_decisions.items()]

        #Find all possible subsets of possible dispatcher decisions
        list_valid_decisions = []
        for i in range(len(valid_dispatcher_decisions)):
            list_valid_decisions.append(subsets(valid_dispatcher_decisions,i+1))
        valid_decisions = [item for elem in list_valid_decisions for item in elem]

        return valid_decisions

    def generate_decision_dict(self, dispatcher_action): #Generate new agent_decision dictionary
        step = self.step
        decisions = self.decisions_dict
        dispatcher_actions= self.decision_to_dict(dispatcher_action)

        result = lambda key: re.sub('\S*_DA\[(\S*)]', r'\1', key).replace(',', '^')

        for key, value in dispatcher_actions.items():
            if re.search('va', key):
                decisions['va']['VA'][result(key)][step] = value
            elif re.search('zeta', key):
                decisions['zeta']['RE'][result(key)][step] = value
            elif re.search('gas', key):
                decisions['gas']['CS'][result(key)][step] = value
            elif re.search('compressor', key):
                decisions['compressor']['CS'][result(key)][step] = value
        return decisions

    #Get a list of decisions for da2 [va_1,va_2, zeta, gas, compressor]
    def get_decisions(self, agent_decisions):

        possible_decisions = self.dispatcher_decisions(agent_decisions)
        decisions = list(v for k, v in agent_decisions.items())
        rs, gs, cs = get_con_pos()

        list_d = []
        for d in possible_decisions:
            valve = 0
            dec = decisions.copy()
            for i in range(len(d)):
                if re.search('va', d[i][0]):
                    dec[valve] = d[i][1]
                    valve += 1
                if re.search('zeta', d[i][0]):
                    dec[rs] = d[i][1]
                if re.search('gas', d[i][0]):
                    dec[gs] = d[i][1]
                if re.search('compressor', d[i][0]):
                    dec[cs] = d[i][1]
                if dec[cs] == 0: dec[gs] = 0

            if (dec in list_d) or (dec[0] == 0 and dec[1] == 0):
                continue
            list_d.append(dec)
        list_d = self.check_decision(list_d)
        # print(new_list_d)
        # exit()
        return list_d

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0
        da_dec = dispatcher_dec.copy()

        for k, v in da_dec.items():
            da_dec[k] = da_action[i]
            i += 1
        return da_dec

    #Apply the chosen decision
    def take_action(self, da_action):

        self.decisions_dict = self.generate_decision_dict(da_action)

        solution = simulator_step(self.decisions_dict, self.step, "ai")

        self.state = extract_from_solution(solution)
        self.exp_penalty = find_penalty(solution)

    def take_old_action(self):
        solution = simulator_step(Gas_Network.decisions_dict, self.step, "ai")
        old_dec_penalty = find_penalty(solution)
        dec_value = self.get_reward(old_dec_penalty)

        return dec_value, old_dec_penalty[0]

    #Find the reward value for dispatcher agent
    def get_reward(self, penalty):

        #low penalty rewards high value
        if penalty[0] == 0 or penalty[0] < 10:
            return 10
        elif penalty[0] > 10 and penalty[0] < 50:
            return 5
        elif penalty[0] > 50 and penalty[0] < 100:
            return -5
        else: return -10


    def check_decision(self, list_actions):
        modified_list_actions = list_actions
        for i, action in enumerate(list_actions):

            decision = self.generate_decision_dict(action)
            solution = simulator_step(decision, self.step, "ai")

            penalty = find_penalty(solution)

            value = self.get_reward(penalty)

            if value < 0:
                del modified_list_actions[i]

        return modified_list_actions
