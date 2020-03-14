# Absolute value of old flow of non-pipes
param var_non_pipe_Qo_old_abs[<l,r> in CN without P]     := abs(var_non_pipe_Qo_old[l,r]);
# Absolute value of old_old flow of non-pipes
param var_non_pipe_Qo_old_old_abs[<l,r> in CN without P] := abs(var_non_pipe_Qo_old_old[l,r]);
# Absolute value of old in and outflow of pipes
param var_pipe_Qo_in_old_abs[<l,r> in P]                 := abs(var_pipe_Qo_in_old[l,r]);
param var_pipe_Qo_out_old_abs[<l,r> in P]                := abs(var_pipe_Qo_out_old[l,r]);
# Absolute value of old_old in and outflow of pipes
param var_pipe_Qo_in_old_old_abs[<l,r> in P]             := abs(var_pipe_Qo_in_old_old[l,r]);
param var_pipe_Qo_out_old_old_abs[<l,r> in P]            := abs(var_pipe_Qo_out_old_old[l,r]);

# Mean values are used to stabilize simulation
defnumb stabilizer(a,b) := if a * b > 1 then
                              if a > 0 then
                                 sqrt(a * b)
                              else
                                 -sqrt(a * b)
                              end
                           else
                              ( a + b ) / 2
                           end;
defnumb p_old(n)        := stabilizer(var_node_p_old[n], var_node_p_old_old[n]);
defnumb q_old(l,r)      := stabilizer(var_non_pipe_Qo_old_abs[l,r], var_non_pipe_Qo_old_old_abs[l,r]);
defnumb q_in_old(l,r)   := stabilizer(var_pipe_Qo_in_old_abs[l,r], var_pipe_Qo_in_old_old_abs[l,r]);
defnumb q_out_old(l,r)  := stabilizer(var_pipe_Qo_out_old_abs[l,r], var_pipe_Qo_out_old_old_abs[l,r]);

# Function and Parameter definitions for pipe model
param M   := 18.349; # molar mass of natural gas in kg/kmol
param Tm  := 283.15; # mean gas temperature in K

param R   := 8.3144598; # universal gas constant in J/(mol K)
param Rs  := 1000 * R / M; # specific gas constant in J/(kg K)
param Pi  := 3.14159265359; # Pi
param g   := 9.80665; # gravitational acceleration in m/s²
param pc  := 45.604; # pseudocritical Pressure in bar
param Tc  := 191.918; # pseudocritical Temperature in Kelvin

param b2p := 100000; # factor bar to pascal
param rho := 0.8; # relative density (methane to air)

param Mp  := 150; # unit bar, upper pressure bound - lower pressure bound
param Mq  := 10000; # unit 1000 m³/h, upper flow bound

defnumb pr(p)              := p / pc; # reduced pressure (2.4 Forne)
defnumb Tr(T)              := T / Tc; # reduced Temperature (2.4 Forne)
defnumb A(diam)            := Pi * ( diam / 2 ) ** 2; # cross sectional area of a pipe in m²
defnumb z(p,T)             := 1 - 3.52 * pr(p) * exp(-2.26 * Tr(T)) + 0.274 * pr(p) ** 2 * exp(-1.878 * Tr(T)); # compressibility factor Papay (2.4 Forne) # Felix: falsch! 0.274, nicht 0.247
defnumb zm(pi,po)          := ( z(pi,Tm) + z(po,Tm) ) / 2; # compressibility factor Papay (2.4 Forne)
defnumb lambda(diam,rough) := ( 2 * log(diam/rough) + 1.138 ) ** -2; # Nikuradze (2.19 Forne), diameter diam in m, integral roughness rough in m
defnumb rtza(i,o)          := Rs * Tm * zm(p_old(i),p_old(o)) / A(D[i,o]); # Rs * Tm * zm / A
defnumb vi(i,o)            := rtza(i,o) * rho / 3.6 * q_in_old(i,o) / ( b2p * p_old(i) ); # Eingangsgeschwindigkeit # Felix Faktor 0.8/3.6 und 100000
defnumb vo(i,o)            := rtza(i,o) * rho / 3.6 * q_out_old(i,o) / ( b2p * p_old(o) ); # Ausgangsgeschwindigkeit # Felix Faktor 0.8/3.6 und 100000

