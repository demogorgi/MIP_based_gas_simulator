from .sol2state import *
from .gas_network import *
from .neural_network_architecture import *
from .train import *


def ai_input(solution, agent_decisions, config, compressors, dt):


    state = extract_from_solution(solution)
    gas_network = Gas_Network(state, agent_decisions)

    net = NeuralNetworkWrapper(gas_network)

    train  = Train(gas_network, net)
    train.start(config, compressors, dt)
