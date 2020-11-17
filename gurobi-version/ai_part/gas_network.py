
from copy import deepcopy
from .functions_ai import *

mean_value = lambda l,u:((u - l)/2 + l)

class Gas_Network(object):

    state = None
    next_step = 0
    decisions_dict = {}
    c_penalty = [0, 0] #Current penalty [Dispatcher penalty, Trader penalty]
    n_penalty = [0, 0] #Penalty expected for new decision
    possible_decisions = []
    num_steps = 0

    def __init__(self):
        self.row = len(self.state)
        self.nom_XN, self.nom_XH, self.nom_EN, self.nom_EH = [abs(v) for k, v in get_trader_nom(self.next_step, self.decisions_dict).items()]

    def get_action_size(self):
        return self.row

    def get_state_dimension(self):
        return (self.row, 1)

    def get_agent_decision(self):
        return deepcopy(self.decisions_dict)

    def get_possible_decisions(self):
        return self.get_possible_nexts()


    #Function to get possible dispatcher decisions
    def get_possible_nexts(self):
        va = 1
        if self.nom_EN > self.nom_XN:
            cs = 1
            gas = round(mean_value(args.gas_lb,args.gas_ub),3)
            zeta = args.zeta_ub
        else:
            cs = 0
            gas = 0
            zeta = mean_value(args.zeta_lb, args.zeta_ub)

        valid_initial_action = [va, va, zeta, gas, cs]
        self.apply_halving(valid_initial_action)
        final_action = [v for k,v in get_dispatcher_dec().items()]
        return final_action


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
        decision = self.generate_decision_dict(action)
        accumulated_cs = get_c(decision, self.num_steps, self.next_step)

        return accumulated_cs[pos][0], accumulated_cs[pos][1]


    #def perturbed_halving(self, action):
    #    sgn = random.randrange(-1,2,2) # values are -1 and 1 uniformly distributed
    #    p = random.randint(10,100) # if perturbation is bigger than 10% action should be somehow bad
    #    pert_action = action + sgn * p * action

    def apply_halving(self, action):

        #if self.next_step % config['nomination_freq'] == 0:
        gs_ub = args.gas_ub
        gs_lb = args.gas_lb

        rs_ub = args.zeta_ub
        rs_lb = args.zeta_lb

        rs, gs, cs = get_con_pos()

        if config['random_decisions']:
                action[gs] = random.randrange(100*gs_lb,100*gs_ub,1)/100
                action[cs] = random.randint(0,1)
                action[rs] = random.randrange(rs_lb,rs_ub,1)
                #b = bool(random.getrandbits(1))
                #if b:
                #    action[gs] = random.randrange(100*gs_lb,100*gs_ub,1)/100
                #    action[rs] = 1200
                #else:
                #    action[gs] = 0.0
                #    action[cs] = 0
                #    action[rs] = random.randrange(rs_lb,rs_ub,1)
                #print("b: " + str(o) + " gs: " + str(action[gs]) + " rs: " + str(action[rs]))
        else:
            for i in range(config['num_halvings']):
                c_EH, c_EN = self.get_cumulative_c(action)
                c = abs(c_EH)+abs(c_EN)
                if i == config['num_halvings']-1: break

                if self.nom_EN > self.nom_XN:
                    if c_EN > 0:
                        gs_lb = action[gs]
                        action[gs] = round(mean_value(gs_lb, gs_ub),3)
                    else:
                        if c_EN < 0:
                            gs_ub = action[gs]
                            action[gs] = round(mean_value(gs_lb, gs_ub),3)
                else:
                    if c_EH > 0:
                        rs_ub = action[rs]
                        action[rs] = round(mean_value(rs_lb, rs_ub),2)
                    else:
                        if c_EH < 0:
                            rs_lb = action[rs]
                            action[rs] = round(mean_value(rs_lb, rs_ub),2)

            if action[gs] < 0.005 and self.nom_EN > self.nom_XN:
                action_ = action.copy()
                action_[cs] = 0
                new_c_EH, new_c_EN = self.get_cumulative_c(action_)
                new_c = abs(new_c_EH)+abs(new_c_EN)

                if abs(new_c) < abs(c):
                    action = action_

        set_dispatcher_dec(self.decision_to_dict(action))