# Function for resistor model
#defnumb vm(i,o) := ( rtza(i,o) * q_old(i,o) ) / 2 * ( 1 / p_old(i) + 1 / p_old(o) ); # Für Widerstandsmodellierung
defnumb vm(i,o) := rho / 3.6 * ( rtza(i,o) * q_old(i,o) ) / 2 * 1 / b2p * ( 1 / p_old(i) + 1 / p_old(o) ); # Für Widerstandsmodellierung

# Functions for compressor model
#
defnumb L_min(Lminpi,Lminphi,phi) :=  - Lminpi / Lminphi * phi + Lminpi;
# Achsenabschnitt der Maximalleistung als Funktion vom Eingangsdruck. Quasi "Maximale Max-Leistung"
defnumb L_max_axis_intercept(Lmax,Leta,p_in_min,p_in_max,p_in) := Lmax * ( Leta - 1 ) / ( p_in_max - p_in_min ) * ( p_in - p_in_min ) + Lmax;
# Maximalleistung als Funktion vom Fluss unter Verwendung des Achsenabschnitts. Die Steigung erhalten wir aus der Parametrierung der Minimalleistung.
defnumb L_max(Lminpi,Lminphi,Lmax,Leta,p_in_min,p_in_max,phi,p_in) := - Lminpi / Lminphi * phi + L_max_axis_intercept(Lmax,Leta,p_in_min,p_in_max,p_in);
# Leistung als Funktion des "Gaspedals" zwischen 0% und 100%
defnumb L_gas(Lminpi,Lminphi,phi,gasp) := ( 1 - gasp ) * L_min(Lminpi,Lminphi,phi) + gasp * L_max(Lminpi,Lminphi,Lmax,Leta,p_in_min,p_in_max,phi,p_in);
# pi2: Geradengleichung mit den Punkten (0,pi_2) und (phi_max,pi_1)
defnumb ulim(phi,phimax,pi1,pi2) := ( pi1 - pi2 ) / phimax * phi + pi2;
# Berechnung der phi-Koordinate des Schnittpunkts zwischen der Druckverhältnisgeraden (=p_out/p_in) und L_gas
defnumb intercept(Lminpi,Lminphi,p_in_min,p_in_max,Lmax,Leta,gasp,p_in,p_out) := 
(Lminphi * (gasp * Lmax * p_in ** 2 - gasp * Leta * Lmax * p_in ** 2 - 
   gasp * Lmax * p_in * p_in_max - Lminpi * p_in * p_in_max + 
   gasp * Lminpi * p_in * p_in_max + gasp * Leta * Lmax * p_in * p_in_min + 
   Lminpi * p_in * p_in_min - gasp * Lminpi * p_in * p_in_min + p_in_max * p_out -
    p_in_min * p_out))/(Lminpi * p_in * (-p_in_max + p_in_min));
# phi-Koordinate der Projektion von phi auf ulim
defnumb proje(Lminpi,Lminphi,pi1,pi2,phimax,phi,pi) := - ( ( - Lminpi * phi - Lminphi * pi + Lminphi * pi2 ) / ( Lminpi * phimax + Lminphi * pi1 - Lminphi * pi2 ) ) * phimax;
# Berechnung des neuen phi. Ggf. mit Projektion
defnumb phi_new(phi,phimin,phimax,pi1,pi2,Lminpi,Lminphi,p_in_min,p_in_max,Lmax,Leta,gasp,p_in,p_out) := if p_out / p_in > ulim(phi,phimax,pi1,pi2) then proje(Lminpi,Lminphi,pi1,pi2,phimax,phi,ulim(intercept(Lminpi,Lminphi,p_in_min,p_in_max,Lmax,Leta,gasp,p_in,p_out),phimax,pi1,pi2)) else min(max(intercept(Lminpi,Lminphi,p_in_min,p_in_max,Lmax,Leta,gasp,p_in,p_out),phimin),phimax) end;

