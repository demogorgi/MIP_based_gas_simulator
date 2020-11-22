from .functions_ai import *

mean_value = lambda l,u:((u - l)/2 + l)
cumulative_c = None
class Gas_Network(object):

    initial_state = None
    initial_decisions_dict = {}
    next_step = 0
    possible_decisions = []

    ex_nom_EH = 0
    ex_nom_EN = 0
    num_steps = config['nomination_freq']


    def __init__(self):
        self.row = len(self.initial_state)
        self.nom_XN, self.nom_XH, self.nom_EN, self.nom_EH = [abs(v) for k, v in get_trader_nom(self.next_step, deepcopy(self.initial_decisions_dict)).items()]
        self.possible_nexts = self.get_possible_nexts()
        self.save_nominations(self.nom_EH, self.nom_EN)
        self.reset()

    def reset(self):
        self.current_state = deepcopy(self.initial_state)
        self.current_decisions = deepcopy(self.initial_decisions_dict)
        self.current_step = self.next_step

    def get_action_size(self):
        return self.row

    def get_state_dimension(self):
        return (self.row, 1)

    def get_agent_decision(self):
        return deepcopy(self.current_decisions)

    def get_possible_decisions(self):
        return self.possible_decisions

    def set_possible_decisions(self, new_set_decisions = []):
        if not new_set_decisions:
            new_set_decisions = self.get_valid_actions()
        self.possible_decisions = new_set_decisions

    def save_nominations(self, old_EH, old_EN):
        self.ex_nom_EH = old_EH
        self.ex_nom_EN = old_EN


    def get_saved_nominations(self):
        return self.ex_nom_EH, self.ex_nom_EN

    def set_nominations(self, new_EN):
        decisions = deepcopy(self.get_agent_decision())
        step = self.current_step
        self.nom_EH = 1100-new_EN
        self.nom_EN = new_EN
        decisions["entry_nom"]["S"]["EN_aux0^EN"][step] = self.nom_EN
        decisions["entry_nom"]["S"]["EH_aux0^EH"][step] = self.nom_EH
        self.current_decisions = remove_duplicate_decision(deepcopy(self.get_agent_decision()), decisions, step, label = 'nom')

    #Function to get possible dispatcher decisions
    def get_possible_nexts(self):
        va = 1
        list_actions= []
        decision_pos = None
        rs_pos,gas_pos,cs_pos = get_con_pos()
        if not self.next_step%config['nomination_freq'] == 0: list_actions.append(get_old_action())
        if self.nom_EN > self.nom_XN:
            cs = 1
            gas = []
            decision_pos = gas_pos
            while len(gas) < self.get_action_size():
                x = round(random.uniform(args.gas_lb, args.gas_ub), 2)
                if x not in gas:
                    gas.append(x)
            for i in range(len(gas)):
                list_actions.append([va, va, args.zeta_ub, gas[i], cs])
        else:
            cs = 0
            zeta = []
            decision_pos = rs_pos
            while len(zeta) < self.get_action_size():
                x = random.randint(args.zeta_lb, args.zeta_ub)
                if x not in zeta:
                    zeta.append(x)
            for i in range(len(zeta)):
                list_actions.append([va, va, zeta[i], args.gas_lb, cs])

        list_actions.append([va, va, args.zeta_ub, args.gas_lb, 0])
        #random.shuffle(list_actions)
        pos_values = random.sample(range(0, len(list_actions)), self.get_action_size())
        list_actions = [list_actions[i] for i in pos_values]
        list_actions.sort(key = lambda list_actions: abs(list_actions[decision_pos]))
        return list_actions

    #Find accumulated c for all decisions in the pool
    def get_valid_actions(self):
        global accumulated_cs
        list_actions = self.possible_nexts
        list_actions_with_c = []
        c1, c2, c = [0 for _ in range(3)]
        pos = get_end_position(self.next_step)
        for action in list_actions:
            decision = self.generate_decision_dict(action)
            accumulated_cs = get_c(decision, self.num_steps, self.next_step)
            c1 = accumulated_cs[pos][0]
            c2 = accumulated_cs[pos][1]
            c = abs(c1)+abs(c2)

            list_actions_with_c.append([action, c])

        #list_actions_with_c.sort(key = lambda list_actions_with_c: abs(list_actions_with_c[1]))
        return list_actions_with_c

    #Generate new agent_decision dictionary
    def generate_decision_dict(self, dispatcher_action, decisions = {}):
        step = self.current_step
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

    #Calculate cumulative sum of c
    def get_cumulative_c(self, decision, i = 0):
        global accumulated_cs, cumulative_c
        i *= config['decision_freq']
        c1, c2, c = [0 for _ in range(3)]
        step = self.next_step + i
        accumulated_cs = get_c(decision, self.num_steps-i, step)
        pos = get_end_position(self.next_step)
        c1 = accumulated_cs[pos][0]
        c2 = accumulated_cs[pos][1]

        c = abs(c1)+abs(c2)
        cumulative_c = c
        return c

    #Find the weight value for dispatcher agent
    def get_reward(self, acc_c = None):
        if not acc_c:
            acc_c = cumulative_c if cumulative_c else config['winning_threshold']/2
        #low penalty rewards high value
        if acc_c == 0:
            return 1
        elif acc_c > 0 and acc_c < config['winning_threshold']/2:
            return 0.75
        elif acc_c >= config['winning_threshold']/2 and acc_c < config['winning_threshold']:
            return 0.5
        else: return 0.1

    #Find the cumulative c value and its corresponding reward for NN
    def get_value(self, decision, i = 0):
        c = self.get_cumulative_c(decision, i)
        value = c-config['winning_threshold']/2
        if value > 0:
            return  -1 #Loss
        elif value < 0:
            return  1 #Won
        else:
            return  0 #Draw

    #Find the state after performing the chosen decision over decision frequency time steps
    def apply_action(self, decisions):
        solution = None
        for i in range(config['decision_freq']):
            step = self.current_step+i
            if step < numSteps:
                solution = simulator_step(decisions, step, "ai")
        if solution:
            self.current_decisions = decisions
            self.current_state = get_state(step, decisions, solution)
            self.current_step = step+1
