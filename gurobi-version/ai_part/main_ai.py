from .functions_ai import *
from .gas_network import *

from collections import deque
import os
import csv
from params import *
from .configs import *

def get_decisions_from_ai(solution, agent_decisions, step, penalty):

    if step < numSteps:

        Gas_Network.decisions_dict = agent_decisions
        Gas_Network.next_step = step
        Gas_Network.c_penalty = penalty

        Gas_Network.state = get_state(step-1, agent_decisions, solution)

        gas_network = Gas_Network()

        next_action = gas_network.get_possible_decisions()
        new_agent_decision = gas_network.generate_decision_dict(next_action)

        if new_agent_decision:
            return new_agent_decision
        else:
            return agent_decisions