# Kennfeld plotten
do forall <l,r> in CS do print "",
  "# __GNUPLOT__;",
  # encoding
  "set encoding iso_8859_1; ",
  #
  "set term pdfcairo enhanced font 'Calibri Light,10'; ",
  "set output 'CS_", l, "_", r, "_", iteration, ".pdf'; ",
  # title
  "set title '{/:Bold Verdichter ", l, " -> ", r, " (", iteration, ")}'; ", 
  # labels
  "set xlabel 'Fluss {/Symbol f}/m^3/s'; ",
  "set ylabel 'Druckverh\344ltnis {/Symbol p}/1'; ",
  #
  "plot [0:", phi_max[l,r]+1, "] ",
  # LINES
  # add l min line
  "[0:", L_max_pi[l,r] + 0.5, "] ",
  #"[0:", L_max_axis_intercept(L_max_pi[l,r], eta[l,r], p_i_min[l,r], p_i_max[l,r], var_node_p_old[l]) + 0.5, "] ",
  - L_min_pi[l,r] / L_min_phi[l,r], " * x + ",  L_min_pi[l,r],  " title 'L_{min}' lt 1 lw 2, ",
  # add l max line
  - L_min_pi[l,r] / L_min_phi[l,r], " * x + ", 
  L_max_axis_intercept(L_max_pi[l,r],eta[l,r],p_i_min[l,r],p_i_max[l,r],p_old(l)), 
  " title 'L_{max}' lt 1 lw 2, ",
  # add l gas line
  ( 1 - gas[l,r] ), 
  " * ( ", 
  ( - L_min_pi[l,r] / L_min_phi[l,r] ), 
  " * x + ", 
  L_min_pi[l,r], 
  " ) + ", 
  gas[l,r], 
  " * ( ", 
  ( - L_min_pi[l,r] / L_min_phi[l,r] ), 
  " * x + ", 
  L_max_axis_intercept(L_max_pi[l,r],eta[l,r],p_i_min[l,r],p_i_max[l,r],p_old(l)), 
  " )", 
  " dashtype 4 lt 3 title 'L_{gas}', ",
  # add pi 1 line
  pi_1[l,r], 
  " dashtype 3 lt 1 title '{/Symbol p}_1', ",
  # add Lmaxmax line
  ( - L_min_pi[l,r] / L_min_phi[l,r] ), 
  " * x + ", 
  L_max_axis_intercept(L_max_pi[l,r],eta[l,r],p_i_min[l,r],p_i_max[l,r],p_i_min[l,r]), 
  " dashtype 3 lt 1 lw 1 title 'L_{MAX}', ",
  # add ulim line
  ( pi_1[l,r] - pi_2[l,r] ) / phi_max[l,r], 
  " * x + ", 
  pi_2[l,r], 
  " lt 1 lw 2 title 'ulim', ",
  # add var_node_p_old[r] / var_node_p_old[l] line
  p_old(r) / p_old(l),
  " dashtype 4 lt 3 title 'p_{out} / p_{in}'; ",
  # add phi_min line
  "set arrow from ", phi_min[l,r], ",0 to ", phi_min[l,r], ",", pi_2[l,r] * 2, " nohead dashtype 2 lc rgb 'black'; ",
  # add phi_max line
  "set arrow from ", phi_max[l,r], ",0 to ", phi_max[l,r], ",", pi_2[l,r], " nohead dashtype 2 lc rgb 'black'; ",
  
  # TICKS
  # add L_max_axis_intercept value as a tic
  " set ytics add ( ", 
  " 'L_{max\_axis\_int}(", round(10 * p_old(l)) / 10, ")' ",
  L_max_axis_intercept(L_max_pi[l,r],eta[l,r],p_i_min[l,r],p_i_max[l,r],p_old(l)),
  " );",
  # add pi_2 value as a tic
  " set ytics add ( ", 
  " '{/Symbol p}_2' ",
  pi_2[l,r],
  " );",
  # add pi_1 value as a tic
  " set ytics add ( ", 
  " '{/Symbol p}_1' ",
  pi_1[l,r],
  " );",
  # add L_min_pi value as a tic
  " set ytics add ( ", 
  " 'L_{/Symbol p}_{\_min}' ",
  L_min_pi[l,r],
  " );",
  # add phi_min value as a tic
  " set xtics add ( ", 
  " '{/Symbol f}_{min}' ",
  phi_min[l,r],
  " );",
  # add phi_max value as a tic
  " set xtics add ( ", 
  " '{/Symbol f}_{max}' ",
  phi_max[l,r],
  " );",
  # add L_phi_min value as a tic
  " set xtics add ( ", 
  " 'L_{/Symbol f}_{\_min}' ",
  L_min_phi[l,r],
  " );",
  
  # POINTS
  # add interception point
  " set label at ", 
  intercept(L_min_pi[l,r],L_min_phi[l,r],p_i_min[l,r],p_i_max[l,r],L_max_pi[l,r],eta[l,r],gas[l,r],p_old(l),p_old(r)),
  #intercept(Lminpi,       Lminphi,       p_in_min,    p_in_max,    Lmax,        Leta,     gasp,    p_in,             p_out)
  ",", 
  (p_old(r) / p_old(l)), 
  " '' point pointtype 7 pointsize 1; ",
  
  # MISC
  # output
  "set output 'CS_", l, "_", r, "_", iteration, ".pdf'; ",
  "replot;";

