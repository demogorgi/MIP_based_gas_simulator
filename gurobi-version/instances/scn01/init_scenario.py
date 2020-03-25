# -*- coding: utf-8 -*-
""" auto-generated python script by create_netstate """

# this file contains initial values for physics
# it has to be generated from state_sim.xml automatically later

import gurobipy as gp
from gurobipy import GRB

# Pressure old_old and pressure old in bar
nodes, var_node_p_old_old, var_node_p_old = gp.multidict({
	# innodes
	'N22': [40.72325, 40.72325],
	'N23': [71.01325, 71.01325],
	'N25': [71.01325, 71.01325],
	'N18': [71.01325, 71.01325],
	'N19': [71.01325, 71.01325],
	'N20': [71.01325, 71.01325],
	'N12': [40.72325, 40.72325],
	'N11': [40.86325, 40.86325],
	'N17': [71.01325, 71.01325],
	'N26': [40.57325, 40.57325],
	'N14': [40.423249999999996, 40.423249999999996],
	'N13': [40.57325, 40.57325],
	'N23_1': [71.01325, 71.01325],
	'EN': [41.01325, 41.01325],
	'EN_aux1': [41.01325, 41.01325],
	'EN_aux2': [41.01325, 41.01325],
	'EN_aux3': [41.01325, 41.01325],
	'EH': [71.01325, 71.01325],
	'EH_aux1': [71.01325, 71.01325],
	'EH_aux2': [71.01325, 71.01325],
	'EH_aux3': [71.01325, 71.01325],
	'N26_aux': [71.01325, 71.01325],
	'N22_aux': [40.72325, 40.72325],
	'N23_aux': [71.01325, 71.01325],
	# entries
	'EN_auxMin': [71.01325, 71.01325],
	'EN_auxMax': [41.01325, 41.01325],
	'EH_auxMin': [91.01325, 91.01325],
	'EH_auxMax': [71.01325, 71.01325],
	# exits
	'XH': [71.01325, 71.01325],
	'XN': [40.27325, 40.27325]
})

# Flow old_old and flow old of non-pipes in 1000 m³/h
non_pipes, var_non_pipe_Qo_old_old, var_non_pipe_Qo_old = gp.multidict({
	# compressorStations
	('N22', 'N23'): [0, 0],
	# resistors
	('N25', 'N26_aux'): [0, 0],
	# checkValves
	('EN_auxMin', 'EN_aux1'): [0, 0],
	('EN_auxMax', 'EN_aux3'): [0, 0],
	('EH_auxMin', 'EH_aux1'): [0, 0],
	('EH_auxMax', 'EH_aux3'): [0, 0],
	('N26_aux', 'N26'): [0, 0],
	('N22_aux', 'N23_aux'): [0, 0],
	# valves
	('N23', 'N23_1'): [0, 0]
})


# Flow old_old and flow old for pipes (in and out) in 1000 m³/h
pipes, var_pipe_Qo_in_old_old, var_pipe_Qo_in_old, var_pipe_Qo_out_old_old, var_pipe_Qo_out_old = gp.multidict({
	('N20', 'XH'): [0.001,0.001,0.001,0.001],
	('N12', 'N22'): [0,0,0,0],
	('N23_1', 'N18'): [0,0,0,0],
	('EH', 'N17'): [0.001,0.001,0.001,0.001],
	('N17', 'N18'): [0.001,0.001,0.001,0.001],
	('N18', 'N19'): [0.001,0.001,0.001,0.001],
	('N19', 'N20'): [0.001,0.001,0.001,0.001],
	('N11', 'N12'): [200,200,200,200],
	('EN', 'N11'): [200,200,200,200],
	('N19', 'N25'): [0,0,0,0],
	('N14', 'XN'): [200,200,200,200],
	('N26', 'N13'): [0,0,0,0],
	('N13', 'N14'): [200,200,200,200],
	('N12', 'N13'): [200,200,200,200],
	('EN_aux1', 'EN'): [0,0,0,0],
	('EN_aux2', 'EN_aux1'): [0,0,0,0],
	('EN_aux3', 'EN_aux2'): [0,0,0,0],
	('EH_aux1', 'EH'): [0,0,0,0],
	('EH_aux2', 'EH_aux1'): [0,0,0,0],
	('EH_aux3', 'EH_aux2'): [0,0,0,0],
	('N22', 'N22_aux'): [0,0,0,0],
	('N23_aux', 'N23'): [0,0,0,0]
})
