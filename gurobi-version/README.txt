compressors.yml
  specification of the compressors in the network

constants.py
  contains relevant constants for physics model

functions.py
  contains helper functions (for physics only?)

init_decisions.yml
  contains the initial decisions for active elements (valves, compressors, ...)

init_scenario.py
  contains the initial physics values

net.py
  contains the topology and some bounds for physical values

urmel.py
  the main function
  imports all the other files
  contains the simulator model and gurobi stuff

invocation:
  python3 urmel.py
