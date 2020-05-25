import importlib
import sys
import re
import numpy as np
from .configs import *

wd = sys.argv[1].replace("/",".")
wd = re.sub(r'\.$', '', wd)

no = importlib.import_module(wd + ".nodes") #Nodes of the network(entry + exit +inner nodes)

original_nodes = []
for n in no.nodes:
    if '_aux' not in n:
        original_nodes.append(n)
pr, flow, dispatcher_dec, trader_dec, state_ = ({} for i in range(5))


def extract_from_solution(solution):
    state = []
    da_dec = {}

    for k, v in solution.items():
        if not re.search('_aux', k):
            if k.startswith('var_node_p'):
                res = re.sub('var_node_p\[(\S*)]', r'\1', k)
                pr[res] = round(v, 2)
            elif k.startswith('var_node_Qo_in'):
                res = re.sub('var_node_Qo_in\[(\S*)]', r'\1', k)
                flow[res] = round(v, 2)
        if re.search('(va|zeta|gas|compressor)_DA', k):
            dispatcher_dec[k] = v
        if re.search('nom_TA',k):
            trader_dec[k] = v

    da_dec = normalize_dispatcher_dec(dispatcher_dec.copy())
    pressures = normalize_pressure(pr.copy())

    for k, v in da_dec.items(): #Dispatcher decision
        state_[k] = [v]
    for value in original_nodes: # Pressure values
        #state_[value] = [pr[value], flow[value]]
        state_[value] = [pressures[value]]

    for key, value in state_.items():
        state.append(value)

    #state = normalize_state(np.array(state), 0, 1)
    state =  np.array(state)
    

    return state

def normalize_dispatcher_dec(decisions):
    for label, value in decisions.items():
        if re.search('zeta_DA', label):
            decisions[label] = value/CFG.zeta_upper
    return decisions

def normalize_pressure(pressure_dict):
    for label, value in pressure_dict.items():
        if re.search('XN', label):
            pressure_dict[label] = (value - CFG.pressure_lb_XN) / (CFG.pressure_ub - CFG.pressure_lb_XN)
        elif re.search('XH', label):
            pressure_dict[label] = (value - CFG.pressure_lb_XH) / (CFG.pressure_ub - CFG.pressure_lb_XH)
        else:
            pressure_dict[label] = (value - CFG.pressure_lb) / (CFG.pressure_ub - CFG.pressure_lb)

    return pressure_dict

# def normalize_state(array, low, high): #Normalize the values to [0,1]
#     minimum = min(array)
#     maximum = max(array)
#
#     diff = maximum - minimum
#     diffScale = high - low
#
#     return map ( lambda x: [float((x - minimum)*(float(diffScale)/diff)+low)], array)


def find_penalty(solution):

    pr_violations = 0 #Dispatcher pressure bound violations
    flow_violations  = 0 #Dispatcher flow bound violations
    trader_violations = 0 #Trader nomination violation

    for k, v in solution.items():
        if re.search('(ub|lb)_pressure_violation_DA', k):
            key = re.sub('(ub|lb)_pressure_violation_DA\[(\S*)]',r'\1_\2', k)
            if not re.search('_aux', key): pr_violations += max(0,v)

        if re.search('slack_DA', k):
            flow_violations += abs(v)
        if re.search('scenario_balance_TA', k):
            trader_violations += abs(v)


    dispatcher_penalty = int(CFG.pressure_wt_factor * pr_violations + CFG.flow_wt_factor * flow_violations)
    trader_penalty = int(0.2*trader_violations)

    return [dispatcher_penalty, trader_penalty]
