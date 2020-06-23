from .sol2statepenalty import *
from .gas_network import Gas_Network
from .neural_network_architecture import NeuralNetworkWrapper
from .train import Train

from collections import deque
import os
import csv

numSteps  = int(sys.argv[2])
dt = int(sys.argv[3])

penalty = [0,0]

def get_decisions_from_ai(solution, agent_decisions, config, compressors, step):
    global penalty

    if step < numSteps:
        Gas_Network.decisions_dict = agent_decisions
        Gas_Network.config = config
        Gas_Network.compressors = compressors
        Gas_Network.dt = dt
        Gas_Network.step = step

        Gas_Network.state = extract_from_solution(solution)
        Gas_Network.penalty = find_penalty(solution)

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
        train.start()

        new_agent_decision = train.get_decision(net)
        new_agent_decision = remove_duplicate_decision(agent_decisions, new_agent_decision, step)
        penalty = Gas_Network.penalty
        return new_agent_decision

def create_dict_for_csv(agent_decisions, step = 0, timestamp = '', penalty_ = []):
    global penalty
    
    extracted_ = {}
    extracted_['Time'] = timestamp
    if penalty_:
        penalty = penalty_
    extracted_['Dispatcher Penalty'] = penalty[0]
    extracted_['Trader Penalty'] = penalty[1]

    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                for p in range(step,-1,-1):
                    if p in n:
                        extracted_[key] = n[p]
                        break
    fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def remove_duplicate_decision(prev_agent_decisions, new_agent_decisions, step):
    for (k1,v1), (k2,v2) in zip(prev_agent_decisions.items(), new_agent_decisions.items()):
        for (l1,v_1),(l2,v_2) in zip(v1.items(),v2.items()):
            for (label1, value1), (label2, value2) in zip(v_1.items(), v_2.items()):
                for i in range(step-1, -1, -1):
                    if i in value1 and step in value2:
                        if value1[i] == value2[step]:
                            del value2[step]
                            break
    return new_agent_decisions
