""" auto-generated python script by create_netstate """

import gurobipy as gp
from gurobipy import GRB

valves = gp.tuplelist([
  ('N73_1', 'N74_1')
])

flap_traps = gp.tuplelist([
	('START_1_auxMin', 'START_1_aux1'),
	('START_1_auxMax', 'START_1_aux3'),
	('N94_1_aux', 'N94_1'),
	('N80_1_aux', 'N81_1_aux')
])

resistors, diameter = gp.multidict({
	('N93_1', 'N94_1_aux'): 0.9
})

# compressors tuples
compressors = gp.tuplelist([
	('N80_1', 'N81_1')
])

pipes, length, roughness = gp.multidict({
	('N53_1', 'N54_1'): [10000, 0.000012],
	('N52_1', 'N53_1'): [10000, 0.000012],
	('START_1', 'N52_1'): [10000, 0.000012],
	('N92_1', 'N93_1'): [10000, 0.000012],
	('N91_1', 'N92_1'): [10000, 0.000012],
	('N96_1', 'N97_1'): [10000, 0.000012],
	('N97_1', 'N98_1'): [10000, 0.000012],
	('N94_1', 'N95_1'): [10000, 0.000012],
	('N95_1', 'N96_1'): [10000, 0.000012],
	('N100_1', 'END_1'): [10000, 0.000012],
	('N98_1', 'N99_1'): [10000, 0.000012],
	('N99_1', 'N100_1'): [10000, 0.000012],
	('N79_1', 'N80_1'): [10000, 0.000012],
	('N78_1', 'N79_1'): [10000, 0.000012],
	('N81_1', 'N82_1'): [10000, 0.000012],
	('N90_1', 'N91_1'): [10000, 0.000012],
	('N60_1', 'N61_1'): [10000, 0.000012],
	('N61_1', 'N62_1'): [10000, 0.000012],
	('N58_1', 'N59_1'): [10000, 0.000012],
	('N59_1', 'N60_1'): [10000, 0.000012],
	('N72_1', 'N73_1'): [10000, 0.000012],
	('N70_1', 'N71_1'): [10000, 0.000012],
	('N71_1', 'N72_1'): [10000, 0.000012],
	('N68_1', 'N69_1'): [10000, 0.000012],
	('N69_1', 'N70_1'): [10000, 0.000012],
	('N66_1', 'N67_1'): [10000, 0.000012],
	('N67_1', 'N68_1'): [10000, 0.000012],
	('N55_1', 'N56_1'): [10000, 0.000012],
	('N54_1', 'N55_1'): [10000, 0.000012],
	('N57_1', 'N58_1'): [10000, 0.000012],
	('N56_1', 'N57_1'): [10000, 0.000012],
	('N76_1', 'N77_1'): [10000, 0.000012],
	('N77_1', 'N78_1'): [10000, 0.000012],
	('N74_1', 'N75_1'): [10000, 0.000012],
	('N75_1', 'N76_1'): [10000, 0.000012],
	('N88_1', 'N89_1'): [10000, 0.000012],
	('N89_1', 'N90_1'): [10000, 0.000012],
	('N86_1', 'N87_1'): [10000, 0.000012],
	('N87_1', 'N88_1'): [10000, 0.000012],
	('N84_1', 'N85_1'): [10000, 0.000012],
	('N85_1', 'N86_1'): [10000, 0.000012],
	('N82_1', 'N83_1'): [10000, 0.000012],
	('N83_1', 'N84_1'): [10000, 0.000012],
	('N65_1', 'N66_1'): [10000, 0.000012],
	('N64_1', 'N65_1'): [10000, 0.000012],
	('N63_1', 'N64_1'): [10000, 0.000012],
	('N62_1', 'N63_1'): [10000, 0.000012],
	('START_1_aux1', 'START_1'): [10000, 0.000012],
	('START_1_aux2', 'START_1_aux1'): [10000, 0.000012],
	('START_1_aux3', 'START_1_aux2'): [10000, 0.000012],
	('N80_1', 'N80_1_aux'): [1, 0.000012],
	('N81_1_aux', 'N81_1'): [1, 0.000012]
})

# this cannot be put into the multidicts for pipes and resistors, as no keys could be appended then
diameter = {
	#pipes
	('N53_1', 'N54_1'): 0.9,
	('N52_1', 'N53_1'): 0.9,
	('START_1', 'N52_1'): 0.9,
	('N92_1', 'N93_1'): 0.9,
	('N91_1', 'N92_1'): 0.9,
	('N96_1', 'N97_1'): 0.9,
	('N97_1', 'N98_1'): 0.9,
	('N94_1', 'N95_1'): 0.9,
	('N95_1', 'N96_1'): 0.9,
	('N100_1', 'END_1'): 0.9,
	('N98_1', 'N99_1'): 0.9,
	('N99_1', 'N100_1'): 0.9,
	('N79_1', 'N80_1'): 0.9,
	('N78_1', 'N79_1'): 0.9,
	('N81_1', 'N82_1'): 0.9,
	('N90_1', 'N91_1'): 0.9,
	('N60_1', 'N61_1'): 0.9,
	('N61_1', 'N62_1'): 0.9,
	('N58_1', 'N59_1'): 0.9,
	('N59_1', 'N60_1'): 0.9,
	('N72_1', 'N73_1'): 0.9,
	('N70_1', 'N71_1'): 0.9,
	('N71_1', 'N72_1'): 0.9,
	('N68_1', 'N69_1'): 0.9,
	('N69_1', 'N70_1'): 0.9,
	('N66_1', 'N67_1'): 0.9,
	('N67_1', 'N68_1'): 0.9,
	('N55_1', 'N56_1'): 0.9,
	('N54_1', 'N55_1'): 0.9,
	('N57_1', 'N58_1'): 0.9,
	('N56_1', 'N57_1'): 0.9,
	('N76_1', 'N77_1'): 0.9,
	('N77_1', 'N78_1'): 0.9,
	('N74_1', 'N75_1'): 0.9,
	('N75_1', 'N76_1'): 0.9,
	('N88_1', 'N89_1'): 0.9,
	('N89_1', 'N90_1'): 0.9,
	('N86_1', 'N87_1'): 0.9,
	('N87_1', 'N88_1'): 0.9,
	('N84_1', 'N85_1'): 0.9,
	('N85_1', 'N86_1'): 0.9,
	('N82_1', 'N83_1'): 0.9,
	('N83_1', 'N84_1'): 0.9,
	('N65_1', 'N66_1'): 0.9,
	('N64_1', 'N65_1'): 0.9,
	('N63_1', 'N64_1'): 0.9,
	('N62_1', 'N63_1'): 0.9,
	('START_1_aux1', 'START_1'): 0.9,
	('START_1_aux2', 'START_1_aux1'): 3,
	('START_1_aux3', 'START_1_aux2'): 3,
	('N80_1', 'N80_1_aux'): 1,
	('N81_1_aux', 'N81_1'): 1,
	# resistors
	('N93_1', 'N94_1_aux'): 0.9
}

# special pipes
special = gp.tuplelist([
	('START_1_aux1', 'START_1')
])

connections = pipes + resistors + valves + flap_traps + compressors

non_pipes = [x for x in connections if x not in pipes]

