#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 main.py path numIterations lengthTimestep

from urmel import *

for i in range(int(sys.argv[2])):
    print("step %d" % i)
    simulator_step(config, agent_decisions, compressors, i, int(sys.argv[3]))