# Model
# Inner node variables
var var_node_p[NO] >= 1.01325 <= 151.01325;
var var_node_Qo_in[NO] >= -10000 <= 10000;
# Pipe variables
var var_pipe_Qo_in[P] >= -10000 <= 10000;
var var_pipe_Qo_out[P] >= -10000 <= 10000;
# Boundary node variables
var var_boundary_node_flow_slack_positive[X];
var var_boundary_node_flow_slack_negative[X];
var var_boundary_node_pressure_slack_positive[E];
var var_boundary_node_pressure_slack_negative[E];
# Non pipe connections variables
var var_non_pipe_Qo[CN without P] >= -10000 <= 10000;
# Flap trap variables
var flaptrap[FT] binary;
# Auxilary variables
# v * Q for pressure drop (for pipes and resistors)
var vQp[P] >= -infinity; #:= ( vi(l,r) * var_pipe_Qo_in[l,r] + vo(l,r) * var_pipe_Qo_out[l,r] ) * rho / 3.6;
var vQr[RE] >= -infinity; #:= vm(l,r) * var_non_pipe_Qo[l,r] * rho / 3.6;
# factors for pressure drop for pipes ...
defnumb xip(i,o) := lambda(D[i,o], k[i,o]) * L[i,o] / ( 4 * D[i,o] * A(D[i,o]) );
# ... and resistors
defnumb xir(i,o) := zeta[i,o] / ( 2 * A(D[i,o]) ); # * b2p); # scaling with b2p for nicer zeta range
# pressure difference p_out minus p_in
var delta_p[CN] >= -Mp <= Mp; #:= var_node_p[l] - var_node_p[r];

# Auxiliary variables to track dispatcher agent decisions
var va_DA[VA];
var zeta_DA[RE];
var gas_DA[CS];
var compressor_DA[CS];
# Auxiliary variables to track trader agent decisions
var exit_nom_TA[X] >= - infinity <= 0;
var entry_nom_TA[S] >= 0 <= infinity;
# Auxiliary variable to track deviation from nominations
var nom_entry_slack_DA[S] >= -infinity;
var nom_exit_slack_DA[X] >= - infinity;
# Auxiliary variable to track balances
var scenario_balance_TA >= - infinity;
# Auxiliary variable to track pressure violations
var ub_pressure_violation_DA[NO] >= - infinity;
var lb_pressure_violation_DA[NO] >= - infinity;

