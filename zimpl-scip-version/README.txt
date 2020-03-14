Invocation:
>ruby doIt.rb numTimesteps lengthTimestep scenarioFolder optionalArgument

numTimesteps is the number of time steps to be simulated
lengthTimestep is the length of each timestep in seconds
scenarioFolder is a folder containing scenario information and all output
optionalArgument can be "grb" if gurobi shall be used instead of scip

scenario folder has to contain
- the folder "netstate" with sim_net.xml and sim_stat.xml from create_netstate
  script in it
- compressor.yml being "---" or something like
  "N22^N23": # alias of compressor element
     # value of L_max at 0 in 1
     L_max_pi : 3
     # value of L_min at 0 in 1
     L_min_pi: 1.15
     # argument phi with P_min(phi) = 0 in 1
     L_min_phi: 2.5
     # p_i_min in bar
     p_i_min: 40
     # p_i_max in bar
     p_i_max: 80
     # phi_min in m³/s
     phi_min: 0.5
     # phi_max in m³/s
     phi_max: 5
     # pi_1
     pi_1: 1.3
     # pi_2
     pi_2: 1.4
     # eta
     eta: 0.8
- agents_decisions_0000.yml containing the agents decisions for the first time
  step. Agent decisions for later timesteps have to be inside the folder
  "output" on the same level as "netstate". Example:
  # hint:
  # use param name[S] := <> 0; if S is the empty set.
  #
  # Decisions of the trader agent
  exit_nom:
      X:
          XN: -200
          XH: -0
  
  entry_nom:
      S:
          EH_aux1^EH: 0
          EN_aux1^EN: 200
  
  # Decisions of the dispatcher agent
  va:
      VA:
          N23^N23_1: 0
  
  zeta:
      RE:
          N25^N26_aux: 100000
  
  gas:
      CS:
          N22^N23: 0
  
  compressor:
      CS:
          N22^N23: 0
