from copy import deepcopy
from .functions_ai import *

mean_value = lambda l,u:((u - l)/2 + l)

cum_n_q = [0 for _ in range(config['decision_freq'])]
accumulated_cs = {}

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = 0 #Current accumulated c value from solution
    possible_decisions = []
    ex_nom_EH = 0
    ex_nom_EN = 0
    ex_dec_pool = []


    def __init__(self):
        self.row = len(self.state)
        self.nom_XN, self.nom_XH, self.nom_EN, self.nom_EH = [abs(v) for k, v in get_trader_nom(self.next_step, deepcopy(self.decisions_dict)).items()]
        self.possible_decisions = self.get_valid_actions()
        self.save_nominations(self.nom_EH, self.nom_EN, deepcopy(self.possible_decisions))

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

    def save_nominations(self, old_EH, old_EN, old_decision_pool):
        self.ex_nom_EH = old_EH
        self.ex_nom_EN = old_EN
        self.ex_dec_pool = old_decision_pool

    def get_saved_nominations(self):
        return self.ex_nom_EH, self.ex_nom_EN, self.ex_dec_pool

    def set_nominations(self, new_EN):
        decisions = deepcopy(self.get_agent_decision())
        step = self.next_step
        self.nom_EH = 1100-new_EN
        self.nom_EN = new_EN
        decisions["entry_nom"]["S"]["EN_aux0^EN"][step] = self.nom_EN
        decisions["entry_nom"]["S"]["EH_aux0^EH"][step] = self.nom_EH
        self.decisions_dict = remove_duplicate_decision(deepcopy(self.get_agent_decision()), decisions, step, label = 'nom')
        

    #Function to get possible dispatcher decisions
    def get_possible_nexts(self):
        va = 1
        cs_path = False
        re_path = False
        list_actions= []
        rs, gs, cs = get_con_pos()
        if self.nom_EN > self.nom_XN: cs_path = True #Compressor path to be chosen
        else: re_path = True #Resistor path to be chosen
        if cs_path:
            cs = 1
            gas = []
            for i in range(args.decision_size):
                x = round(random.uniform(args.gas_lb, args.gas_ub), 2)
                if x not in gas:
                    gas.append(x)
            for i in range(len(gas)):
                list_actions.append([va, va, args.zeta_ub, gas[i], cs])
            list_actions.append([va, va, args.zeta_ub, args.gas_lb, 0])

        if re_path:
            cs = 0
            zeta = []
            for i in range(args.decision_size):
                x = random.randint(args.zeta_lb, args.zeta_ub)
                if x not in zeta:
                    zeta.append(x)
            for i in range(len(zeta)):
                list_actions.append([va, va, zeta[i], args.gas_lb, cs])
        if not self.next_step%args.decision_size == 0: list_actions.append(get_old_action())

        return list_actions


    def get_valid_actions(self):

        list_actions = self.get_possible_nexts()
        list_actions_with_c = []
        c1, c2, c = [0 for _ in range(3)]

        for action in list_actions:
            decision = self.generate_decision_dict(action)

            accumulated_cs = get_c(decision, config['decision_freq'], self.next_step)

            for key, values in accumulated_cs.items():
                c1 = values[0]
                c2 = values[1]
            c = abs(c1)+abs(c2)

            list_actions_with_c.append([action, c])

        list_actions_with_c.sort(key = lambda list_actions_with_c: abs(list_actions_with_c[1]))
        return list_actions_with_c

    def generate_decision_dict(self, dispatcher_action, decisions = {}): #Generate new agent_decision dictionary
        step = self.next_step
        if not decisions:
            decisions = deepcopy(self.get_agent_decision())
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
        new_decisions = remove_duplicate_decision(deepcopy(self.get_agent_decision()), decisions, step)
        return new_decisions

    #Make decision as a 'dict' type {va_DA[VA]:_, zeta_DA[RE]:_, gas_DA[CS]:_, compressor_DA[CS]:_}
    def decision_to_dict(self, da_action):
        i = 0
        da_dec = get_dispatcher_dec().copy()

        for k, v in da_dec.items():
            da_dec[k] = da_action[i]
            i += 1
        return da_dec

    def get_cumulative_c(self, decision, i = 0):
        global accumulated_cs
        c1, c2, c = [0 for _ in range(3)]
        step = self.next_step + i
        accumulated_cs = get_c(decision, config['decision_freq']-i, step)

        for key, values in accumulated_cs.items():
            c1 = values[0]
            c2 = values[1]
        c = abs(c1)+abs(c2)

        return c

    #Find the reward value for dispatcher agent
    def get_reward(self, acc_c = None):
        if not acc_c: acc_c = self.c_penalty
        #low penalty rewards high value
        if acc_c == 0:
            return 1 #Dispatcher won
        elif acc_c > 0 or acc_c < args.max_da_c/2:
            return 0.5    #Dispatcher won with half reward
        elif acc_c >= args.max_da_c/2 and acc_c < args.max_da_c:
            return 0 #Draw
        else: return -1 #Loss

    #Find the cumulative c value and its corresponding reward for NN
    def get_value(self, decision, i = 0):
        c = self.get_cumulative_c(decision, i)
        value = c-args.max_da_c/2
        if value > 0:
            return  -1
        elif value < 0:
            return  1
        else:
            return  0
