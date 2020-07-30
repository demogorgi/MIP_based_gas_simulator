import importlib
import sys
import re
import numpy as np
import random

from urmel import *

from .utils import *
from .configs import penalties

args = dotdict({
    #Weights to calculate penalty for both agents
    'pressure_wt_factor' : 1,
    's_flow_wt_factor' : 0.1,
    'x_flow_wt_factor': 0.05,
    #Upper and lower limit for generating a drag factor value for RE
    'zeta_ub' : 1200,
    'zeta_lb' : 100,
})

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

entry_q_ub = no.q_ub['EH']
pr,dispatcher_dec, trader_nom, state_ = ({} for i in range(4))

def get_agents_dict(step, agent_decisions):
    agents_dict = {}
    for k1,v1 in agent_decisions.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2.items():
                if re.search('(exit|entry)_nom', k1):
                    key = k1+"_TA["+k3+"]"
                else:
                    key = k1+"_DA["+k3+"]"
                for i in range(step,-1,-1):
                    if i in v3:
                        break
                agents_dict[key] = v3[i]
    return agents_dict

def get_state(step, agent_decisions):
    global trader_nom, dispatcher_dec

    for k, v in states[step-1]['p'].items():
        if not re.search('_aux|_HD|_ND', k):
            pr[k] = round(v,2)

    agents_dict = get_agents_dict(step,agent_decisions)
    trader_nom = {k:v for k, v in agents_dict.items() if re.search('_TA',k)}
    dispatcher_dec = {k:v for k, v in agents_dict.items() if re.search('_DA',k)}

    da_dec = normalize_dispatcher_dec(dispatcher_dec.copy())
    ta_dec = normalize_trader_noms(trader_nom.copy())
    pressures = normalize_pressure(pr.copy())

    for k, v in da_dec.items(): #Dispatcher decision
        state_[k] = [v]
    for k, v in ta_dec.items(): #Trader decision
        state_[k] = [v]

    for value in original_nodes:
        state_[value] = [pressures[value]] # Pressure values

    state = np.array([value for key, value in state_.items()])

    return state
def get_trader_nom(step, agent_decisions):
    dec_dict = get_agents_dict(step,agent_decisions)
    trader_noms = {k:v for k, v in dec_dict.items() if re.search('_TA',k)}
    return trader_noms.copy()

def get_dispatcher_dec():
    return dispatcher_dec.copy()

def get_old_action():
    old_action = list(v for k, v in get_dispatcher_dec().items())
    return old_action

def normalize_dispatcher_dec(decisions):
    for label, value in decisions.items():
        if re.search('zeta_DA', label):
            decisions[label] = value/10000
    return decisions

def normalize_pressure(pressure_dict):
    for label, value in pressure_dict.items():
        pressure_dict[label] = (value - no.pressure_limits_lower[label])/(no.pressure_limits_upper[label] - no.pressure_limits_lower[label])
    return pressure_dict

def normalize_trader_noms(decisions):
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
    entry_flow_violations  = 0 #Dispatcher flow bound violations
    exit_flow_violations = 0
    trader_violations = 0 #Trader nomination violation
    entry_flow_violations_EN = 0
    entry_flow_violations_EH = 0
    exit_flow_violations_XN = 0
    exit_flow_violations_XH = 0

    for k, v in solution.items():
        if re.search('(ub|lb)_pressure_violation_DA', k):
            key = re.sub('(ub|lb)_pressure_violation_DA\[(\S*)]',r'\1_\2', k)
            if not re.search('_aux|_HD|_ND', key): pr_violations += max(0,v)

        if re.search('slack_DA', k):
            res = re.sub('(\S*)\[(\S*)]', r'\1\2', k)
            if 'entry' in res:
                if 'EN' in res:
                    entry_flow_violations_EN += v
                else:
                    entry_flow_violations_EH += v
            else:
                if 'XN' in res:
                    exit_flow_violations_XN += v
                else:
                    exit_flow_violations_XH += v

        if re.search('scenario_balance_TA', k):
            trader_violations += abs(v)

    entry_flow_violations = abs(entry_flow_violations_EN) + abs(entry_flow_violations_EH)
    exit_flow_violations = abs(exit_flow_violations_XN) + abs(exit_flow_violations_XH)



    dispatcher_penalty = int(args.pressure_wt_factor * pr_violations
                             + args.s_flow_wt_factor * entry_flow_violations
                             + args.x_flow_wt_factor * exit_flow_violations)
    trader_penalty = trader_violations

    return [dispatcher_penalty, trader_penalty]

def get_con_pos():
    va = 0
    rs = 0
    cs = 0
    for k,v in get_dispatcher_dec().items():
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

#Function to remove duplicate entries from fixed_decisions.yml file
def remove_duplicate_decision(prev_agent_decisions, new_agent_decisions, step):
    for (k1,v1), (k2,v2) in zip(prev_agent_decisions.items(), new_agent_decisions.items()):
        if not re.search('(entry|exit)_nom',k1):
            for (l1,v_1),(l2,v_2) in zip(v1.items(),v2.items()):
                for (label1, value1), (label2, value2) in zip(v_1.items(), v_2.items()):
                    for i in range(step, -1, -1):
                        if i in value1:
                            break
                    if value1[i] == value2[step]:
                        del value2[step]
    return new_agent_decisions

#Create csv to store agent decisions, boundary flows, pressures and agent penalty values
def create_dict_for_csv(agent_decisions, step = 0, timestamp = '', penalty = [], bn_pr_flows = {}):

    extracted_ = {}
    acc_penalty = 0
    extracted_['Time'] = timestamp
    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                for p in range(step,-1,-1):
                    if p in n:
                        extracted_[key] = n[p]
                        break
    if not bn_pr_flows:
        for i in no.exits:
            extracted_[f"var_node_p[{i}]"] = None
        for i in no.exits:
            extracted_[f"var_node_Qo_in[{i}]"] = None
        for i in special_pipes:
            extracted_[f"var_pipe_Qo_in[{i}]"] = None
    else:
        for i, j in bn_pr_flows.items():
            extracted_[i] = round(j,3)
    if penalty:
        extracted_['Dispatcher Penalty'] = penalty[0]
        extracted_['Trader Penalty'] = penalty[1]
        if not step%8 == 0:
            i = step
            while not i%8 == 0:
                acc_penalty += penalties[i][0]
                i -= 1
            acc_penalty += penalties[i][0]
        else:
            acc_penalty = penalties[step][0]
        extracted_['Accumulated'] = acc_penalty
    else:
        extracted_['Dispatcher Penalty'] = None
        extracted_['Trader Penalty'] = None
        extracted_['Accumulated'] = None

    fieldnames = reordered_headers(list(extracted_.keys()))
    # fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def reordered_headers(fieldnames):
    order = [0,1,12,2,13,3,15,4,14,5,6,7,8,9,10,11,16,17,18]
    fieldnames = [fieldnames[i] for i in order]
    return fieldnames
