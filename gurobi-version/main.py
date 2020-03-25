#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 main.py path numIterations lengthTimestep

from urmel import *

data_path = sys.argv[1]
numSteps  = int(sys.argv[2])
dt        = int(sys.argv[3])

# read manual file with configs
# the dictionary does not change during the process
with open(path.join(data_path, 'config.yml')) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    #print(config)

# read manual file with compressor data
# the dictionary does not change during the process
with open(path.join(data_path, 'compressors.yml')) as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    #print(compressors)

# read manual file with initial gas network control
# the dictionary changes with every new control
with open(path.join(data_path, 'init_decisions.yml')) as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    #print(agent_decisions)

for i in range(numSteps):
    print("step %d" % i)
    # for every i in numSteps a simulator step is performed.
    # config (config.yml in scenario folder) controls the amount of output.
    # agent_decisions (init_decisions.yml in scenario folder for the first step) delivers the agents decisions to the simulator and can be modified for every step.
    # compressors (compressors.yml in scenario folder) specifies the compressors in the network under consideration.
    # i is the step number (neccessary for naming output files if any).
    # dt is the length of the current time step and could be changed for each iteration, but I think we shouldn't do that.
    solution = simulator_step(config, agent_decisions, compressors, i, dt)
    print("\n\nThe optimal solution is:\n%s" % (solution))

    ################################### @Bitty ###################################
    # Bitty, I think this is the place where the AI comes into play.
    # The solution should contain all information you need to compute penalties.     
    # And you can adjust the agent_decisions-dictionary here.
    ##############################################################################

