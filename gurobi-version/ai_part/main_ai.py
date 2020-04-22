from .sol2state import *
from .gas_network import *
from .neural_network_architecture import *
from .train import *


def ai_input(solution, agent_decisions, config, compressors, dt):


    state = sol2state(solution)
    gas_network = Gas_Network(state, agent_decisions)