#########
# PRINT #
#########
#do forall <v> in NO do print "var_node_p_old[", v, "] = ", var_node_p_old[v];
#do forall <l,r> in P do print "z[", l, ",", r, "] = ", zm(var_node_p_old[l],var_node_p_old[r]), " ", z(var_node_p_old[l],Tm), " ", z(var_node_p_old[r],Tm), " ", abs((z(var_node_p_old[l],Tm) - z(var_node_p_old[r],Tm))/zm(var_node_p_old[l],var_node_p_old[r]) * 100), " %";
#do forall <l,r> in P do print "A(D[", l, ",", r, "]) = ", A(D[l,r]);
#do forall <l,r> in P do print "2 Rs Tm zm = ", 2 * Rs * Tm * zm(var_node_p_old[l],var_node_p_old[r]), ", dt = ", dt, ", 2 Rs Tm zm dt / ( A(D[", l, ",", r, "]) * L[", l, ",", r, "] ) = ", 2 * Rs * Tm * zm(var_node_p_old[l],var_node_p_old[r]) * dt / ( A(D[l,r]) * L[l,r] );
#do forall <l,r> in RE do print "csv;<", l, ", ", r, ">;", ";", var_non_pipe_Qo_old[l,r], ";", var_non_pipe_Qo_old_old[l,r], ";", q_old(l,r);


minimize obj: sum <b> in X: (var_boundary_node_flow_slack_negative[b] + var_boundary_node_flow_slack_positive[b]) + 10 * sum <b> in E: (var_boundary_node_pressure_slack_negative[b] + var_boundary_node_pressure_slack_positive[b]);

### auxilary constraints
# v * Q for pressure drop (for pipes and resistors)
subto vxQp:
      forall <l,r> in P: vQp[l,r] == ( vi(l,r) * var_pipe_Qo_in[l,r] + vo(l,r) * var_pipe_Qo_out[l,r] ) * rho / 3.6;

subto vxQr:
      forall <l,r> in RE: vQr[l,r] == vm(l,r) * var_non_pipe_Qo[l,r] * rho / 3.6;

# constraints to track trader agent's decisions
subto nomx:
      forall <x> in X: exit_nom_TA[x] == exit_nom[x];

subto nome:
      forall <l,r> in S: entry_nom_TA[l,r] == entry_nom[l,r];

# constraints to track dispatcher agent's decisions
subto va_mode:
      forall <l,r> in VA: va_DA[l,r] == va[l,r];

subto re_drag:
      forall <l,r> in RE: zeta_DA[l,r] == zeta[l,r];

subto cs_fuel:
      forall <l,r> in CS: gas_DA[l,r] == gas[l,r];

subto cs_mode:
      forall <l,r> in CS: compressor_DA[l,r] == compressor[l,r];


# pressure difference p_out minus p_in
subto dp:
      forall <l,r> in CN: delta_p[l,r] == var_node_p[l] - var_node_p[r];

### node and pipe model ###

# forall nodes: connection_inflow - connection_outflow = node_inflow
subto c_e_cons_conserv_Qo:
      forall <n> in NO: var_node_Qo_in[n] - sum <n,i> in P: var_pipe_Qo_in[n,i] + sum <i,n> in P: var_pipe_Qo_out[i,n] - sum <n,i> in CN without P: var_non_pipe_Qo[n,i] + sum <i,n> in CN without P: var_non_pipe_Qo[i,n] == 0;

# forall inner nodes: node_inflow = 0
subto null_setzen:
      forall <n> in N: var_node_Qo_in[n] == 0;

# flow slack for boundary nodes
subto c_u_cons_boundary_node_wflow_slack_1:
      forall <x> in X: - var_boundary_node_flow_slack_positive[x] + var_node_Qo_in[x] <= + exit_nom[x];

subto c_u_cons_boundary_node_wflow_slack_2:
      forall <x> in X: - var_boundary_node_flow_slack_negative[x] - var_node_Qo_in[x] <= - exit_nom[x];

# pressure slack for boundary nodes
subto c_u_cons_boundary_node_wpressure_slack_1:
      forall <e> in E: - var_boundary_node_pressure_slack_positive[e] + var_node_p[e] <= + pressure[e];

subto c_u_cons_boundary_node_wpressure_slack_2:
      forall <e> in E: - var_boundary_node_pressure_slack_negative[e] - var_node_p[e] <= - pressure[e];

