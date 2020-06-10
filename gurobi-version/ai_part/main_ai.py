from .sol2statepenalty import *
from .gas_network import Gas_Network
from .neural_network_architecture import NeuralNetworkWrapper
from .train import Train

from collections import deque
import os
import csv

numSteps  = int(sys.argv[2])
dt = int(sys.argv[3])

def get_decisions_from_ai(solution, agent_decisions, config, compressors, step):

    Gas_Network.decisions_dict = shift_to_left(agent_decisions, step)
    Gas_Network.config = config
    Gas_Network.compressors = compressors
    Gas_Network.dt = dt

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

    new_agent_decision = Gas_Network.decisions_dict

    return new_agent_decision

def create_dict_for_csv(agent_decisions, timestamp = ''):
    extracted_ = {}
    extracted_['Time'] = timestamp
    extracted_['Penalty'] = Gas_Network.penalty

    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                extracted_[key] = n

    fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def shift_to_left(agent_decisions,step):
    for key, value in agent_decisions.items():
        for label, val in value.items():
            for l, v in val.items():
                if re.search('^X', label):
                    d = deque(v)
                    d.rotate(-1)
                    agent_decisions[key][label][l] = list(d)
    return agent_decisions
