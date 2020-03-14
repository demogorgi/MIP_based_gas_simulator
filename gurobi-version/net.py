# -*- coding: utf-8 -*-

# this file contains the network information
# it has to be generated from state_sim.xml automatically later

from constants import *
from functions import *
from init_scenario import *
import gurobipy as gp
from gurobipy import GRB

entries, entry_flow_bound, pressure = gp.multidict({
  'EN_auxMin': [100, 71.01325],
  'EN_auxMax': [1000, 41.01325],
  'EH_auxMin': [250, 91.01325],
  'EH_auxMax': [1000, 71.01325]
  })

exits = ['XH', 'XN']

innodes = ['N22', 'N23', 'N25', 'N18', 'N19', 'N20', 'N12', 'N11', 'N17', 'N26', 'N14', 'N13', 'N23_1', 'EN', 'EN_aux1', 'EN_aux2', 'EN_aux3', 'EH', 'EH_aux1', 'EH_aux2', 'EH_aux3', 'N26_aux', 'N22_aux', 'N23_aux']

nodes, heights, pressure_limits_lower, pressure_limits_upper = gp.multidict({
  "XH":    [0.0, 56.01325, 105.01325],
  "XN":    [0.0, 46.01325, 105.01325],
  "EN_auxMin": [0.0, 1.01325, 71.01325],
  "EN_auxMax": [0.0, 1.01325, 41.01325],
  "EH_auxMin": [0.0, 1.01325, 91.01325],
  "EH_auxMax": [0.0, 1.01325, 71.01325],
  "N22":    [0.0, 1.01325, 105.01325],
  "N23":    [0.0, 1.01325, 105.01325],
  "N25":    [0.0, 1.01325, 105.01325],
  "N18":    [0.0, 1.01325, 105.01325],
  "N19":    [0.0, 1.01325, 105.01325],
  "N20":    [0.0, 1.01325, 105.01325],
  "N12":    [0.0, 1.01325, 105.01325],
  "N11":    [0.0, 1.01325, 105.01325],
  "N17":    [0.0, 1.01325, 105.01325],
  "N26":    [0.0, 1.01325, 105.01325],
  "N14":    [0.0, 1.01325, 105.01325],
  "N13":    [0.0, 1.01325, 105.01325],
  "N23_1":   [0.0, 1.01325, 105.01325],
  "EN":    [0.0, 1.01325, 105.01325],
  "EN_aux1":  [0.0, 1.01325, 41.01325],
  "EN_aux2":  [0.0, 1.01325, 71.01325],
  "EN_aux3":  [0.0, 1.01325, 71.01325],
  "EH":    [0.0, 1.01325, 105.01325],
  "EH_aux1":  [0.0, 1.01325, 71.01325],
  "EH_aux2":  [0.0, 1.01325, 91.01325],
  "EH_aux3":  [0.0, 1.01325, 91.01325],
  "N26_aux":  [0.0, 1.01325, 105.01325],
  "N22_aux":  [0.0, 1.01325, 105.01325],
  "N23_aux":  [0.0, 1.01325, 105.01325]
  })

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

connections = pipes + valves + resistors + flap_traps + compressors

nodes = entries + exits + innodes
pipen_pipes = [x for x in connections if x not in pipes]

special = gp.tuplelist([
  ("EN_aux1", "EN"),
  ("EH_aux1", "EH")
  ])

