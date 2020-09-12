from .functions_ai import *
from .gas_network import *
from .neural_network_architecture import NeuralNetworkWrapper
from .train import Train

from collections import deque
import os
import csv
from params import *
from .configs import *

def get_decisions_from_ai(solution, agent_decisions, step):

    if step < numSteps:

        Gas_Network.decisions_dict = agent_decisions
        Gas_Network.next_step = step
        Gas_Network.c_penalty = current_acc_c

        Gas_Network.state = get_state(step-1, agent_decisions, solution)

        gas_network = Gas_Network()
        net = NeuralNetworkWrapper(gas_network)

        if configs.load_model:
            file_path = configs.model_dir + "best_model.meta"
            if os.path.exists(file_path):
                net.load_model("best_model")
            else:
                print("Trained model does not exist. Starting from scratch")
        else:
            print("Trained model not loaded. Starting from scratch")

        train  = Train(gas_network, net)
        new_agent_decision = train.start()

        if new_agent_decision:
            return new_agent_decision
        else:
            return agent_decisions
