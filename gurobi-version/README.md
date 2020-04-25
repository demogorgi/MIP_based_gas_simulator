# Simulator part
### Invocation
python3 main.py scenarioPath numIterations lengthTimestep

#### compressors.yml
  specification of the compressors in the network
  
###### config.yml
  controls the amount of output

###### connections.py and nodes.py
  contains the data for all elements in the network under consideration
  files are generated externally by create_netstate

###### constants.py
  contains relevant constants for physics model
  
###### functions.py
  contains helper functions for physics model
  
###### init_decisions.yml
  contains the initial decisions for active elements (valves, compressors, ...)

###### init_scenario.py
  contains the initial physics values
  
###### main.py
  manages the iterative process
  
###### model.py
  contains the gurobi simulator model (pyhsics model)
  
###### net_sim.xml and state_sim.xml
  generated externally by create_netstate
  used to generate further state-xmls to be displayed in contour
  
###### sol2state.rb
  generates data that can be viewed in contour
  
###### urmel.py
  this file contains the simulator_step-method to perform a single simulator step

# AI part

### Add some description here
