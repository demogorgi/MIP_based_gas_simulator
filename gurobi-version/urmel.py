#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file contains the simulator_step-method to perform a single simulator step

import importlib
import sys
from os import path
import re
import shutil
import os
import gurobipy as gp
from gurobipy import GRB
from constants import *
from functions import *
from model import *
import yaml
import plotter

output = path.join(sys.argv[1],'output')
if os.path.exists(output):
    shutil.rmtree(output)
if not os.path.exists(output):
    os.makedirs(output)

def simulator_step(config, agent_decisions, compressors, step, dt):
    # m ist the simulator model with agent decisisons, compressor specs and timestep length incorporated
    m = simulate(agent_decisions, compressors, dt)
    # control output
    m.params.logToConsole = config['grb_console']
    m.params.logfile = config['grb_logfile']
    # optimize the model ( = do a simulation step)
    m.optimize()
    # get the model status
    status = m.status
    # generate often used strings
    _step = str(step).rjust(5, "0")
    step_files_path = "".join([output, "/", config["name"], "_", _step]).replace("\\", "/")
    # if solved to optimallity
    print ("status: ", status == GRB.INFEASIBLE)
    if status == GRB.OPTIMAL: # == 2
        # plot data with gnuplot
        if config['gnuplot']: plot(_step, agent_decisions, compressors)
        if config['write_lp']: m.write(step_files_path + ".lp")
        if config['write_sol']: m.write(step_files_path + ".sol")
        # store solution in dictionary
        sol = {}
        for v in m.getVars():
            sol[v.varName] = v.x
            if config['urmel_console_output']:
                print('%s %g' % (v.varName, v.x))
        #print(sol)
        # set old to old_old and current value to old for flows and pressures
        for node in no.nodes:
            sc.var_node_p_old_old[node] = sc.var_node_p_old[node]
            sc.var_node_p_old[node] = sol["var_node_p[%s]" % node]
        for non_pipe in co.non_pipes:
            sc.var_non_pipe_Qo_old_old[non_pipe] = sc.var_non_pipe_Qo_old[non_pipe]
            sc.var_non_pipe_Qo_old[non_pipe] = sol["var_non_pipe_Qo[%s,%s]" % non_pipe]
        for pipe in co.pipes:
            sc.var_pipe_Qo_in_old_old[pipe] = sc.var_pipe_Qo_in_old[pipe]
            sc.var_pipe_Qo_in_old[pipe] = sol["var_pipe_Qo_in[%s,%s]" % pipe]
            sc.var_pipe_Qo_out_old_old[pipe] = sc.var_pipe_Qo_out_old[pipe]
            sc.var_pipe_Qo_out_old[pipe] = sol["var_pipe_Qo_out[%s,%s]" % pipe]
        return sol
    # if infeasible write IIS for analysis and debugging
    elif status == GRB.INFEASIBLE:
        if config['write_ilp']:
            if config['urmel_console_output']:
                print("Model is infeasible. %s.ilp written." % config['name'])
            m.computeIIS()
            m.write(step_files_path + ".ilp")
        else:
            if config['urmel_console_output']:
                print("Model is infeasible.")
    # don't know yet, what else
    else:
        if config['urmel_console_output']:
            print("Solution status is %d, don't know what to do." % status)
