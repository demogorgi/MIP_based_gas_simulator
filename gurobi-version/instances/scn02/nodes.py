""" auto-generated python script by create_netstate """

import gurobipy as gp
from gurobipy import GRB

# set up entries
entries, entry_flow_bound, pressure = gp.multidict({
	'EN_auxMin': [100, 71.01325],
	'EN_auxMax': [1000, 41.01325],
	'EH_auxMin': [250, 91.01325],
	'EH_auxMax': [1000, 71.01325]
})

# set up exits
exits = ['XH', 'XN']

# set up innodes
innodes = ['N22', 'N23', 'N25', 'N18', 'N19', 'N20', 'N12', 'N11', 'N17', 'N26', 'N14', 'N13', 'N23_1', 'EN', 'EN_aux1', 'EN_aux2', 'EN_aux3', 'EH', 'EH_aux1', 'EH_aux2', 'EH_aux3', 'N26_aux', 'N22_aux', 'N23_aux']

# set up nodes heights and pressure limits
nodes, heights, pressure_limits_lower, pressure_limits_upper = gp.multidict({
	# innodes
	'N22': [0.0, 1.01325, 105.01325],
	'N23': [0.0, 1.01325, 105.01325],
	'N25': [0.0, 1.01325, 105.01325],
	'N18': [0.0, 1.01325, 105.01325],
	'N19': [0.0, 1.01325, 105.01325],
	'N20': [0.0, 1.01325, 105.01325],
	'N12': [0.0, 1.01325, 105.01325],
	'N11': [0.0, 1.01325, 105.01325],
	'N17': [0.0, 1.01325, 105.01325],
	'N26': [0.0, 1.01325, 105.01325],
	'N14': [0.0, 1.01325, 105.01325],
	'N13': [0.0, 1.01325, 105.01325],
	'N23_1': [0.0, 1.01325, 105.01325],
	'EN': [0.0, 1.01325, 105.01325],
	'EN_aux1': [0.0, 1.01325, 41.01325],
	'EN_aux2': [0.0, 1.01325, 71.01325],
	'EN_aux3': [0.0, 1.01325, 71.01325],
	'EH': [0.0, 1.01325, 105.01325],
	'EH_aux1': [0.0, 1.01325, 71.01325],
	'EH_aux2': [0.0, 1.01325, 91.01325],
	'EH_aux3': [0.0, 1.01325, 91.01325],
	'N26_aux': [0, 1.01325, 105.01325],
	'N22_aux': [0.0, 1.01325, 105.01325],
	'N23_aux': [0.0, 1.01325, 105.01325],
	# boundary nodes
	'XH': [0.0, 56.01325, 105.01325],
	'XN': [0.0, 46.01325, 105.01325],
	'EN_auxMin': [0.0, 1.01325, 71.01325],
	'EN_auxMax': [0.0, 1.01325, 41.01325],
	'EH_auxMin': [0.0, 1.01325, 91.01325],
	'EH_auxMax': [0.0, 1.01325, 71.01325]
})

# all nodes
nodes = entries + exits + innodes
