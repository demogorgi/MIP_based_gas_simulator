from .sol2statepenalty import *
from .gas_network import Gas_Network
from .neural_network_architecture import NeuralNetworkWrapper
from .train import Train

from collections import deque
import os
import csv
from params import *

def get_decisions_from_ai(solution, agent_decisions, step, penalty):

    if step < numSteps:
        Gas_Network.decisions_dict = agent_decisions
        Gas_Network.step = step
        Gas_Network.penalty = penalty
        
        Gas_Network.state = extract_from_solution(solution)
        if step-1 > 0:
            Gas_Network.penalties.append(Gas_Network.penalty)
        gas_network = Gas_Network()
        net = NeuralNetworkWrapper(gas_network)

        if CFG.load_model:
            file_path = CFG.model_dir + "best_model.meta"
            if os.path.exists(file_path):
                net.load_model("best_model")
            else:
                print("Trained model does not exist. Starting from scratch")
        else:
            print("Trained model not loaded. Starting from scratch")

        train  = Train(gas_network, net)
        new_agent_decision = train.start()

        if new_agent_decision:
            new_agent_decision = remove_duplicate_decision(agent_decisions, new_agent_decision, step)
            return new_agent_decision
        else:
            return agent_decisions

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
    else:
        extracted_['Dispatcher Penalty'] = None
        extracted_['Trader Penalty'] = None

    fieldnames = reordered_headers(list(extracted_.keys()))
    # fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def reordered_headers(fieldnames):
    order = [0,1,12,2,13,3,15,4,14,5,6,7,8,9,10,11,16,17]
    fieldnames = [fieldnames[i] for i in order]
    return fieldnames
