#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 urmel.py numIterations lengthTimestep path (or ./urmel.py path numIterations lengthTimestep)

import importlib
import sys
from os import path
import re

import os
output = path.join(sys.argv[1],'output')
if not os.path.exists(output):
    os.makedirs(output)

import gurobipy as gp
from gurobipy import GRB
from constants import *
from functions import *
from model import *
import yaml

# manual file with compressor data is read
# the dictionary does not change during the process
with open(path.join(sys.argv[1], 'compressors.yml')) as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    #print(compressors)

# manual file with initial gas network control is read
# the dictionary changes with every new control
with open(path.join(sys.argv[1], 'init_decisions.yml')) as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    #print(agent_decisions)
    
# used for output file name
name = "urmel"

for i in range(int(sys.argv[2])):
    # m ist the simulator model with agent decisisons, compressor specs and timestep length incorporated
    m = simulate(agent_decisions,compressors,int(sys.argv[3]))
    # optimize the model ( = do a simulation step)
    m.optimize()
    # get the model status
    status = m.status
    # if solved to optimallity
    if status == 2:
        #m.write(output + "/" + name + "_" + str(i).rjust(5, '0') + ".lp")
        m.write(output + "/" + name + "_" + str(i).rjust(5, '0') + ".sol")
        # store solution in dictionary
        sol = {}
        for v in m.getVars():
            sol[v.varName] = v.x
            #print('%s %g' % (v.varName, v.x))
        #print(sol)
        # set old to old_old and current value to old for flows and pressures
        for node in no.nodes:
            sc.var_node_p_old_old[node], sc.var_node_p_old[node]
            sc.var_node_p_old[node], sol["var_node_p[%s]" % node]
        for non_pipe in co.non_pipes:
            sc.var_non_pipe_Qo_old_old[non_pipe] = sc.var_non_pipe_Qo_old[non_pipe]
            sc.var_non_pipe_Qo_old[non_pipe] = sol["var_non_pipe_Qo[%s,%s]" % non_pipe]
        for pipe in co.pipes:
            sc.var_pipe_Qo_in_old_old[pipe] = sc.var_pipe_Qo_in_old[pipe]
            sc.var_pipe_Qo_in_old[pipe] = sol["var_pipe_Qo_in[%s,%s]" % pipe]
            sc.var_pipe_Qo_out_old_old[pipe] = sc.var_pipe_Qo_out_old[pipe]
            sc.var_pipe_Qo_out_old[pipe] = sol["var_pipe_Qo_out[%s,%s]" % pipe]
    # if infeasible write IIS for analysis and debugging
    elif status == 3:
        print("Model is infeasible. %s.ilp written." % name)
        m.computeIIS()
        m.write(output + "/" + name + str(i) + ".ilp")
    # don't know yet, what else
    else:
        print("Solution status is %d, don't know what to do." % status)
