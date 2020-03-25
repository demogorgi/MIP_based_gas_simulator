#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file contains the simulator_step-method to perform a single simulator step

import importlib
import sys
from os import path
import re
import glob
import os
import gurobipy as gp
from gurobipy import GRB
from constants import *
from functions import *
from model import *
import yaml

output = path.join(sys.argv[1],'output')
if not os.path.exists(output):
    os.makedirs(output)
else:
    files = glob.glob(path.join(output,"*"))
    for f in files:
        os.remove(f)

def simulator_step(config, agent_decisions, compressors, step, dt):
    # m ist the simulator model with agent decisisons, compressor specs and timestep length incorporated
    m = simulate(agent_decisions, compressors, dt)
    # optimize the model ( = do a simulation step)
    m.optimize()
    # get the model status
    status = m.status
    # generate often used strings
    _step = str(step).rjust(5, "0")
    step_files_path = "".join([output, "/", config["name"], "_", _step]).replace("\\", "/")
    # if solved to optimallity
    if status == GRB.OPTIMAL: # == 2
        # plot data with gnuplot
        if config['gnuplot']: plot(_step, agent_decisions, compressors)
        if config['write_lp']: m.write(step_files_path + ".lp")
        if config['write_sol']: m.write(step_files_path + ".sol")
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
        return sol
    # if infeasible write IIS for analysis and debugging
    elif status == GRB.INFEASIBLE and config['write_ilp']:
        print("Model is infeasible. %s.ilp written." % config['name'])
        m.computeIIS()
        m.write(step_files_path + ".ilp")
        # m.write(output + "/" + config['name'] + "_" + _step + ".ilp")
    # don't know yet, what else
    else:
        print("Solution status is %d, don't know what to do." % status)


def plot(_step, agent_decisions, compressors):
    for k in compressors:
        cs = compressors[k]
        _from, _to = k.split("^")
        gas = agent_decisions["gas"]["CS"][k]
        L_min_pi = cs["L_min_pi"]
        L_min_phi = cs["L_min_phi"]
        L_max_pi = cs["L_max_pi"]
        eta = cs["eta"]
        p_i_min = cs["p_i_min"]
        p_i_max = cs["p_i_max"]
        pi_1 = cs["pi_1"]
        pi_2 = cs["pi_2"]
        phi_max = cs["phi_max"]
        phi_min = cs["phi_min"]
        
        cmd = ";".join([
"gnuplot -e \"set term pdfcairo enhanced font 'Calibri Light, 10'",
"set output '%s/CS_%s_%s_%s.pdf'" % (output, _from, _to, _step),
# title
"set title '{/:Bold Verdichter %s -> %s (%s)}'" % (_from, _to, _step),
# labels
"set xlabel 'Fluss {/Symbol f}/m^3/s'",
"set ylabel 'Druckverh\344ltnis {/Symbol p}/1'",

# LINES
"plot [0:%d] %s" % (cs["phi_max"] + 1, " ".join([
    
    # l min line
    "[0:%d]" % (cs["L_max_pi"] + 0.5),
    "- %d / %d * x + %d title 'L_{min}' lt 1 lw 2, " % (
        L_min_pi, 
        L_min_phi, 
        L_min_pi
    ),
    
    # l max line
    "- %d / %d * x + %d title 'L_{max}' lt 1 lw 2, " % (
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_old(_from)
        )
    ),
    
    # l gas line
    "(1 - %d) * ((-%d / %d) * x + %d) + %d * ((-%d / %d) * x + %d) dashtype 4 lt 3 title 'L_{gas}', " % (
        gas,
        L_min_pi,
        L_min_phi,
        L_min_pi,
        gas,
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_old(_from)
        )
    ),
    
    # pi 1 line
    "%d dashtype 3 lt 1 title '{/Symbol p}_1', " % (pi_1),
    
    # L_max_max line
    "(-%d / %d) * x + %d dashtype 3 lt 1 lw 1 title 'L_{MAX}', " % (
        L_min_pi,
        L_min_phi,
        L_max_axis_intercept(
            L_max_pi,
            eta,
            p_i_min,
            p_i_max,
            p_i_min
        )
    ),
    
    # ulim line
    "(%d - %d) / %d * x + %d lt 1 lw 2 title 'ulim', " % (
        pi_1,
        pi_2,
        phi_max,
        pi_2
    ),
    
    # (old) pressure_to / pressure_from line
    "(%d / %d) dashtype 4 lt 3 title 'p_{out} / p_{in}'" % (
        p_old(_to), 
        p_old(_from)
    ),
])),
# phi_min line
"set arrow from %d,0 to %d,%d*2 nohead dashtype 2 lc rgb 'black' " % (
    phi_min,
    phi_min,
    pi_2
),

# phi_max line
"set arrow from %d,0 to %d,%d nohead dashtype 2 lc rgb 'black'" % (
    phi_max,
    phi_max,
    pi_2
),

# TICKS
# add L_max_axis_intercept value as tic
"set ytics add('L_{max\\_axis\\_int}(%d))' %d) " % (
    round(10 * p_old(_from)) / 10,
    L_max_axis_intercept(
        L_max_pi,
        eta,
        p_i_min,
        p_i_max,
        p_old(_from)
    )
),

# add pi_2 value as a tic
"set ytics add ('{/Symbol p}_2' %d) " % pi_2,

# add pi_1 value as a tic
"set ytics add ('{/Symbol p}_1' %d) " % pi_1,

# add L_min_pi value as a tic
"set ytics add ('{/Symbol p}_{\\_min}' %d)" % L_min_pi,

# add phi_min value as tic
"set xtics add ('{/Symbol f}_{min}' %d)" % phi_min,

# add phi_max value as a tic
"set xtics add ('{/Symbol f}_{max}' %d)" % phi_max,

# add L_phi_min value as a tic
"set xtics add ('L_{/Symbol f}_{\\_min}' %d)" % L_min_phi,


# POINTS
# add interception point
"set label at %d '' point pointtype 7 pointsize 1" % (
    intercept(
        L_min_pi, 
        L_min_phi, 
        p_i_min, 
        p_i_max,
        L_max_pi,
        eta,
        gas,
        p_old(_from),
        p_old(_to)
    )
),


# FINILIZE
"set output '%s/CS_%s_%s_%s.pdf'" % (output, _from, _to, _step),
"replot; \""
        ])
        
        os.system(cmd)
