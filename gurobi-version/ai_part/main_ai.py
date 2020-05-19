from .sol2state import *
from .gas_network import Gas_Network
from .neural_network_architecture import NeuralNetworkWrapper
from .train import Train
import os
import csv


def get_decisions_from_ai(solution, agent_decisions, config, compressors, dt):

    Gas_Network.decisions_dict = agent_decisions
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

    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                extracted_[key] = n

    fieldnames = list(extracted_.keys())

    return fieldnames, extracted_
