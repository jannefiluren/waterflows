# -*- coding: utf-8 -*-

"""
Python program for measureing the run time for GR4J model
"""

import numpy as np
from numba import jit
import time
import os

# Values of the S curve (cumulative HU curve) of
# GR unit hydrograph UH1

def SS1(I,C,D):
    FI = I
    if FI <= 0.0:
        SS1 = 0.0
    elif FI < C:
        SS1 = np.power(FI/C, D)
    else:
        SS1 = 1.0
    return SS1

# Values of the S curve (cumulative HU curve) of GR
# unit hydrograph UH2

def SS2(I,C,D):
    FI = I
    if FI <= 0.0:
        SS2 = 0.0
    elif FI <= C:
        SS2 = 0.5*np.power(FI/C, D)
    elif FI < 2.0*C:
        SS2 = 1.0-0.5*np.power(2.0-FI/C, D)
    else:
        SS2=1.0
    return SS2

# Computation of ordinates of GR unit hydrograph UH1
# using successive differences on the S curve SS1

def UH1(OrdUH1,C,D):
    NH = len(OrdUH1)
    for I in range(1, NH):
        OrdUH1[I-1] = SS1(I,C,D)-SS1(I-1,C,D)
    return
    
# Computation of ordinates of GR unit hydrograph UH2
# using successive differences on the S curve SS2

def UH2(OrdUH2,C,D):
    NH = len(OrdUH2)
    for I in range(1, NH):
        OrdUH2[I-1] = SS2(I,C,D)-SS2(I-1,C,D)
    return


@jit
def run_timestep(St, StUH1, StUH2, OrdUH1, OrdUH2, Param, P1, E):
    
    A = Param[0]
    B = 0.9
    
    # Interception and production store
            
    if P1 <= E:
        EN = E - P1
        PN = 0.0
        WS = EN / A
        if WS > 13.0:
            WS = 13.0
        TWS = np.tanh(WS)
        Sr = St[0] / A
        ER = St[0] * (2.0-Sr)*TWS/(1.0+(1.0-Sr)*TWS)
        AE = ER + P1
        St[0] = St[0] - ER
        PR = 0.0
    else:
        EN = 0.0
        AE = E
        PN = P1 - E
        WS = PN / A
        if WS > 13.0:
            WS = 13.0
        TWS = np.tanh(WS)
        Sr = St[0] / A
        PS = A*(1.0-Sr*Sr)*TWS/(1.0+Sr*TWS)
        PR = PN - PS
        St[0] = St[0] + PS
        
    # Percolation from production store
  
    if St[0] < 0.0:
        St[0] = 0.0
    
    Sr = St[0] / Param[0]
    Sr = Sr * Sr
    Sr = Sr * Sr
    PERC = St[0] * (1.0-1.0/np.sqrt(np.sqrt(1.0 + Sr/25.62891)))
    St[0] = St[0] - PERC
    PR = PR + PERC
    
    # Split of effective rainfall into the two routing components
  
    PRHU1 = PR * B
    PRHU2 = PR * (1.0-B)
    
    # Convolution of unit hydrograph UH1
  
    NH = len(OrdUH1)
    for K in range(0, NH-2):
        StUH1[K] = StUH1[K+1] + OrdUH1[K]*PRHU1
    StUH1[NH-1] = OrdUH1[NH-1] * PRHU1
    
    # Convolution of unit hydrograph UH2
  
    NH = len(OrdUH2)
    for K in range(0, NH-2):
        StUH2[K] = StUH2[K+1] + OrdUH2[K]*PRHU2
    StUH2[NH-1] = OrdUH2[NH-1] * PRHU2
         
    # Potential intercatchment semi-exchange
  
    Rr = St[1]/Param[2]
    EXCH = Param[1]*Rr*Rr*Rr*np.sqrt(Rr)
    
    # Routing store
    
    AEXCH1 = EXCH
    
    if (St[1]+StUH1[0]+EXCH) < 0.0:
        AEXCH1 = -St[1] - StUH1[0]
  
    St[1] = St[1] + StUH1[0] + EXCH
  
    if St[1] < 0.0:
        St[1] = 0.0
				
    Rr = (St[1]*St[1]*St[1]*St[1]) / (Param[2]*Param[2]*Param[2]*Param[2])
    
    #####Rr = np.power(St[1],4) / np.power(Param[2],4)
  
    QR = St[1] * (1.0-1.0/np.sqrt(np.sqrt(1.0+Rr)))    
  
    St[1] = St[1] - QR
  
    # Runoff from direct branch QD
  
    AEXCH2 = EXCH
  
    if ((StUH2[0]+EXCH) < 0.0):
        AEXCH2 = -StUH2[0]
    
    QD = np.maximum(0.0,StUH2[0]+EXCH)
    
    # Total runoff
  
    Q = QR + QD
  
    if (Q < 0.0):
        Q = 0.0
        
    return Q



# Run the GR4J model with initial states (St, StUH1,
# StUH2 , OrdUH1, OrdUH2), parameters (Param) for time
# series of inputs (P1, E)

@jit
def hydro_model(St, StUH1, StUH2, OrdUH1, OrdUH2, Param, P1, E, Q):
    
    for irun in range(0,100):
        
        # Initilize state variables
    
        St[0] = 0.3 * Param[0]
        St[1] = 0.5 * Param[2]
        
        for i in range(0,19):
            StUH1[i] = 0
        
        for i in range(0,39):
            StUH2[i] = 0
    
        for t in range(0, len(P1)):
            
            Q[t] = run_timestep(St, StUH1, StUH2, OrdUH1, OrdUH2, Param, P1[t], E[t])
      
    return




os.chdir('C:\\Work\\Studies\\vann\\comp_time')



# Set parameter values

param = [257.238, 1.012, 88.235, 2.208]

D = 2.5

# Allocate state variables

n_ord = 20

st     = np.zeros(2)
st_uh1 = np.zeros(n_ord)
st_uh2 = np.zeros(2 * n_ord)

# Compute ordinates

ord_uh1 = np.zeros(n_ord)
ord_uh2 = np.zeros(2 * n_ord)

UH1(ord_uh1, param[3], D)
UH2(ord_uh2, param[3], D)

# Read inputs

data = np.genfromtxt('test_data.txt', delimiter="")

P1    = data[:,0]
E     = data[:,1]
q_ref = data[:,2]

# Allocate outputs

q_sim = np.zeros(len(P1))

# Measure execution time

hydro_model(st, st_uh1, st_uh2, ord_uh1, ord_uh2, param, P1, E, q_sim)

start_time = time.clock()

hydro_model(st, st_uh1, st_uh2, ord_uh1, ord_uh2, param, P1, E, q_sim)

print(time.clock() - start_time, "seconds")

# Compare against reference results

q_error = np.max(np.abs(q_sim - q_ref))

print("Maximum error = ", q_error)
