#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 main.py path numIterations lengthTimestep

from urmel import *
import pprint
from deepmerge import always_merger
import random

from ai_part.main_ai import*
# from ai_my_version.main_ai import *

# read manual file with initial gas network control
# the dictionary changes with every new control
with open(path.join(data_path, 'init_decisions.yml')) as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    #print(agent_decisions)

#csv file to store (agent) decisions in a csv file in scenario output folder
with open(path.join(data_path, 'output/information.csv'), 'w+', newline='') as f:
    fieldnames, extracted_ = create_dict_for_csv(agent_decisions)
    thewriter = csv.DictWriter(f, fieldnames=fieldnames)
    thewriter.writeheader()
c = 0
sum_first_half = 0
sum_second_half = 0
s = 0
simulator_step.counter = 0
for i in range(numSteps):
    print("step %d" % i)

    # dirty hack to modify nominations
    if i > 0 and (i+1) % config['nomination_freq'] == 0 and (i+1) < numSteps:
        a = random.randrange(0, 1100, 50) # random value between 0 and 1100 which is a multiple of 50
        agent_decisions["entry_nom"]["S"]["EN_aux0^EN"][i+1] = a
        agent_decisions["entry_nom"]["S"]["EH_aux0^EH"][i+1] = 1100 - a

    # for every i in numSteps a simulator step is performed.
    # agent_decisions (init_decisions.yml in scenario folder for the first step) delivers the agents decisions to the simulator and can be modified for every step.
    # i is the step number (neccessary for naming output files if any).
    # If the last argument "porcess_type" is "sim" files (sol, lp, ... ) will be written if their option is set.
    # If the last argument "porcess_type" is not "sim" files will only be written if their option is set and if config["debug"] is True.
    solution = simulator_step(agent_decisions, i, "sim")
    c += get_nom_q_diff(solution, i, agent_decisions)
    c_values.append(c)

    #Store each new (agent) decisions value from ai_part to csv
    timestamp = timestep.strftime("%H:%M:%S")
    with open(path.join(data_path, 'output/information.csv'), 'a+', newline = '') as f:
        bn_pr_flows = get_bn_pressures_flows(solution)
        penalty = find_penalty(solution)
        penalties.append(penalty)
        fieldnames, extracted_ = create_dict_for_csv(agent_decisions, i, timestamp, penalty, bn_pr_flows)
        thewriter = csv.DictWriter(f, fieldnames=fieldnames)
        thewriter.writerow(extracted_)
    timestep += timedelta(0,dt)
    if i+1 == numSteps/2:
        sum_first_half = s
        s = 0
    elif i+1 == numSteps:
        sum_second_half = s
    else:
        if (i+1) % config['decision_freq'] == 0:
            c = round(c/config['decision_freq'], 2)
            s += abs(c)
    if (i+1) % config['decision_freq'] == 0:
        c = 0
        if config["ai"]:
            # Generating new agent_decision for the next iteration from neural network as it learns to generate
            agent_decisions = get_decisions_from_ai(solution, agent_decisions, i+1, penalty)
            if not agent_decisions: continue

    #Write agent decisions in output folder
    f = open(path.join(data_path, "output/fixed_decisions.yml"), "w")
    yaml.dump(agent_decisions, f)
    ################################### @Bitty ###################################
    # Bitty, I think this is the place where the AI comes into play.
    # The solution should contain all information you need to compute penalties.
    # And you can adjust the agent_decisions-dictionary here.
    ##############################################################################

if sum_first_half > sum_second_half:
    print('Succeeded')
print(sum_first_half, sum_second_half)

#Copying information regarding trader nominations, dispatcher decisions and penalties to another csv with new format
with open(path.join(data_path, 'output/information.csv'), 'r+', newline='') as infile, open(path.join(data_path, 'output/information_de.csv'), 'w+', newline='') as outfile:
    csv2csv_de(infile,outfile)

# generate contour output
if config["contour_output"]:
    if not config["write_sol"]:
        print("WARNING: Config parameter \"write_sol\" needs to be True if contour_output is True.")
    else:
        os.system("ruby sol2state.rb " + data_path)

# concat all compressor pdfs to a single one
if config["gnuplot"]:
    p = path.join(data_path, "output/")
    os.system("pdftk " + p + "*.pdf cat output " + p + "all.pdf")
    print("pdftk " + path.join(data_path, "output/*.pdf") + " cat output all.pdf")

print("\n\n>> finished")
