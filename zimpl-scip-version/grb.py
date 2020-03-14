#!/usr/bin/python
from gurobipy import *
import sys
m=read(sys.argv[1])
m.optimize()
m.write(sys.argv[1].replace(".lp",".sol"))
