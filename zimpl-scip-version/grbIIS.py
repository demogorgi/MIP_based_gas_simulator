#!/usr/bin/python
from gurobipy import *
import sys
m=read(sys.argv[1])
m.optimize()
m.computeIIS()
m.write(sys.argv[1] + ".ilp")

