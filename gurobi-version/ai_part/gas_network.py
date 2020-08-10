
import tensorflow as tf
import itertools

from copy import deepcopy
from .functions_ai import *

mean_value = lambda l,u:((u - l)/2 + l)
gs_ub = 0
gs_lb = 0

rs_ub = 0
rs_lb = 0
cum_n_q = [0 for _ in range(16)]

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = [0, 0] #Current penalty [Dispatcher penalty, Trader penalty]
    n_penalty = [0, 0] #Penalty expected for new decision
    possible_decisions = []


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
        va = 1

        if self.next_step%config['nomination_freq'] == 0:
            if self.nom_EN > self.nom_XN:
                cs = 1
                gas = round(mean_value(args.gas_lb,args.gas_ub),3)
                zeta = args.zeta_ub
            elif self.nom_EN == self.nom_XN:
                cs = 0
                gas = 0
                zeta = args.zeta_ub
            else:
                cs = 0
                gas = 0
                zeta = mean_value(args.zeta_lb, args.zeta_ub)
        else:

            for l, v in old_decisions.items():
                if re.match('va', l):
                    va = v
                elif re.match('zeta', l):
                    zeta = v
                elif re.match('gas', l):
                    gas = v
                elif re.match('compressor', l):
                    cs = v

        valid_decisions = [va, va, zeta, gas, cs]

        return valid_decisions

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


    def apply_action(self, action):
        #actions = []
        global gs_ub, gs_lb, rs_ub, rs_lb, cum_n_q

        if self.next_step % config['nomination_freq'] == 0:
            gs_ub = args.gas_ub
            gs_lb = args.gas_lb

            rs_ub = args.zeta_ub
            rs_lb = args.zeta_lb

        rs, gs, cs = get_con_pos()

        for i in range(19):
            c = 0
            step = self.next_step
            decision = self.generate_decision_dict(action)
            for j in range(config['penalty_freq']):
                if step < numSteps:
                    solution = simulator_step(decision, step, "ai")
                    #penalty = find_penalty(solution)
                    c += self.get_nom_q_difference(solution)
                    cum_n_q[j] = c
                    step += 1

            #actions.append([action.copy(), c])
            if i == config['decision_freq']: break
            if c > 0:

                if self.nom_EN > self.nom_XN:
                    gs_lb = action[gs]
                    action[gs] = round(mean_value(gs_lb, gs_ub),3)
                else:
                    rs_ub = action[rs]
                    action[rs] = round(mean_value(rs_lb, rs_ub),2)
            else:
                if c < 0:
                    if self.nom_EN > self.nom_XN:
                        gs_ub = action[gs]
                        action[gs] = round(mean_value(gs_lb, gs_ub),3)
                    else:
                        rs_lb = action[rs]
                        action[rs] = round(mean_value(rs_lb, rs_ub),2)

        if action[gs] < 0.05 and self.nom_EN > self.nom_XN:

            action_ = action.copy()
            action_[cs] = 0
            action_[gs] = 0
            decision = self.generate_decision_dict(action_)
            solution = simulator_step(decision, self.next_step, "ai")
            c = self.get_nom_q_difference(solution)

            if abs(c) < abs(cum_n_q[0]):
                action = action_

        set_dispatcher_dec(self.decision_to_dict(action))

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
