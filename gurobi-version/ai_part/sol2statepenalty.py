import importlib
import sys
import re
import numpy as np
import random

from .configs import *

wd = sys.argv[1].replace("/",".")
wd = re.sub(r'\.$', '', wd)

no = importlib.import_module(wd + ".nodes") #Nodes of the network(entry + exit +inner nodes)
co = importlib.import_module(wd + ".connections") #Connections of the network

special_pipes = []
for i in co.special:
    special_pipes.append(re.sub("\('(\S*)',\s'(\S*)'\)", r'\1,\2', str(i)))

original_nodes = []
for n in no.nodes:
    if '_aux' not in n:
        if '_HD' not in n:
            if '_ND' not in n:
                original_nodes.append(n)

pr, flow, dispatcher_dec, trader_dec, state_ = ({} for i in range(5))


def extract_from_solution(solution):
    #global pr, dispatcher_dec, trader_dec
    state = []
    da_dec = {}

    for k, v in solution.items():
        if not re.search('_aux|_HD|_ND', k):
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
    ta_dec = normalize_trader_dec(trader_dec.copy())
    pressures = normalize_pressure(pr.copy())

    for k, v in da_dec.items(): #Dispatcher decision
        state_[k] = [v]
    for k, v in ta_dec.items(): #Trader decision
        state_[k] = [v]

    for value in original_nodes:
        #state_[value] = [pr[value], flow[value]]
        state_[value] = [pressures[value]] # Pressure values

    for key, value in state_.items():
        state.append(value)

    state =  np.array(state)

    return state

def normalize_dispatcher_dec(decisions):
    for label, value in decisions.items():
        if re.search('zeta_DA', label):
            decisions[label] = value/10000
    return decisions

def normalize_pressure(pressure_dict):
    for label, value in pressure_dict.items():
        pressure_dict[label] = (value - no.pressure_limits_lower[label])/(no.pressure_limits_upper[label] - no.pressure_limits_lower[label])
    return pressure_dict

def normalize_trader_dec(decisions):
    norm = lambda value, lb, ub: (value - lb)/(ub - lb)
    for label, value in decisions.items():
        key = re.sub('nom\S*_TA\[(\S*)]', r'\1', label)
        if re.search('XH', key):
            decisions[label] = norm(value, no.q_lb['XH'], no.q_ub['XH'])
        elif re.search('XN', key):
            decisions[label] = norm(value, no.q_lb['XN'], no.q_ub['XN'])
        elif re.search('EH', key):
            decisions[label] = norm(value, no.q_lb['EH'], no.q_ub['EH'])
        elif re.search('EN', key):
            decisions[label] = norm(value, no.q_lb['EN'], no.q_ub['EN'])
    return decisions

def find_penalty(solution):

    pr_violations = 0 #Dispatcher pressure bound violations
    flow_violations  = 0 #Dispatcher flow bound violations
    trader_violations = 0 #Trader nomination violation

    for k, v in solution.items():
        if re.search('(ub|lb)_pressure_violation_DA', k):
            key = re.sub('(ub|lb)_pressure_violation_DA\[(\S*)]',r'\1_\2', k)
            if not re.search('_aux|_HD|_ND', key): pr_violations += max(0,v)

        if re.search('slack_DA', k):
            flow_violations += abs(v)
        if re.search('scenario_balance_TA', k):
            trader_violations += abs(v)

    dispatcher_penalty = int(CFG.pressure_wt_factor * pr_violations + CFG.flow_wt_factor * flow_violations)
    trader_penalty = trader_violations

    return [dispatcher_penalty, trader_penalty]

def get_con_pos():
    va = 0
    rs = 0
    cs = 0
    for k,v in dispatcher_dec.items():
        if re.search('va', k):
            va += 1
        if re.search('zeta', k):
            rs += 1
        if re.search('compressor',k):
            cs += 1
    rs_pos = va
    gas_pos = va+rs
    cs_pos = va+rs+cs
    return rs_pos,gas_pos,cs_pos

def get_bn_pressures_flows(solution):
    exit_pr_flows = {}
    for k,v in solution.items():
        if re.findall(r"var_node_p\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_node_Qo_in\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_pipe_Qo_in\[("+'|'.join(special_pipes)+r")]",k):
            exit_pr_flows[k] = v
    return exit_pr_flows
