#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 main.py path numIterations lengthTimestep

from urmel import *

data_path = sys.argv[1]

# manual file with configs
with open(path.join(data_path, 'config.yml')) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    #print(config)

# manual file with compressor data is read
# the dictionary does not change during the process
with open(path.join(data_path, 'compressors.yml')) as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    #print(compressors)

# manual file with initial gas network control is read
# the dictionary changes with every new control
with open(path.join(data_path, 'init_decisions.yml')) as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    #print(agent_decisions)

numSteps = int(sys.argv[2])
dt = int(sys.argv[3])
for i in range(numSteps):
    print("step %d" % i)
    # for every i in numSteps a simulator step is performed.
    # config (config.yml in scenario folder) controls the amount of output.
    # agent_decisions (init_decisions.yml in scenario folder for the first step) delivers the agents decisions to the simulator and can be modified for every step.
    # compressors (compressors.yml in scenario folder) specifies the compressors in the network unde consideration.
    # i is the step number (neccessary for naming output files).
    # dt is the length of the current time step and could be changed for each iteration, but I think we shouldn't do that.
    simulator_step(config, agent_decisions, compressors, i, dt)

