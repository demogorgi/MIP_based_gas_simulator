#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this file manages the iterative process
# it works for example with python3, gurobi 8.0.1, yaml 5.3
# >python3 urmel.py (or ./urmel.py)

from constants import *
from functions import *
from init_scenario import *
import gurobipy as gp
from gurobipy import GRB
from network.nodes import *
from network.connections import *
from model import *

m.write("urmel.lp")
