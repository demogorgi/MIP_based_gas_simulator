from .agent_decisions_ai import Agent_Decision
from instances.scn02.nodes import *

import tensorflow as tf
import re

def ai_input(agent_decisions, solution):
    decisions = Agent_Decision()
    trader_dec = decisions.trader_decisions(agent_decisions)

    print(trader_dec)
    convert_solution(solution)
def convert_solution(solution):
    original_nodes = []
    for n in nodes:
        if '_aux' not in n:
            original_nodes.append(n)

    pressure = {}
    for k, v in solution.items():
        if k.startswith('var_node_p'):
            if not re.search('_aux', k):
                res = re.sub('var_node_p\[(\S*)]', r'\1', k)
                pressure[res] = v

    inp = tf.placeholder(pressure, tf.float32)
