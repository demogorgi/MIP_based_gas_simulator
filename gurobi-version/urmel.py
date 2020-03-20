#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 urmel.py path (or ./urmel.py path)

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
# m ist the simulator model with agent decisisons, compressor specs and timestep length incorporated
m = simulator_model(agent_decisions,compressors,900)
# optimize the model ( = do a simulation step)
m.optimize()
# get the model status
status = m.status
# if solved to optimallity store solution in dictionary
if status == 2:
    m.write(output + "/" + name + ".lp")
    sol = {}
    for v in m.getVars():
        sol[v.varName] = v.x
        #print('%s %g' % (v.varName, v.x))
    print(sol)
# if infeasible write IIS for analysis and debugging
elif status == 3:
    print("Model is infeasible. %s.ilp written." % name)
    m.computeIIS()
    m.write(output + "/" + name + ".ilp")
# don't know yet, what else
else:
    print("Solution status is %d, don't know what to do." % status)

#print("-------------------------------------")
#print(m.getVarByName("va_DA[N23,N23_1]"))
#print("-------------------------------------")
#print(m.getAttr('VarName', m.getVars()))
#print("-------------------------------------")

