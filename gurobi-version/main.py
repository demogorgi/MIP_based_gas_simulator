#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 main.py path numIterations lengthTimestep

from urmel import *
from datetime import datetime, timedelta

timestep = datetime.now()

data_path = sys.argv[1]
numSteps  = int(sys.argv[2])
dt        = int(sys.argv[3])

# default configs which are merged with instance configuration
config = {
    # prefix for output filenames
    "name": "urmel",
    # write problem files in the lp-format?
    "write_lp": False,
    # write solution files in the sol-format?
    "write_sol": False,
    # write irreducible infeasibility set if problem is infeasible?
    "write_ilp": False,
    # write wheel maps with gnuplot?
    "gnuplot": True,
    # console output?
    "urmel_console_output": False,
    # gurobi logfile
    "grb_logfile": "gurobi.log",
    # gurobi console output
    "grb_console": False,
    # contour output (net- and state-files in contour folder)
    "contour_output": False,
    # is the ai-part active?
    "ai" : True
}

# read manual file with configs
# the dictionary does not change during the process
if os.path.exists(os.path.join(data_path, "config.yml")):
    with open(os.path.join(data_path, 'config.yml')) as file:
        ymlConfig = yaml.load(file, Loader=yaml.FullLoader)
        merged = {**config, **ymlConfig}
        config = merged
        print(config)

if config["ai"]:
    from ai_part.main_ai import *

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

#csv file to store agent decisions from ai in a csv file
if config["ai"]:
    with open('./ai_part/decisions_file.csv', 'w+', newline='') as f:
        fieldnames, extracted_ = create_dict_for_csv(agent_decisions)
        thewriter = csv.DictWriter(f, fieldnames=fieldnames)
        thewriter.writeheader()


for i in range(numSteps):
    print("step %d" % i)
    # for every i in numSteps a simulator step is performed.
    # config (config.yml in scenario folder) controls the amount of output.
    # agent_decisions (init_decisions.yml in scenario folder for the first step) delivers the agents decisions to the simulator and can be modified for every step.
    # compressors (compressors.yml in scenario folder) specifies the compressors in the network under consideration.
    # i is the step number (neccessary for naming output files if any).
    # dt is the length of the current time step and could be changed for each iteration, but I think we shouldn't do that.
    solution = simulator_step(config, agent_decisions, compressors, i, dt)

    if config["ai"]:
        #Generating new agent_decision for the next iteration from neural network as it learns to generate
        agent_decisions = get_decisions_from_ai(solution, agent_decisions, config, compressors, dt)

        #Store each new agent_decisions value from ai_part to csv
        timestamp = timestep.strftime("%H:%M:%S")
        with open('./ai_part/decisions_file.csv', 'a+', newline = '') as f:
            fieldnames, extracted_ = create_dict_for_csv(agent_decisions, timestamp)
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)
            thewriter.writerow(extracted_)
        timestep += timedelta(0,dt)

    ################################### @Bitty ###################################
    # Bitty, I think this is the place where the AI comes into play.
    # The solution should contain all information you need to compute penalties.
    # And you can adjust the agent_decisions-dictionary here.
    ##############################################################################


# generate contour output
if config["contour_output"]:
    if not config["write_sol"]:
        print("WARNING: Config parameter \"write_sol\" needs to be True if contour_output is True.")
    else:
        os.system("ruby sol2state.rb " + sys.argv[1])

# concat all compressor pdfs to a single one
if config["gnuplot"]:
    p = path.join(sys.argv[1], "output/")
    os.system("pdftk " + p + "*.pdf cat output " + p + "all.pdf")
    print("pdftk " + path.join(sys.argv[1], "output/*.pdf") + " cat output all.pdf")

print("\n\n>> finished")
