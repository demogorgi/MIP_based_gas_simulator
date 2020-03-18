import gurobipy as gp
from gurobipy import GRB

valves = gp.tuplelist([('N23', 'N23_1')])

flap_traps = gp.tuplelist([
   ("EN_auxMin", "EN_aux1"),
   ("EN_auxMax", "EN_aux3"),
   ("EH_auxMin", "EH_aux1"),
   ("EH_auxMax", "EH_aux3"),
   ("N26_aux", "N26"),
   ("N22_aux", "N23_aux")
  ])

resistors, diameter = gp.multidict({
  ('N25', 'N26_aux'): 0.9
  })

compressors, L_max_pi, L_min_pi, L_min_phi, p_i_min, p_i_max, phi_max, phi_min, pi_1, pi_2, eta = gp.multidict({
  ('N22', 'N23'): [3, 1.15, 2.5, 40, 80, 5, 0.5, 1.3, 1.4, 0.8]
  })

pipes, length, diameter, roughness = gp.multidict({
  ("N20", "XH"):        [20000.0, 0.9, 1.2e-05],
  ("N12", "N22"):       [20000.0, 0.9, 1.2e-05],
  ("N23_1", "N18"):      [20000.0, 0.9, 1.2e-05],
  ("EH", "N17"):        [20000.0, 0.9, 1.2e-05],
  ("N17", "N18"):       [20000.0, 0.9, 1.2e-05],
  ("N18", "N19"):       [20000.0, 0.9, 1.2e-05],
  ("N19", "N20"):       [20000.0, 0.9, 1.2e-05],
  ("N11", "N12"):       [20000.0, 0.9, 1.2e-05],
  ("EN", "N11"):        [20000.0, 0.9, 1.2e-05],
  ("N19", "N25"):       [20000.0, 0.9, 1.2e-05],
  ("N14", "XN"):        [20000.0, 0.9, 1.2e-05],
  ("N26", "N13"):       [20000.0, 0.9, 1.2e-05],
  ("N13", "N14"):       [20000.0, 0.9, 1.2e-05],
  ("N12", "N13"):       [20000.0, 0.9, 1.2e-05],
  ("EN_aux1", "EN"):      [10000.0, 0.9, 1.2e-05],
  ("EN_aux2", "EN_aux1"):   [10000.0, 3.0, 1.2e-05],
  ("EN_aux3", "EN_aux2"):   [10000.0, 3.0, 1.2e-05],
  ("EH_aux1", "EH"):      [10000.0, 0.9, 1.2e-05],
  ("EH_aux2", "EH_aux1"):   [10000.0, 3.0, 1.2e-05],
  ("EH_aux3", "EH_aux2"):   [10000.0, 3.0, 1.2e-05],
  ("N22", "N22_aux"):     [  1.0, 1.0, 1.2e-05],
  ("N23_aux", "N23"):     [  1.0, 1.0, 1.2e-05]
  })

# this cannot be put into the multidicts for pipes and resistors, as no keys could be appended then
diameter = {
  # pipes
  ("N20", "XH"):          0.9,
  ("N12", "N22"):         0.9,
  ("N23_1", "N18"):       0.9,
  ("EH", "N17"):          0.9,
  ("N17", "N18"):         0.9,
  ("N18", "N19"):         0.9,
  ("N19", "N20"):         0.9,
  ("N11", "N12"):         0.9,
  ("EN", "N11"):          0.9,
  ("N19", "N25"):         0.9,
  ("N14", "XN"):          0.9,
  ("N26", "N13"):         0.9,
  ("N13", "N14"):         0.9,
  ("N12", "N13"):         0.9,
  ("EN_aux1", "EN"):      0.9,
  ("EN_aux2", "EN_aux1"): 3.0,
  ("EN_aux3", "EN_aux2"): 3.0,
  ("EH_aux1", "EH"):      0.9,
  ("EH_aux2", "EH_aux1"): 3.0,
  ("EH_aux3", "EH_aux2"): 3.0,
  ("N22", "N22_aux"):     1.0,
  ("N23_aux", "N23"):     1.0,
  # resistors
  ('N25', 'N26_aux'):     0.9
  }

connections = pipes + resistors + valves + flap_traps + compressors

non_pipes = [x for x in connections if x not in pipes]
