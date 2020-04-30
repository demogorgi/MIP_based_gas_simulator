from .sol2state import *
from .gas_network import *
from .neural_network_architecture import *
from .train import *


def ai_input(solution, agent_decisions, config, compressors, dt):

    Gas_Network.decisions_dict = agent_decisions
    Gas_Network.config = config
    Gas_Network.compressors = compressors
    Gas_Network.dt = dt

    state = extract_from_solution(solution)
    Gas_Network.state = state

    gas_network = Gas_Network()


    net = NeuralNetworkWrapper(gas_network)

    train  = Train(gas_network, net)
    train.start()
