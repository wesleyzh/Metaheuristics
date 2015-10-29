import math
import random
import DSSPmodule as DSSP 
import time
#Tabu Search combined with DSSPmodule
#Inputs: -------------------------------
# m = GUROBI model -- specifically a linear relaxation of the Fixed Cost Network Flow problem
# maxIter = maximum number of iterations for tabu search
# p: parameter to modify DSSP algorithm
# tabulength = length of tabu list
# neighbors = number of neighbors search
# arcs = set of arcs (i,j) in the network model; data type: tuple
# varcost: dictionary of variable costs for each commodity k on arc (i,j); denoted mathematically: c_ijk
# fixedcost: dictionary of fixed costs for each arc (i,j); denoted mathematically: f_ij
# totalSupply: dictionary of total supply of commodity k in the network, denoted mathematically: M_k
# K: the number of commodities in the network (NOTE: up until now all work has K = 1)
# flow: dictionary of GUROBI model variables which represent the flow of commodity k on arc (i,j); denoted mathematically: x_ijk
# e: e/2 is the farthest distance of neighbor

#Outputs: ------------------------------
# iterations: total iterations completed
# pbest: best p value found
# gbestObj: best objective value found

def Choose_neighbors(p,neighbors, e):
    neighborslist = []
    #add neighbors into list
    for i in xrange(neighbors):
        temp = p+random.uniform(-e/2,e/2)   #look for neighbor, e/2 is the farthest distance of neighbor
        
        #compare with pmin and pmax
        if temp > 2:
            temp =  temp - 1
        elif temp <= 0:
            temp = abs(temp)         

        neighborslist.append(temp)
        
    return neighborslist

def update_tabulist(a,b):
    a.remove(a[0])
    a.append(b)
    return a

def main (m, maxIter, max_time, p, tabulength, neighbors, arcs, varcost, fixedcost, totSupply, K, flow, e,nodeCnt):
    
    #solve the problem with original p
    t0 = time.clock()
    result = DSSP.DSSP (m, arcs, varcost, fixedcost, totSupply, K, flow, p)
    DSSPtime = time.clock()-t0
    iterations = result[0]
    gbestObj = result[2]
    pbest = p
    curp = p 
    
    long_term_memory = {curp:0} #creat long-term memory 
    long_term_max = 2           #define the max frequency of long_term memory    
    
    early_termin_cnt = 0   #count of iterations gbestObj is not improved
    gbestObj_track = gbestObj+1000   #initialize the gbestObj track
    
    #initialize tabu list with pbest
    tabulist=[]
    for i in xrange(0,tabulength):
        tabulist.append(pbest)
    
    #define the total iteraions of search
    DSSPIter = min(maxIter,int(max_time/DSSPtime))
    Iter = int(DSSPIter/neighbors)
    
    for i in xrange(0,Iter):
        
        ##check elapsed time
        #iteration_time = time.clock()                                   
        #elapsed_time = time.clock() - t0
        #if (elapsed_time > max_time): 
            #break            
        
        #early termination condition check
        if gbestObj_track == gbestObj:
            early_termin_cnt += 1
            if early_termin_cnt >= 10:
                break    #stop loop
        else: early_termin_cnt = 0
                
        gbestObj_track = gbestObj        

        neighborlist = Choose_neighbors(curp,neighbors, e)  #choose neighborhoods around current p
        
        candidate = []
        candidate_obj = []                
        #caculate the objective value of element in neighborlist
        for n in xrange(0,len(neighborlist)):
            flag = True
            for t in xrange(0,tabulength):
                flag = flag&(abs(tabulist[t]-neighborlist[n])>0.001) #check the tabustates of neighborlist
          
            if flag:
                m.reset()
                result = DSSP.DSSP (m, arcs, varcost, fixedcost, totSupply, K, flow, neighborlist[n])
                iterations += result[0]
                candidate.append(result[1])
                candidate_obj.append(result[2])
        
        #find the best from candidate_obj and get its p value        
        bestcandidate = min(candidate_obj)
        index = candidate_obj.index(bestcandidate)
        curp = candidate[index]
        
        #compare with best so far  
        if bestcandidate <= gbestObj:
            gbestObj=bestcandidate
            pbest = curp
  
        #update short tabu list with FIFO rule whatever curp is better then best so far
        tabulist = update_tabulist(tabulist,curp)
        
        #long term memory based on frequency of short-term memory
        #difference<0.1, was regarded same p and recoreded in the long term memory
        for pre_curp in long_term_memory.keys():
            if abs(curp-pre_curp) <= 0.01:
                long_term_memory[pre_curp] += 1
                if long_term_memory[pre_curp] >= long_term_max and bestcandidate >= gbestObj:
                    curp = random.random()*(2-0)
            else:
                long_term_memory.update({curp:1})
                
    TSresult=[iterations,pbest,gbestObj]    
    return TSresult