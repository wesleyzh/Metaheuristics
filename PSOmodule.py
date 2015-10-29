import math
import random
from scipy import *
import DSSPmodule as DSSP 
import time
#Particle Swam Optimization combined with DSSPmodule
#Inputs: -------------------------------
# m = GUROBI model -- specifically a linear relaxation of the Fixed Cost Network Flow problem
# maxIter = maximum number of iterations for updating positions
# noP = number of particles
# pMin and pMax: min/max parameter to modify DSSP algorithm
# arcs = set of arcs (i,j) in the network model; data type: tuple
# varcost: dictionary of variable costs for each commodity k on arc (i,j); denoted mathematically: c_ijk
# fixedcost: dictionary of fixed costs for each arc (i,j); denoted mathematically: f_ij
# totalSupply: dictionary of total supply of commodity k in the network, denoted mathematically: M_k
# K: the number of commodities in the network (NOTE: up until now all work has K = 1)
# flow: dictionary of GUROBI model variables which represent the flow of commodity k on arc (i,j); denoted mathematically: x_ijk

#Outputs: ------------------------------
# iterations: total iterations completed
# global_best: best p value found
# global_best_score: best objective value found

def update_velocity(w, velocity, Vmax, particle_best, global_best, position):
    c1 = 2               #define c1
    c2 = 2               #define c2
    
    velocity = w*velocity+c1*random.random()*(particle_best-position)+c2*random.random()*(global_best-position)
                                                      
    if velocity > Vmax:
        velocity = Vmax
    elif velocity < -Vmax:
        velocity = -Vmax
        
    return velocity

def update_position(velocity,position):
    position  = position + velocity
    
    if position > 2:
        position = position -1
    elif position < 0:
        position = abs(position)
    
    return position

def main(m, maxIter, max_time, noP, pmin, pmax, arcs, varcost, fixedcost, totSupply, K, flow, nodeCnt):
    wMax = 0.9           #Max inertia weight
    wMin = 0.4           #Min inertia weight    
    Vmax = 1             #define Vmax
    position = zeros(noP)        #create particles positions array
    velocity = zeros(noP)        #create particles velocity array
    particle_best = zeros(noP)
    particle_best_score = zeros(noP)
    iterations = 0
    
    #initialize position, velocity, particle best position and score
    for p in range(0,noP):
        position[p] = random.uniform(pmin,pmax)
        velocity[p] = random.uniform(-Vmax,Vmax)
        particle_best[p] = position[p]
        particle_best_score[p] = float("infinity")
    
    t0 = time.clock()
    #initial run to determine DSSP time; use result to ensure PSO produces solution <= DSSP
    result = DSSP.DSSP(m, arcs, varcost, fixedcost, totSupply, K, flow, 1)   #note: psi = 1 here 
    DSSPtime = time.clock()-t0
    #initialize pratcile/global best position and score with p[0]
    particle_best[0] = result[0]
    global_best = result[0]
    particle_best_score[0] = result[2]
    global_best_score = result[2] #initial global best value as inf
        
    #t0 = time.clock() #start record time
    early_termin_cnt = 0   #count of iterations gbestObj is not improved
    gbestObj_track = -1   #initialize the gbestObj track   
    
    #define the total iteraions of search
    DSSPIter = min(maxIter,int(max_time/DSSPtime))
    Iter = int(DSSPIter/noP)
    
    #start search
    for itval in xrange(1,Iter+1):
        
        #check elapsed time
        #iteration_time = time.clock()                                   
        #elapsed_time = time.clock() - t0
        #if (elapsed_time > max_time): 
            #break
        
        #early termination condition check
        if gbestObj_track == global_best_score:
            early_termin_cnt += 1
            if early_termin_cnt >= 3:
                break    #stop loop
        else: early_termin_cnt = 0
        gbestObj_track = global_best_score        

        #update fitness for each particle
        for p in range(0,noP):
            m.reset()
            result = DSSP.DSSP(m, arcs, varcost, fixedcost, totSupply, K, flow, position[p])
            fitness = result[2]
            iterations += result[0]
            
            if fitness <= particle_best_score[p]: #compare the particle_best[p] with fitness
                particle_best_score[p] = fitness
                particle_best[p] = position[p]
                if fitness <= global_best_score:
                    global_best_score = fitness
                    global_best = position[p]
                
        w = wMax-itval*((wMax-wMin)/maxIter)
        for p in range (noP):
            velocity[p] = update_velocity(w, velocity[p], Vmax, particle_best[p], global_best, position[p])
            position[p] = update_position(velocity[p],position[p])
            
    PSOresult=[iterations,global_best,global_best_score]    
    return PSOresult
            
            