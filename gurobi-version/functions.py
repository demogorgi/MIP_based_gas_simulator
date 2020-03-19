# -*- coding: utf-8 -*-

# this file contains helper functions to model gas physics

import importlib
import sys
import re
wd = sys.argv[1].replace("/",".")
wd = re.sub(r'\.$', '', wd)

sc = importlib.import_module(wd + ".init_scenario")
no = importlib.import_module(wd + ".nodes")
co = importlib.import_module(wd + ".connections")

from constants import *
from math import *

# Mean values are used to stabilize simulation
def stabilizer(a, b):
    if a * b > 1:
        if a > 0:
            return sqrt(a * b)
        else:
            return -sqrt(a * b)
    else:
        return ( a + b ) / 2

# pressure stabilizer
def p_old(n):
    return stabilizer(sc.var_node_p_old[n], sc.var_node_p_old_old[n])
    
# flow stabilizer (non-pipes)
def q_old(non_pipe):
    return stabilizer(abs(sc.var_non_pipe_Qo_old[non_pipe]), abs(sc.var_non_pipe_Qo_old_old[non_pipe]))
    
# pipe inflow stabilizer
def q_in_old(pipe):
    return stabilizer(abs(sc.var_pipe_Qo_in_old[pipe]), abs(sc.var_pipe_Qo_in_old_old[pipe]))
    
# pipe outflow stabilizer
def q_out_old(pipe):
    return stabilizer(abs(sc.var_pipe_Qo_out_old[pipe]), abs(sc.var_pipe_Qo_out_old_old[pipe]))

# reduced pressure (2.4 Forne)
def pr(p):
    return p / pc
    
# reduced Temperature (2.4 Forne)
def Tr(T):
    return T / Tc
    
# cross sectional area of a pipe in m²
def A(diam):
    return Pi * ( diam / 2 ) ** 2
    
# compressibility factor Papay (2.4 Forne) # Felix: "falsch im Forne-Buch; 0.274, nicht 0.247 muss es sein!"
def z(p,T):
    return 1 - 3.52 * pr(p) * exp(-2.26 * Tr(T)) + 0.274 * pr(p) ** 2 * exp(-1.878 * Tr(T))
    
# compressibility factor Papay (2.4 Forne)
def zm(pi,po):
    return ( z(pi,Tm) + z(po,Tm) ) / 2
    
# Nikuradze (2.19 Forne), diameter diam in m, integral roughness rough in m
def lamb(diam, rough):
    return ( 2 * log(diam/rough) + 1.138 ) ** -2
    
# Rs * Tm * zm / A
def rtza(i,o):
    return Rs * Tm * zm(p_old(i),p_old(o)) / A(co.diameter[(i,o)])
    
# Inflow velocity
def vi(i,o):
    return rtza(i,o) * rho / 3.6 * q_in_old((i,o)) / ( b2p * p_old(i) )
    
# Outflow velocity
def vo(i,o):
    return rtza(i,o) * rho / 3.6 * q_out_old((i,o)) / ( b2p * p_old(o) )

# Function for resistor model
def vm(i,o):
    return rho / 3.6 * ( rtza(i,o) * q_old((i,o)) ) / 2 * 1 / b2p * ( 1 / p_old(i) + 1 / p_old(o) )

# Functions for compressor model
#
def L_min(L_min_pi,L_min_phi,phi):
    return - L_min_pi / L_min_phi * phi + L_min_pi

# Achsenabschnitt der Maximalleistung als Funktion vom Eingangsdruck. Quasi "Maximale Max-Leistung"
def L_max_axis_intercept(L_max,L_eta,p_i_min,p_i_max,p_in):
    return L_max * ( L_eta - 1 ) / ( p_i_max - p_i_min ) * ( p_in - p_i_min ) + L_max

# Maximalleistung als Funktion vom Fluss unter Verwendung des Achsenabschnitts. Die Steigung erhalten wir aus der Parametrierung der Minimalleistung.
def L_max(L_min_pi,L_min_phi,L_max,L_eta,p_i_min,p_i_max,phi,p_in):
    return - L_min_pi / L_min_phi * phi + L_max_axis_intercept(L_max,L_eta,p_i_min,p_i_max,p_in)

# Leistung als Funktion des "Gaspedals" zwischen 0% und 100%
def L_gas(L_min_pi,L_min_phi,phi,gas):
    return ( 1 - gas ) * L_min(L_min_pi,L_min_phi,phi) + gas * L_max(L_min_pi,L_min_phi,L_max,L_eta,p_i_min,p_i_max,phi,p_in)

# pi_2: Geradengleichung mit den Punkten (0,pi_2) und (phi_max,pi_1)
def ulim(phi,phi_max,pi_1,pi_2):
    return ( pi_1 - pi_2 ) / phi_max * phi + pi_2

# Berechnung der phi-Koordinate des Schnittpunkts zwischen der Druckverhältnisgeraden (=p_out/p_in) und L_gas
def intercept(L_min_pi,L_min_phi,p_i_min,p_i_max,L_max,L_eta,gas,p_in,p_out):
    return (L_min_phi * (gas * L_max * p_in ** 2 - gas * L_eta * L_max * p_in ** 2 - 
   gas * L_max * p_in * p_i_max - L_min_pi * p_in * p_i_max + 
   gas * L_min_pi * p_in * p_i_max + gas * L_eta * L_max * p_in * p_i_min + 
   L_min_pi * p_in * p_i_min - gas * L_min_pi * p_in * p_i_min + p_i_max * p_out -
    p_i_min * p_out))/(L_min_pi * p_in * (-p_i_max + p_i_min))

# phi-Koordinate der Projektion von phi auf ulim
def proje(L_min_pi,L_min_phi,pi_1,pi_2,phi_max,phi,pi):
    return - ( ( - L_min_pi * phi - L_min_phi * pi + L_min_phi * pi_2 ) / ( L_min_pi * phi_max + L_min_phi * pi_1 - L_min_phi * pi_2 ) ) * phi_max

# Berechnung des neuen phi. ggf. mit Projektion
def phi_new(phi,phi_min,phi_max,pi_1,pi_2,L_min_pi,L_min_phi,p_i_min,p_i_max,L_max,L_eta,gas,p_in,p_out):
    return proje(L_min_pi,L_min_phi,pi_1,pi_2,phi_max,phi,ulim(intercept(L_min_pi,L_min_phi,p_i_min,p_i_max,L_max,L_eta,gas,p_in,p_out),phi_max,pi_1,pi_2)) if (p_out / p_in) > ulim(phi, phi_max, pi_1, pi_2) else min(max(intercept(L_min_pi,L_min_phi,p_i_min,p_i_max,L_max,L_eta,gas,p_in,p_out),phi_min),phi_max)

# factors for pressure drop for pipes ...
def xip(i):
    return lamb(co.diameter[i], co.roughness[i]) * co.length[i] / ( 4 * co.diameter[i] * A(co.diameter[i]) )

# ... and resistors
def xir(i,zeta):
    return zeta / ( 2 * A(co.diameter[i]) );
    #return agent_decisions["zeta"]["RE"][joiner(i)] / ( 2 * A(co.diameter[i]) );
