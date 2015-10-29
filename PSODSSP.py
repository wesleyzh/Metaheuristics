

#FCNF Varying Cost Model
#simulated annealing using the scipy inspired implementation (12/5/2013)

from __future__ import division
import operator
import time
from numpy import * 
import math
from gurobipy import *
import matplotlib.pyplot as plt
import random

#path = sys.path
#path.append('C:\Users\\nich8038\Documents\Research and Grants\Research\PythonModules')

import randFCNF as CN
import DSSPmodule as DSSP 
import PSOmodule as PSO


##FCNF setting
#nodeCntlist = [10]
#supplyPct =0.2
#demandPct = 0.2
#rhsMin = 1000
#rhsMax = 2000
#cMin = 0 
#cMax = 20
#fMin = 20000
#fMax = 60000
#K = 1 

##PSO settings
#pmin = 0.0        #initial pMin
#pmax = 2.0        #initial pMin
#maxIter = 500     #max iteration
#noP = 2           #number of particles
#max_time = 600    #max time of PSO search

def main(nodeCntlist, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, maxIter, max_time, numseed, pmin, pmax, noP):
    for nodeCnt in nodeCntlist:
    
        m = Model('GenFCNF')
        m.setParam( 'OutputFlag', 0 ) 
        #m.setParam( 'LogToConsole', 1 )
        m.params.timeLimit = 3600 
        #m.setParam( 'LogFile', "" ) 
        m.setParam('threads', 7)
        m.params.NodefileStart = 0.5
        
        arcs=[]
        decision = {}
        
        f = open('fDSSP PSO_{}_{}_{}_{}_{}_{}_{}.txt'.format(nodeCnt,cMin,cMax,fMin,fMax,noP,maxIter),'w')
        f.close()
        
        for seed in xrange(1,numseed+1):   
            m.reset()
            for v in m.getVars():
                m.remove(v)
            for c in m.getConstrs():
                m.remove(c)    
            
            random.seed(seed)
            
            arcs[:]=[]
            #generate the Fixed Charge Network Problem
            FCNFresult = CN.FCNFgenerator(seed, m, nodeCnt, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, arcs)
            arcs=tuplelist(arcs)
            noV = len(arcs)
            req = FCNFresult[0]
            flow = FCNFresult[1]
            varcost = FCNFresult[2]
            fixedcost = FCNFresult[3]
            totSupply = FCNFresult[4]  
            
            for k in xrange(K):
                totSupply[k] = 0
                for i in xrange(nodeCnt):
                    if req[i,k] > 0:
                        totSupply[k] = totSupply[k] + req[i,k]
    
            TVC = time.clock() #record time for PSO
    
            #Particle Swarm Optimization  
            PSOresult = PSO.main(m, maxIter, max_time, noP, pmin, pmax, arcs, varcost, fixedcost, totSupply, K, flow, nodeCnt)
            iterations = PSOresult[0]
            pbest = PSOresult[1]     #best value of p
            gbestObj= PSOresult[2]
                       
            f = open('fDSSP PSO_{}_{}_{}_{}_{}_{}_{}.txt'.format(nodeCnt,cMin,cMax,fMin,fMax,noP,maxIter),'a')
            f.write('{},{},{},{},{}\n'.format(seed, iterations, time.clock() - TVC, pbest,gbestObj))
            f.close()    