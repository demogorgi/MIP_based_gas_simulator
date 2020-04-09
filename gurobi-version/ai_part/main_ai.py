
from instances.scn02.nodes import *

import tensorflow as tf
import re

def ai_input(solution):
    original_nodes = []
    for n in nodes:
        if '_aux' not in n:
            original_nodes.append(n)


    pr, inflow, dispatcher_dec, trader_dec, nodes_, violations = ({} for i in range(6))

    for k, v in solution.items():
        if not re.search('_aux', k):
            if k.startswith('var_node_p'):
                res = re.sub('var_node_p\[(\S*)]', r'\1', k)
                pr[res] = v
            elif k.startswith('var_node_Qo_in'):
                res = re.sub('var_node_Qo_in\[(\S*)]', r'\1', k)
                inflow[res] = v
        if re.search('(ub|lb)_pressure_violation_DA', k):
            key = re.sub('(ub|lb)_pressure_violation_DA\[(\S*)]',r'\1_\2', k)
            violations[key] = v
        if re.search('(va|zeta|gas|compressor)_DA', k):
            dispatcher_dec[k] = v
        if re.search('_TA',k):
            trader_dec[k] = v

    for value in original_nodes:
        nodes_[value] = [pr[value], inflow[value]]
