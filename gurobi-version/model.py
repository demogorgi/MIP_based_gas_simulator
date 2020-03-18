#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file contains the simulator model
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 urmel.py (or ./urmel.py)

from constants import *
from functions import *
from init_scenario import *
import gurobipy as gp
from gurobipy import GRB
from network.nodes import *
from network.connections import *

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
# v * Q for pressure drop for pipes ...
vQp = m.addVars(pipes, lb=-GRB.INFINITY, name="vQp") #:= ( vi(l,r) * var_pipe_Qo_in[l,r] + vo(l,r) * var_pipe_Qo_out[l,r] ) * rho / 3.6;
# ... and resistors
vQr = m.addVars(resistors, lb=-GRB.INFINITY, name="vQr") #:= vm(l,r) * var_non_pipe_Qo[l,r] * rho / 3.6;

# Pressure difference p_out minus p_in
delta_p = m.addVars(connections, lb=-Mp, ub=Mp, name="delta_p") #:= var_node_p[l] - var_node_p[r];

## Auxiliary variables to track dispatcher agent decisions
va_DA = m.addVars(valves, name="va_DA");
zeta_DA = m.addVars(resistors, name="zeta_DA");
gas_DA = m.addVars(compressors, name="gas_DA");
compressor_DA = m.addVars(compressors, name="compressor_DA");

## Auxiliary variables to track trader agent decisions
exit_nom_TA = m.addVars(exits, lb=-GRB.INFINITY, name="exit_nom_TA")
entry_nom_TA = m.addVars(special, name="entry_nom_TA")

## Auxiliary variable to track deviations from entry nominations ...
nom_entry_slack_DA = m.addVars(special, lb=-GRB.INFINITY, name="nom_entry_slack_DA")
# ... and from exit nominations
nom_exit_slack_DA = m.addVars(exits, lb=-GRB.INFINITY, name="nom_exit_slack_DA")

## Auxiliary variable to track balances
scenario_balance_TA = m.addVar(lb=-GRB.INFINITY, name="scenario_balance_TA")

## Auxiliary variable to track pressure violations
ub_pressure_violation_DA = m.addVars(nodes, lb=-GRB.INFINITY, name="ub_pressure_violation_DA")
lb_pressure_violation_DA = m.addVars(nodes, lb=-GRB.INFINITY, name="lb_pressure_violation_DA")

# From here on the constraints have to be added.
