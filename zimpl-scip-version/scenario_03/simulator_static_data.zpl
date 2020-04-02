# Entrys
set E := {
<"EN_auxMin">,
<"EN_auxMax">,
<"EH_auxMin">,
<"EH_auxMax">
};

# Exits
set X := {
<"XH">,
<"XN">
};

# Innodes
set N := {
<"N22">,
<"N23">,
<"N25">,
<"N18">,
<"N19">,
<"N20">,
<"N12">,
<"N11">,
<"N17">,
<"N26">,
<"N14">,
<"N13">,
<"N23_1">,
<"EN">,
<"EN_aux1">,
<"EN_aux2">,
<"EN_aux3">,
<"EH">,
<"EH_aux1">,
<"EH_aux2">,
<"EH_aux3">,
<"N26_aux">,
<"N22_aux">,
<"N23_aux">
};

# Pipes
set P := {
<"N20", "XH">,
<"N12", "N22">,
<"N23_1", "N18">,
<"EH", "N17">,
<"N17", "N18">,
<"N18", "N19">,
<"N19", "N20">,
<"N11", "N12">,
<"EN", "N11">,
<"N19", "N25">,
<"N14", "XN">,
<"N26", "N13">,
<"N13", "N14">,
<"N12", "N13">,
<"EN_aux1", "EN">,
<"EN_aux2", "EN_aux1">,
<"EN_aux3", "EN_aux2">,
<"EH_aux1", "EH">,
<"EH_aux2", "EH_aux1">,
<"EH_aux3", "EH_aux2">,
<"N22", "N22_aux">,
<"N23_aux", "N23">
};

# Valves
set VA := {
<"N23", "N23_1">
};

# Resistors
set RE := {
<"N25", "N26_aux">
};

set FT := {
<"EN_auxMin", "EN_aux1">,
<"EN_auxMax", "EN_aux3">,
<"EH_auxMin", "EH_aux1">,
<"EH_auxMax", "EH_aux3">,
<"N26_aux", "N26">,
<"N22_aux", "N23_aux">
};

# Compressors
set CS := {
<"N22", "N23">
};

# Special set to track entry nominations
set S := {
<"EN_aux1", "EN">,
<"EH_aux1", "EH">
};

# Connections
set CN := P union VA union RE union FT union CS;

# Nodes
set NO := E union X union N;

# Boundary nodes
set BN := E union X;

#########################################
#
# Compressor modelling
#
# value of L_max at 0 in 1
param L_max_pi[CS] :=
<"N22","N23"> 5;

# value of L_min at 0 in 1
param L_min_pi[CS] :=
<"N22","N23"> 1;

# argument phi with P_min(phi) = 0 in 1
param L_min_phi[CS] :=
<"N22","N23"> 1.5;

# p_i_min in bar
param p_i_min[CS] :=
<"N22","N23"> 10;

# p_i_max in bar
param p_i_max[CS] :=
<"N22","N23"> 80;

# phi_max in m³/s
param phi_max[CS] :=
<"N22","N23"> 5.5;

# phi_min in m³/s
param phi_min[CS] :=
<"N22","N23"> 1;

# pi_1
param pi_1[CS] :=
<"N22","N23"> 1.6;

# pi_2
param pi_2[CS] :=
<"N22","N23"> 1.8;

# eta
param eta[CS] :=
<"N22","N23"> 0.8;

#########################################

# Pipe lenghts in m
param L[P] :=
<"N20","XH"> 20000.0,
<"N12","N22"> 20000.0,
<"N23_1","N18"> 20000.0,
<"EH","N17"> 20000.0,
<"N17","N18"> 20000.0,
<"N18","N19"> 20000.0,
<"N19","N20"> 20000.0,
<"N11","N12"> 20000.0,
<"EN","N11"> 20000.0,
<"N19","N25"> 20000.0,
<"N14","XN"> 20000.0,
<"N26","N13"> 20000.0,
<"N13","N14"> 20000.0,
<"N12","N13"> 20000.0,
<"EN_aux1","EN"> 10000.0,
<"EN_aux2","EN_aux1"> 10000.0,
<"EN_aux3","EN_aux2"> 10000.0,
<"EH_aux1","EH"> 10000.0,
<"EH_aux2","EH_aux1"> 10000.0,
<"EH_aux3","EH_aux2"> 10000.0,
<"N22","N22_aux"> 1.0,
<"N23_aux","N23"> 1.0;

# Pipe diameters in m
param D[P union RE] :=
<"N20","XH"> 0.9,
<"N12","N22"> 0.9,
<"N23_1","N18"> 0.9,
<"EH","N17"> 0.9,
<"N17","N18"> 0.9,
<"N18","N19"> 0.9,
<"N19","N20"> 0.9,
<"N11","N12"> 0.9,
<"EN","N11"> 0.9,
<"N19","N25"> 0.9,
<"N14","XN"> 0.9,
<"N26","N13"> 0.9,
<"N13","N14"> 0.9,
<"N12","N13"> 0.9,
<"EN_aux1","EN"> 0.9,
<"EN_aux2","EN_aux1"> 3.0,
<"EN_aux3","EN_aux2"> 3.0,
<"EH_aux1","EH"> 0.9,
<"EH_aux2","EH_aux1"> 3.0,
<"EH_aux3","EH_aux2"> 3.0,
<"N22","N22_aux"> 1.0,
<"N23_aux","N23"> 1.0,
<"N25","N26_aux"> 0.9;