# continuity equation
subto c_e_cons_pipe_continuity: forall <l,r> in P:
      b2p * ( var_node_p[l] + var_node_p[r] - p_old(l) - p_old(r) ) + rho / 3.6 * ( 2 * rtza(l,r) * dt ) / L[l,r] * ( var_pipe_Qo_out[l,r] - var_pipe_Qo_in[l,r] ) == 0; # Felix bar -> Pa und 1000 m³/h -> kg/s --> rho / 3.6

# pressure drop equation
subto c_e_cons_pipe_momentum: forall <l,r> in P:
      b2p * delta_p[l,r] == xip(l, r) * vQp[l,r];


### valve model ###

subto valve_eq_one: forall <l,r> in VA:
      var_node_p[l] - var_node_p[r] <= Mp * ( 1 - va[l,r] ); # Eq. (10) station model paper

subto valve_eq_two: forall <l,r> in VA:
      var_node_p[l] - var_node_p[r] >= - Mp * ( 1 - va[l,r] ); # Eq. (11) station model paper

subto valve_eq_three: forall <l,r> in VA:
      var_non_pipe_Qo[l,r] <= Mq * va[l,r]; # Eq. (12) station model paper

subto valve_eq_four: forall <l,r> in VA:
      var_non_pipe_Qo[l,r] >= - Mq * va[l,r]; # Eq. (13) station model paper

### resistor model ###
# pressure drop equation
subto resistor_eq: forall <l,r> in RE:
      b2p * delta_p[l,r] == xir(l,r) * vQr[l,r];

### flap trap model ###

subto flap_trap_eq_one: forall <l,r> in FT:
      var_non_pipe_Qo[l,r] >= 0;

subto flap_trap_eq_two: forall <l,r> in FT:
      var_non_pipe_Qo[l,r] <= Mq * flaptrap[l,r];

subto flap_trap_eq_three: forall <l,r> in FT:
      delta_p[l,r] <= Mp * (1 - flaptrap[l,r] ) + 0.2 * b2p;

subto flap_trap_eq_four: forall <l,r> in FT:
      - delta_p[l,r] <= Mp * (1 - flaptrap[l,r] );

subto flap_trap_eq_five: forall <l,r> in FT:
      delta_p[l,r] <= 0;

### compressor model ###
subto compressor_eq_one: forall <l,r> in CS:
      var_non_pipe_Qo[l,r] >= 0;

subto compressor_eq_two: forall <l,r> in CS:
      var_non_pipe_Qo[l,r] == compressor[l,r] * 3.6 * p_old(l) * phi_new(q_old(l,r) / ( 3.6 * p_old(l) ),phi_min[l,r],phi_max[l,r],pi_1[l,r],pi_2[l,r],L_min_pi[l,r],L_min_phi[l,r],p_i_min[l,r],p_i_max[l,r],L_max(L_min_pi[l,r],L_min_phi[l,r],L_max_pi[l,r],eta[l,r],p_i_min[l,r],p_i_max[l,r],q_old(l,r)  / ( 3.6 * p_old(l) ),L_min_pi[l,r]),eta[l,r],gas[l,r],p_old(l),p_old(r));

### Entrymodellierung ###
subto entry_flow_model:
      forall <e> in E: var_node_Qo_in[e] <= entry_flow_bound[e];

subto nomination_check:
      forall <l,r> in S: var_pipe_Qo_out[l,r] + nom_entry_slack_DA[l,r] == entry_nom[l,r];

subto track_scenario_balance:
      sum <l,r> in S: entry_nom[l,r] + sum <x> in X: exit_nom[x] == scenario_balance_TA;

subto track_exit_nomination_slack:
      forall <x> in X: nom_exit_slack_DA[x] == var_boundary_node_flow_slack_positive[x] - var_boundary_node_flow_slack_negative[x];

subto track_ub_pressure_violation:
      forall <n> in NO: var_node_p[n] - pressureLimitsUpper[n] == ub_pressure_violation_DA[n];

subto track_lb_pressure_violation:
      forall <n> in NO: pressureLimitsLower[n] - var_node_p[n] == lb_pressure_violation_DA[n];
