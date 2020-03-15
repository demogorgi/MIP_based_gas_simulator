#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file contains the simulator core

import yaml
# manual file with compressor data is read
# the dictionary does not change during the process
with open(r'compressors.yml') as file:
    compressors = yaml.load(file, Loader=yaml.FullLoader)
    print(compressors)

# manual file with initial gas network control is read
# the dictionary changes with every new control
with open(r'init_decisions.yml') as file:
    agent_decisions = yaml.load(file, Loader=yaml.FullLoader)
    print(agent_decisions)

from constants import *
from functions import *
from net import *
from init_scenario import *
import gurobipy as gp
from gurobipy import GRB

# Model
m = gp.Model("urmel")

## Node variables
# pressure for every node
var_node_p = m.addVars(nodes, lb=1.01325, ub=151.01325, name="var_node_p")
# flow slack variables for exits, with obj coefficient
var_boundary_node_flow_slack_positive = m.addVars(exits, obj=1, name="var_boundary_node_flow_slack_positive");
var_boundary_node_flow_slack_negative = m.addVars(exits, obj=1, name="var_boundary_node_flow_slack_negative");
# pressure slack variables for entries, with obj coefficient
var_boundary_node_pressure_slack_positive = m.addVars(entries, obj=10, name="var_boundary_node_pressure_slack_positive");
var_boundary_node_pressure_slack_negative = m.addVars(entries, obj=10, name="var_boundary_node_pressure_slack_negative");
# node inflow for entries and exits (inflow is negative for exits)
var_node_Qo_in = m.addVars(nodes, lb=-10000, ub=10000, name="var_node_Qo_in")

## Pipe variables
var_pipe_Qo_in = m.addVars(pipes, lb=-10000, ub=10000, name="var_pipe_Qo_in")
var_pipe_Qo_out = m.addVars(pipes, lb=-10000, ub=10000, name="var_pipe_Qo_out")

## Non pipe connections variables
var_non_pipe_Qo = m.addVars(non_pipes, lb=-10000, ub=10000, name="var_non_pipe_Qo")

## Flap trap variables
flaptrap = m.addVars(flap_traps, vtype=GRB.BINARY, name="flaptrap")

## Auxilary variables
# v * Q for pressure drop (for pipes and resistors)
vQp = m.addVars(pipes, lb=-GRB.INFINITY, name="vQp") #:= ( vi(l,r) * var_pipe_Qo_in[l,r] + vo(l,r) * var_pipe_Qo_out[l,r] ) * rho / 3.6;
vQr = m.addVars(resistors, lb=-GRB.INFINITY, name="vQr") #:= vm(l,r) * var_non_pipe_Qo[l,r] * rho / 3.6;

# pressure difference p_out minus p_in
delta_p = m.addVars(connections, lb=-Mp, ub=Mp, name="delta_p") #:= var_node_p[l] - var_node_p[r];

## Auxiliary variables to track dispatcher agent decisions
va_DA = m.addVars(valves, name="va_DA");
zeta_DA = m.addVars(resistors, name="zeta_DA");
gas_DA = m.addVars(compressors, name="gas_DA");
compressor_DA = m.addVars(compressors, name="compressor_DA");

## Auxiliary variables to track trader agent decisions
exit_nom_TA = m.addVars(exits, lb=-GRB.INFINITY, name="exit_nom_TA")
entry_nom_TA = m.addVars(special, name="entry_nom_TA")

## Auxiliary variable to track deviation from nominations
#m.addVars(nom_entry_slack_DA[S] >= -infinity;
#m.addVars(nom_exit_slack_DA[X] >= - infinity;

## Auxiliary variable to track balances
#m.addVars(scenario_balance_TA >= - infinity;

## Auxiliary variable to track pressure violations
#m.addVars(ub_pressure_violation_DA[NO] >= - infinity;
#m.addVars(lb_pressure_violation_DA[NO] >= - infinity;

m.write("urmel.lp")

#
## Create decision variables for the foods to buy
## buy = m.addVars(foods, name="buy")
#
## You could use Python looping constructs and m.addVar() to create
## these decision variables instead.  The following would be equivalent
##
## buy = {}
## for f in foods:
##   buy[f] = m.addVar(name=f)
#
## The objective is to minimize the costs
#m.setObjective(buy.prod(cost), GRB.MINIMIZE)
#
## Using looping constructs, the preceding statement would be:
##
## m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

