
#FCNF Varying Cost Model
#Tabu Search

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
import TSfinalmodule as TS


#FCNF setting
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

##TS settings
#p = 1.0   #it is terrible compared with PSO/SA, since better solution is 0.48,; when I set p=0.48, it can find better solution at 0.58. So p plays an important role in the performance 
#maxIter = 1000      #max iteration
#e = 0.05          #e/2 is the farthest distance of neighbor
#tabulength = 5    #length of tabu list
#neighbors = 10    #size of neighborhoods
#max_time = 600    #max time of TS

def main(nodeCntlist, supplyPct, demandPct, rhsMin, rhsMax, cMin, cMax, fMin, fMax, K, maxIter, max_time, numseed, p, e, tabulength, neighbors):
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
        
        f = open('fDSSP TS_{}_{}_{}_{}_{}_{}_{}.txt'.format(nodeCnt,cMin,cMax,fMin,fMax,tabulength,maxIter),'w')
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
            
            #for k in xrange(K):
                #totSupply[k] = 0
                #for i in xrange(nodeCnt):
                    #if req[i,k] > 0:
                        #totSupply[k] = totSupply[k] + req[i,k]
    
            TVC = time.clock() #record time for TS
    
            #Tabu Search
            TSresult = TS.main(m, maxIter, max_time, p, tabulength, neighbors, arcs, varcost, fixedcost, totSupply, K, flow, e, nodeCnt)
            iterations = TSresult[0]
            pbest = TSresult[1]     #best value of p
            gbestObj= TSresult[2]
                       
            f = open('fDSSP TS_{}_{}_{}_{}_{}_{}_{}.txt'.format(nodeCnt,cMin,cMax,fMin,fMax,tabulength,maxIter),'a')
            f.write('{},{},{},{},{}\n'.format(seed, iterations, time.clock() - TVC, pbest, gbestObj))
            f.close()    
        
    