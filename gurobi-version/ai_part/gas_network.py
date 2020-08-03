
import tensorflow as tf
import itertools

from copy import deepcopy
from .functions_ai import *

mean_value = lambda l, u: (l+u)/2

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = [0, 0] #Current penalty [Dispatcher penalty, Trader penalty]
    n_penalty = [0, 0] #Penalty expected for new decision
    possible_decisions = []
    cum_sum_penalty = 0
    sol = None

    def __init__(self):
        self.row = len(self.state)
        self.tol_penalty = 20 #Assume allowed penalty
        self.nom_XN, self.nom_XH, self.nom_EN, self.nom_EH = [abs(v) for k, v in get_trader_nom(self.next_step, self.decisions_dict).items()]


    def get_action_size(self):
        return self.row

    def get_state_dimension(self):
        return (self.row, 1)

    def get_agent_decision(self):
        return deepcopy(self.decisions_dict)

    def get_possible_decisions(self):
        return self.get_possible_nexts(get_dispatcher_dec())


    #Function to get possible dispatcher decisions
    def get_possible_nexts(self, old_decisions):
        zeta = None
        gas = None
        cs = None

        da_decisions = {}
        #val = lambda b: int(1-b)
        subsets = lambda s,n: list(itertools.combinations(s,n))

        if  self.next_step%config['nomination_freq'] == 0:
            if self.nom_EN > self.nom_XN:
                cs = 1
                gas = round(mean_value(args.gas_lb,args.gas_ub),3)
                zeta = args.zeta_ub
            else:
                cs = 0
                gas = 0
                zeta = int(mean_value(args.zeta_lb, args.zeta_ub))

        for l, v in old_decisions.items():
            if re.match('va', l):
                da_decisions[l] = 1
            elif re.match('zeta', l):
                da_decisions[l] = zeta if zeta else v
            elif re.match('gas', l):
                da_decisions[l] = gas if gas is not None  else v
            elif re.match('compressor', l):
                da_decisions[l] = cs if cs is not None else v

        valid_decisions = [v for k,v in da_decisions.items()]

        return valid_decisions

    def get_nom_q_difference(self):
        smoothed_EH, smoothed_EN = [round(v,2) for k,v in get_smoothed_flow().items()] #EH, EN

        if self.nom_EN > self.nom_XN:
            c = round(self.nom_EN - smoothed_EN)
        else:
            c = round(self.nom_EH - smoothed_EH)
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

    #Get a list of decisions for da2 [va_1,va_2, zeta, gas, compressor]
    def get_decisions(self, old_decisions):

        possible_decisions = self.get_possible_nexts(old_decisions)
        old_action = get_old_action()
        rs, gs, cs = get_con_pos()
        list_d = []
        for d in possible_decisions:
            valve = 0
            dec = old_action.copy()
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
            if (dec in list_d) or dec == old_action:
                continue
            list_d.append(dec)
        if not list_d:
            list_d.append(old_action)

        return list_d

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0
        da_dec = get_dispatcher_dec().copy()

        for k, v in da_dec.items():
            da_dec[k] = da_action[i]
            i += 1
        return da_dec

    #Functions to apply the chosen decision
    def take_action(self, da_action, step = 0):
        if not step:
            step = self.next_step

        decision = self.generate_decision_dict(da_action)

        solution = simulator_step(decision, step, "ai")

        state = get_state(step, decision, solution)
        self.n_penalty = find_penalty(solution)

    def apply_action(self, action):

        rs, gs, cs = get_con_pos()
        c = 0
        cum_penalty = 0
        d = self.generate_decision_dict(action)
        step = self.next_step
        for i in range(config['penalty_freq']):
            if step < numSteps:
                self.take_action(action, step)
                c += self.get_nom_q_difference()

                cum_penalty += self.n_penalty[0]
                step += 1

        if c > 0:
            if self.nom_EN > self.nom_XN:
                action[gs] = round(mean_value(action[gs], args.gas_ub),3)
            else:
                action[rs] = int(mean_value(args.zeta_lb, action[rs]))

        else:
            if c < 0:
                if self.nom_EN > self.nom_XN:
                    action[gs] = round(mean_value(args.gas_lb, action[gs]),3)
                else:
                    action[rs] = int(mean_value(action[rs], args.zeta_ub))

        set_dispatcher_dec(self.decision_to_dict(action))
        self.cum_sum_penalty = cum_penalty


    #Find the reward value for dispatcher agent
    def get_reward(self, penalty):

        #low penalty rewards high value
        if penalty == 0 or penalty < 10 :
            return 10
        elif penalty >= 10 and penalty < 50:
            return 5
        elif penalty >= 50 and penalty < 100:
            return -5
        else: return -10
