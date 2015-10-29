import PSODSSP
import TSDSSP
import SADSSP

#FCNF setting
nodeCntlist = [10]
supplyPct =0.2
demandPct = 0.2
rhsMin = 1000
rhsMax = 2000
cMin = 0 
cMax = 20
fMin = 20000
fMax = 60000
K = 1 

#Genral seting
p = 1.0
maxIter = 100         #max DSSP iterations
max_time = 3600       #max time of search
numseed = 3           #seed start from 1 to numseed

#PSO setting
pmin = 0.0            #initial pMin
pmax = 2.0            #initial pMin
noP = 10               #number of particles

#TS setting
e = 0.05              #e/2 is the farthest distance of neighbor
tabulength = 5        #length of tabu list
neighbors = 3         #size of neighborhoods

#SA setting
switchlist = [1,3]  #switch=1 boltzman; switch=2 Cauchy; switch=3 very fast anealing
dwell = 3           #max number of times to look for moves at a given temperature
learn_rate = 0.5    
T = T0 = .25        #initial temperature

#setting finished-----------------------------------------------------------------------------------------------------------------------
PSODSSP.main(nodeCntlist, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, maxIter, max_time, numseed, pmin, pmax, noP)

TSDSSP.main(nodeCntlist, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, maxIter, max_time, numseed, p, e, tabulength, neighbors)

SADSSP.main(nodeCntlist, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, maxIter, max_time, numseed, p, dwell, learn_rate, T, T0, switchlist)




