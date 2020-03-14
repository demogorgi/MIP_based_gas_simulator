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

# pressure for every node
var_node_p = m.addVars(nodes, lb=1.01325, ub=151.01325, name="var_node_p")
# flow slack variables for exits, with obj coefficient
var_boundary_node_flow_slack_positive = m.addVars(exits, obj=1, name="var_boundary_node_flow_slack_positive");
var_boundary_node_flow_slack_negative = m.addVars(exits, obj=1, name="var_boundary_node_flow_slack_negative");
# pressure slack variables for entries, with obj coefficient
var_boundary_node_pressure_slack_positive = m.addVars(entries, obj=10, name="var_boundary_node_pressure_slack_positive");
var_boundary_node_pressure_slack_negative = m.addVars(entries, obj=10, name="var_boundary_node_pressure_slack_negative");

m.write("urmel.lp")

#var_node_Qo_in = m.addVars(nodes, name="var_node_Qo_in") # >= -10000 <= 10000;
## Pipe variables
#m.addVars(var_pipe_Qo_in[P] >= -10000 <= 10000;
#m.addVars(var_pipe_Qo_out[P] >= -10000 <= 10000;
## Boundary node variables
## Non pipe connections variables
#m.addVars(var_non_pipe_Qo[CN without P] >= -10000 <= 10000;
## Flap trap variables
#m.addVars(flaptrap[FT] binary;
## Auxilary variables
## v * Q for pressure drop (for pipes and resistors)
#m.addVars(vQp[P] >= -infinity; #:= ( vi(l,r) * var_pipe_Qo_in[l,r] + vo(l,r) * var_pipe_Qo_out[l,r] ) * rho / 3.6;
#m.addVars(vQr[RE] >= -infinity; #:= vm(l,r) * var_non_pipe_Qo[l,r] * rho / 3.6;
## factors for pressure drop for pipes ...
#defnumb xip(i,o) := lambda(D[i,o], k[i,o]) * L[i,o] / ( 4 * D[i,o] * A(D[i,o]) );
## ... and resistors
#defnumb xir(i,o) := zeta[i,o] / ( 2 * A(D[i,o]) ); # * b2p); # scaling with b2p for nicer zeta range
## pressure difference p_out minus p_in
#m.addVars(delta_p[CN] >= -Mp <= Mp; #:= var_node_p[l] - var_node_p[r];
#
## Auxiliary variables to track dispatcher agent decisions
#m.addVars(va_DA[VA];
#m.addVars(zeta_DA[RE];
#m.addVars(gas_DA[CS];
#m.addVars(compressor_DA[CS];
## Auxiliary variables to track trader agent decisions
#m.addVars(exit_nom_TA[X] >= - infinity <= 0;
#m.addVars(entry_nom_TA[S] >= 0 <= infinity;
## Auxiliary variable to track deviation from nominations
#m.addVars(nom_entry_slack_DA[S] >= -infinity;
#m.addVars(nom_exit_slack_DA[X] >= - infinity;
## Auxiliary variable to track balances
#m.addVars(scenario_balance_TA >= - infinity;
## Auxiliary variable to track pressure violations
#m.addVars(ub_pressure_violation_DA[NO] >= - infinity;
#m.addVars(lb_pressure_violation_DA[NO] >= - infinity;
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