# Integral pipe roughness in m
param k[P] :=
<"N20","XH"> 1.2e-05,
<"N12","N22"> 1.2e-05,
<"N23_1","N18"> 1.2e-05,
<"EH","N17"> 1.2e-05,
<"N17","N18"> 1.2e-05,
<"N18","N19"> 1.2e-05,
<"N19","N20"> 1.2e-05,
<"N11","N12"> 1.2e-05,
<"EN","N11"> 1.2e-05,
<"N19","N25"> 1.2e-05,
<"N14","XN"> 1.2e-05,
<"N26","N13"> 1.2e-05,
<"N13","N14"> 1.2e-05,
<"N12","N13"> 1.2e-05,
<"EN_aux1","EN"> 1.2e-05,
<"EN_aux2","EN_aux1"> 1.2e-05,
<"EN_aux3","EN_aux2"> 1.2e-05,
<"EH_aux1","EH"> 1.2e-05,
<"EH_aux2","EH_aux1"> 1.2e-05,
<"EH_aux3","EH_aux2"> 1.2e-05,
<"N22","N22_aux"> 1.2e-05,
<"N23_aux","N23"> 1.2e-05;

# Node heights above sea level in m
param h[NO] :=
<"XH"> 0.0,
<"XN"> 0.0,
<"EN_auxMin"> 0.0,
<"EN_auxMax"> 0.0,
<"EH_auxMin"> 0.0,
<"EH_auxMax"> 0.0,
<"N22"> 0.0,
<"N23"> 0.0,
<"N25"> 0.0,
<"N18"> 0.0,
<"N19"> 0.0,
<"N20"> 0.0,
<"N12"> 0.0,
<"N11"> 0.0,
<"N17"> 0.0,
<"N26"> 0.0,
<"N14"> 0.0,
<"N13"> 0.0,
<"N23_1"> 0.0,
<"EN"> 0.0,
<"EN_aux1"> 0.0,
<"EN_aux2"> 0.0,
<"EN_aux3"> 0.0,
<"EH"> 0.0,
<"EH_aux1"> 0.0,
<"EH_aux2"> 0.0,
<"EH_aux3"> 0.0,
<"N26_aux"> 0,
<"N22_aux"> 0.0,
<"N23_aux"> 0.0;

# entry flow bounds
param entry_flow_bound[E] := 
<"EN_auxMin"> 100,
<"EN_auxMax"> 1000,
<"EH_auxMin"> 250,
<"EH_auxMax"> 1000;

# pressures
param pressure[E] :=
<"EN_auxMin"> 71.01325,
<"EN_auxMax"> 41.01325,
<"EH_auxMin"> 91.01325,
<"EH_auxMax"> 71.01325;

# Lower Pressure Limits for all nodes
param pressureLimitsLower[NO] := 
<"XH"> 56.01325,
<"XN"> 46.01325,
<"EN_auxMin"> 1.01325,
<"EN_auxMax"> 1.01325,
<"EH_auxMin"> 1.01325,
<"EH_auxMax"> 1.01325,
<"N22"> 1.01325,
<"N23"> 1.01325,
<"N25"> 1.01325,
<"N18"> 1.01325,
<"N19"> 1.01325,
<"N20"> 1.01325,
<"N12"> 1.01325,
<"N11"> 1.01325,
<"N17"> 1.01325,
<"N26"> 1.01325,
<"N14"> 1.01325,
<"N13"> 1.01325,
<"N23_1"> 1.01325,
<"EN"> 1.01325,
<"EN_aux1"> 1.01325,
<"EN_aux2"> 1.01325,
<"EN_aux3"> 1.01325,
<"EH"> 1.01325,
<"EH_aux1"> 1.01325,
<"EH_aux2"> 1.01325,
<"EH_aux3"> 1.01325,
<"N26_aux"> 1.01325,
<"N22_aux"> 1.01325,
<"N23_aux"> 1.01325;

# Upper Pressure Limits for all nodes
param pressureLimitsUpper[NO] := 
<"XH"> 105.01325,
<"XN"> 105.01325,
<"EN_auxMin"> 71.01325,
<"EN_auxMax"> 41.01325,
<"EH_auxMin"> 91.01325,
<"EH_auxMax"> 71.01325,
<"N22"> 105.01325,
<"N23"> 105.01325,
<"N25"> 105.01325,
<"N18"> 105.01325,
<"N19"> 105.01325,
<"N20"> 105.01325,
<"N12"> 105.01325,
<"N11"> 105.01325,
<"N17"> 105.01325,
<"N26"> 105.01325,
<"N14"> 105.01325,
<"N13"> 105.01325,
<"N23_1"> 105.01325,
<"EN"> 105.01325,
<"EN_aux1"> 41.01325,
<"EN_aux2"> 71.01325,
<"EN_aux3"> 71.01325,
<"EH"> 105.01325,
<"EH_aux1"> 71.01325,
<"EH_aux2"> 91.01325,
<"EH_aux3"> 91.01325,
<"N26_aux"> 105.01325,
<"N22_aux"> 105.01325,
<"N23_aux"> 105.01325;

