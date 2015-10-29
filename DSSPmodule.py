from gurobipy import *

#Dynamic Slope Scaling Procedure (Kim and Pardolos 1999) 
#Python Implementation: Charles Nicholson, 2013

#Inputs: -------------------------------
# m = GUROBI model -- specifically a linear relaxation of the Fixed Cost Network Flow problem
# arcs = set of arcs (i,j) in the network model; data type: tuple
# varcost: dictionary of variable costs for each commodity k on arc (i,j); denoted mathematically: c_ijk
# fixedcost: dictionary of fixed costs for each arc (i,j); denoted mathematically: f_ij
# totalSupply: dictionary of total supply of commodity k in the network, denoted mathematically: M_k
# K: the number of commodities in the network (NOTE: up until now all work has K = 1)
# flow: dictionary of GUROBI model variables which represent the flow of commodity k on arc (i,j); denoted mathematically: x_ijk
# p: parameter to modify DSSP algorithm

#Outputs: ------------------------------
# t: total iterations completed
# bestObj: best objective value found

def DSSP (m, arcs, varcost, fixedcost, totSupply, K, flow, p):
          
    Change = True    #used to determine if DSSP loop should continue -- specifically: has there been any changes to the solution vector
    y={}             #binary value for each arc (i,j) -- used to calculate true objective cost of the solution (not used as a model variable)
    t= 0             #keeps track of total iterations
    pbest = -1
    
    bestObj = float("infinity")   #stores the best objective value found
    
    tempSolution = {} # used for defining stopping condition   
    
    #initialize the cost coeffecients
    #using initialization "Type II" from Kim and Pardolos 1999
    #since the arcs are uncapacitated, use a sufficient upper bound on flow: in this case, the total supply in the network, M_k
    #intial linearized cost: d_ijk = c_ijk + p*f_ij / M_k
    
    for k in xrange(K):
        for i,j in arcs:
            flow[i,j,k].Obj = varcost[i,j,k] + p*fixedcost[i,j]/totSupply[k]   
            tempSolution[i,j,k] = -1
        
    while Change == True:        
            
        t += 1            #increment iteration count
            
        m.optimize()      #call GUROBI to solve the model   
            
        solution = m.getAttr('x', flow)  # the solution vector, x_ijk
        
        for i,j in arcs:
            if quicksum(solution[i,j,k] for k in xrange(K)) > 0.00001:         #if there is positive flow on arc (i,j), 
                y[i,j] = 1                                                     #  set y_ij = 1 
            else:                                                                
                y[i,j] = 0                                                     #  otherwise, set y_ij = 0
             
        Change = False
        ObjectiveVal = 0     
        for k in xrange(K):
            ObjectiveVal = ObjectiveVal + quicksum(varcost[i,j,k]*solution[i,j,k] + fixedcost[i,j]*y[i,j] for i,j in arcs)  #calculate the true objective cost
                
        if ObjectiveVal < bestObj:        #store the best objective found so far                                       
            bestObj = ObjectiveVal             
            pbest = p
                
        
        #evaluate the arc flow from the solution to update the linearized cost function
        for (i,j) in arcs:                 
            
            
            if solution[i,j,k] <> tempSolution[i,j,k]:    # if any update occurs, continue with DSSP
                Change = True
            
            if solution[i,j,k] > 0.00001:         #for every arc with flow in the solution,                          
                    
                if flow[i,j,k].Obj <> (varcost[i,j,k] + p*fixedcost[i,j]/solution[i,j,k]):    # if the cost coefficient should be updated,
                    flow[i,j,k].Obj =  varcost[i,j,k] + p*fixedcost[i,j]/solution[i,j,k]      # update: d_ijk = c_ijk + f_ij / x_ijk
                                                                         
        tempSolution = m.getAttr('x', flow) 
                
    presult = [t, pbest, bestObj]   #list of total iterations used, best "p" value, and best objective found 
    return presult                  #return the list