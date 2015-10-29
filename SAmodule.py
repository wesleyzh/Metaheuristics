import math
import random
import DSSPmodule as DSSP 
import time
#Simulated Annealing combined with DSSPmodule
#Inputs: -------------------------------
# m = GUROBI model -- specifically a linear relaxation of the Fixed Cost Network Flow problem
# maxIter = maximum number of iterations for updating temperature
# dwell = number of times to look for neighbors at a given temperature
# p: parameter to modify DSSP algorithm
# arcs = set of arcs (i,j) in the network model; data type: tuple
# varcost: dictionary of variable costs for each commodity k on arc (i,j); denoted mathematically: c_ijk
# fixedcost: dictionary of fixed costs for each arc (i,j); denoted mathematically: f_ij
# totalSupply: dictionary of total supply of commodity k in the network, denoted mathematically: M_k
# K: the number of commodities in the network (NOTE: up until now all work has K = 1)
# flow: dictionary of GUROBI model variables which represent the flow of commodity k on arc (i,j); denoted mathematically: x_ijk
# switch: choose the schedule of SA: switch=1 boltzman; switch=2 Cauchy; switch=3 very fast anealing

#Outputs: ------------------------------
# iterations: total iterations completed
# pBest: best p value found
# bestObj: best objective value found

#updating temperature
def Update_Tem(T0, itval, switch):
    
    quench = 1.0   #default value
    n = 1.0        #default value
    if switch == 1:
        T = T0 / math.log(1+itval)
    elif switch == 2:
        T = T0 / (1 + itval)
    elif switch == 3:
        c = n * math.exp(-n * quench)
        T = T0 * math.exp(-c * itval**quench)        
    return T

def sign(x):  #define sign function, python only have copysign
    if x > 0:
        y = 1
    elif x == 0:
        y = 0
    elif x < 0:
        y = -1
    return y

#choose neighbors
def Choose_neighbors(T,learn_rate,p,switch):
    if switch == 1:    
        std = min(math.sqrt(T), 1 / 3.0 / learn_rate)
        xc = random.normalvariate(0, 1.0)
        neighborp = p + xc*std*learn_rate
    elif switch == 2:
        u = random.uniform(-1.0,1.0)*math.pi
        xc = learn_rate*T*math.atan(u)
        neighborp = p + xc
    elif switch ==3:
        u = random.uniform(0,1)
        y = sign(u - 0.5) * T * ((1 + 1/T)**abs(2*u - 1) - 1.0)
        xc = y * 1.0
        neighborp = p + xc
        
    if neighborp > 2:
        neighborp =  neighborp - 1
    elif neighborp <= 0:
        neighborp = abs(neighborp)         
    return neighborp

#main simulated annealing programe
def main(m, maxIter, max_time, T0, dwell, p, learn_rate, arcs, varcost, fixedcost, totSupply, K, flow, switch, nodeCnt):
   
    #solve the problem with original p
    t0 = time.clock()
    result = DSSP.DSSP (m, arcs, varcost, fixedcost, totSupply, K, flow, p)
    DSSPtime = time.clock()-t0
    iterations = result[0]
    gbestObj = result[2]
    pbest = p
    
    early_termin_cnt = 0   #count of iterations gbestObj is not improved
    gbestObj_track = gbestObj+1000   #initialize the gbestObj track    
    
    #define the total iteraions of search
    Iter = min(maxIter,int(max_time/DSSPtime)) 

    for itval in xrange(1,Iter+1):
        
        #check elapsed time
        #iteration_time = time.clock()                                   
        #elapsed_time = time.clock() - t0
        #if (elapsed_time > max_time): 
            #break               
        
        #early termination condition check
        if gbestObj_track == gbestObj:
            early_termin_cnt += 1
            if early_termin_cnt >= 30:
                break    #stop loop
        else: early_termin_cnt = 0
        gbestObj_track = gbestObj
        
        T = Update_Tem(T0,itval,switch) 

        for innerit in xrange(dwell):  #number of times to look for neighbors at a given temperature
            m.reset()  
            #choose a neighbor    
            neighborp = Choose_neighbors(T,learn_rate,p,switch)      
            
            result = DSSP.DSSP (m, arcs, varcost, fixedcost, totSupply, K, flow, neighborp) 
            
            iterations += result[0]
            
            #SA move rule
            if result[2] <= gbestObj:
                gbestObj = result[2]
                pbest = neighborp
                #p = neighborp
                break;                  #break out of inner loop
                
            else: 
                
                #f1 = (gbestObj - baseObjVal)/ baseObjVal
                #f2 = (result[2] - baseObjVal)/ baseObjVal
                #SAP = math.exp(-(f2-f1)/T)
                
                SAP = math.exp((gbestObj-result[2])/gbestObj/T)

                if random.random() < SAP:
                    p = neighborp
                    break;              #break out of inner loop

                        
                         
    SAresult=[iterations,pbest,gbestObj]    
    return SAresult