
import tensorflow as tf
import itertools

from copy import deepcopy

from .functions_ai import *
#from urmel import *

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = [0, 0] #Current penalty [Dispatcher penalty, Trader penalty]
    n_penalty = [0, 0] #Penalty expected for new decision
    possible_decisions = []

    def __init__(self):
        self.row = len(self.state)
        self.possible_decisions = self.get_decisions(get_dispatcher_dec())

    def get_action_size(self):
        return self.row

    def get_state_dimension(self):
        return (self.row, 1)

    def get_agent_decision(self):
        return deepcopy(self.decisions_dict)

    def get_possible_decisions(self):
        if self.possible_decisions:
            return self.possible_decisions
        return self.get_decisions(get_dispatcher_dec())

    #Function to get possible dispatcher decisions
    def get_possible_nexts(self, old_decisions):
        cs = None
        zeta = None
        gas = None
        va_1 = 0
        va_2 = 0
        da_decisions = {}

        val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))
        rndm_value = lambda l,u: round(random.uniform(l,u), 2)
        zeta_value = lambda l,u: round(rndm_value(l, u)*(args.zeta_ub-args.zeta_lb)+args.zeta_lb, 2)

        trader_nom = get_trader_nom(self.next_step, self.decisions_dict)

        for i, k in trader_nom.items():
            if re.search('entry_nom', i):
                res = re.sub('entry_nom_TA\[(\S*)]', r'\1', i)
                if re.search('EN', res) and k > 0:
                    va_1 += 1
                    if k > 500:
                        cs = 1
                        gas = rndm_value(0.4,1)
                    else:
                        gas = rndm_value(0, 0.4)

                if re.search('EH', res) and k > 0:
                    va_2 += 1
                    if k > 500:
                        cs = 0
                        zeta = zeta_value(0, 0.2)
                        #zeta = random.randint(100, 1200) #[100,1200]
                    else:
                        zeta = zeta_value(0.5, 1)

        for l, v in old_decisions.items():
            if re.match('va', l):
                va_name = re.sub('va_DA\[(\S*)]', r'\1', l)
                if va_name == 'N18^N23_1':
                    da_decisions[l] = va_1 if va_1 == 1 else val(v)
                else:
                    da_decisions[l] = va_2 if va_2 == 1 else val(v)
            elif re.match('zeta', l):
                da_decisions[l] = zeta if zeta else v
            elif re.match('gas', l):
                da_decisions[l] = gas if gas is not None else v
            elif re.match('compressor', l):
                da_decisions[l] = cs if cs is not None else v

        valid_dispatcher_decisions = [(k,v) for k, v in da_decisions.items()]

        #Find all possible subsets of possible dispatcher decisions
        list_valid_decisions = []
        for i in range(len(valid_dispatcher_decisions), 0,-1):
            list_valid_decisions.append(subsets(valid_dispatcher_decisions,i))
        valid_decisions = [item for elem in list_valid_decisions for item in elem]

        return valid_decisions

    def generate_decision_dict(self, dispatcher_action): #Generate new agent_decision dictionary
        step = self.next_step
        decisions = self.get_agent_decision()
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
        print(step)
        decisions = remove_duplicate_decision(self.get_agent_decision(), decisions, step)

        return decisions

    #Get a list of decisions for da2 [va_1,va_2, zeta, gas, compressor]
    def get_decisions(self, agent_decisions):

        possible_decisions = self.get_possible_nexts(agent_decisions)
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

            if (dec in list_d) or dec == decisions:
                continue
            list_d.append(dec)
        # list_d = self.check_decision(list_d)

        return list_d

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0
        da_dec = get_dispatcher_dec().copy()

        for k, v in da_dec.items():
            da_dec[k] = da_action[i]
            i += 1
        return da_dec

    #Apply the chosen decision
    def take_action(self, da_action):

        decision = self.generate_decision_dict(da_action)

        solution = simulator_step(decision, self.next_step, "ai")

        #self.state = get_state(self.next_step, decision)
        self.n_penalty = find_penalty(solution)

    def take_old_action(self, step=0):
        if not step:
            step = self.next_step

        solution = simulator_step(Gas_Network.decisions_dict, step, "ai")
        old_dec_penalty = find_penalty(solution)
        #dec_value = self.get_reward(old_dec_penalty)

        return old_dec_penalty[0]

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
            solution = simulator_step(decision, self.next_step, "ai")

            penalty = find_penalty(solution)

            value = self.get_reward(penalty)

            if value < 0:
                del modified_list_actions[i]

        return modified_list_actions

    def get_valid_decisions(self):
        possible_decisions = self.get_possible_decisions()
        print(possible_decisions)
        rs, gs, cs = get_con_pos()
        trader_nom = get_trader_nom(self.next_step, self.decisions_dict)
        valid_decisions = possible_decisions
        for k, v in trader_nom.items():
            if v > entry_q_ub/2:
                if 'EN' in k:
                    valid_decisions = [valid for key, valid in enumerate(possible_decisions) if not valid[cs] == 0]
                if 'EH' in k:
                    valid_decisions = [valid for key, valid in enumerate(possible_decisions) if valid[cs] == 0]
        print(len(valid_decisions))
        return valid_decisions
