
import tensorflow as tf

from copy import deepcopy
from .functions_ai import *

mean_value = lambda l,u:((u - l)/2 + l)

cum_n_q = [0 for _ in range(config['decision_freq'])]

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = [0, 0] #Current penalty [Dispatcher penalty, Trader penalty]
    n_penalty = [0, 0] #Penalty expected for new decision
    possible_decisions = []


    def __init__(self):
        self.row = len(self.state)
        self.nom_XN, self.nom_XH, self.nom_EN, self.nom_EH = [abs(v) for k, v in get_trader_nom(self.next_step, self.decisions_dict).items()]
        self.possible_decisions = self.get_valid_actions()

    def get_action_size(self):
        return self.row

    def get_state_dimension(self):
        return (self.row, 1)

    def get_agent_decision(self):
        return deepcopy(self.decisions_dict)

    def get_possible_decisions(self):
        if self.possible_decisions:
            return self.possible_decisions
        else: self.get_valid_actions()

    def set_possible_decisions(self, new_set_decisions):
        self.possible_decisions = new_set_decisions

    #Function to get possible dispatcher decisions
    def get_possible_nexts(self):
        va = 1
        cs_path = False
        re_path = False
        list_actions= []
        rs, gs, cs = get_con_pos()
        if self.nom_EN > self.nom_XN: cs_path = True #Compressor path to be chosen
        else: re_path = True #Resistor path to be chosen
        if not self.next_step%config['decision_freq'] == 0: list_actions.append(get_old_action())
        if cs_path:
            cs = 1
            gas = []
            for i in range(100):
                x = round(random.uniform(args.gas_lb, args.gas_ub), 2)
                if x not in gas:
                    gas.append(x)
            for i in range(len(gas)):
                list_actions.append([va, va, args.zeta_ub, gas[i], cs])
            list_actions.append([va, va, args.zeta_ub, args.gas_lb, 0])

        if re_path:
            cs = 0
            cs_gas = 0
            zeta = []
            for i in range(100):
                x = random.randint(args.zeta_lb, args.zeta_ub)
                if x not in zeta:
                    zeta.append(x)
            for i in range(len(zeta)):
                list_actions.append([va, va, zeta[i], cs_gas, cs])

        return list_actions

    def get_valid_actions(self):

        list_actions = self.get_possible_nexts()
        p_values = []
        list_actions_with_c = []
        for action in list_actions:
            decision = self.generate_decision_dict(action)
            solution = simulator_step(decision, self.next_step, "ai")
            p_values.append(find_penalty(solution)[0])
            #p_values.append(abs(self.get_nom_q_difference(solution)))
        for i in range(len(list_actions)):
            if p_values[i] <= 100: #abs(c_values[i]) <= 100:
                list_actions_with_c.append([list_actions[i], p_values[i]])
        list_actions_with_c.sort(key = lambda list_actions_with_c: abs(list_actions_with_c[1]))

        return list_actions_with_c

    def get_nom_q_difference(self, solution):
        #smoothed_EH, smoothed_EN = [round(v,2) for k,v in get_smoothed_flow(solution).items()] #EH, EN
        flow_EH, flow_EN = [round(v,2) for k,v in get_flow(solution).items()] #EH, EN

        if self.nom_EN > self.nom_XN:
            c = round(self.nom_EN - flow_EN)

        else:
            c = round(self.nom_EH - flow_EH)
        return c

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
        decisions = remove_duplicate_decision(self.get_agent_decision(), decisions, step)

        return decisions

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0
        da_dec = get_dispatcher_dec().copy()

        for k, v in da_dec.items():
            da_dec[k] = da_action[i]
            i += 1
        return da_dec

    def get_cumulative_c(self, action):
        c = 0
        step = self.next_step
        decision = self.generate_decision_dict(action)
        for j in range(config['decision_freq']):
            if step < numSteps:
                solution = simulator_step(decision, step, "ai")
                c += self.get_nom_q_difference(solution)
                step += 1
        self.n_penalty = find_penalty(solution)
        return c


    #Find the reward value for dispatcher agent
    def get_reward(self, penalty = None):
        if not penalty: penalty = self.c_penalty[0]
        #low penalty rewards high value
        if penalty == 0:
            return 1
        elif penalty > 0 or penalty < 10:
            return 0.5
        elif penalty >= 10 and penalty < 50:
            return 0.25
        elif penalty >= 50 and penalty < 100:
            return 0
        else: return -1

    #Find the cumulative c value and its corresponding reward for NN
    def get_value(self, action):
        c = self.get_cumulative_c(action)
        value = abs(c)-200
        if c > 0:
            return -1
        elif c < 0:
            return 1
        else:
            return 0
        # if abs(c) == 200:
        #     return 0
        # else:
        #     value = abs(c)-200
        #     return -value
