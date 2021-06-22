# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 21:34:00 2020

@author: kevin
"""
import matplotlib.pyplot as plt
import pulp as pulp 
import scipy.stats as scipy

#Beginning_Supply = [283, 272, 94, 318, 160, 443, 246, 155, 74, 46, 160, 285, 639, 156] #Beginning supply in March 26th of hospital beds for region i where i = {14} that we need

Beginning_Supply = [399, 548, 148, 698, 252, 843, 378, 325, 122, 106, 296, 593, 893, 258]#Beginning supply in March 26th of hospital beds for region i where i = {14} that we need


#Weight of each region derived from the excel analysis 
Weight_Region=[ 0.106 ,	 0.096, 	 0.037 ,	 0.088 ,	 0.039 ,	 0.112 	, 0.083 , 0.035 	, 0.019 	, 0.009 ,	 0.052 	, 0.077 ,	 0.199 ,	 0.047 ]

#Projected Covid peak demand analysis derived from the excel
Projected_Covid_Max= 9984


N = 14 # number of regions

def simulatecovid():
    Final_Supply ={} #Supply of hospital beds for region i where i = {14} that we need 
    
    Beds_Sent= {} #Beds moved for region i where i = {14}
    
    Beds_Bought ={} #Beds bought for region i where i = {14}
    
    Demand_Covid={} #Covid demand dictionary that holds the demand of each region for this simulation
    demand= scipy.norm(Projected_Covid_Max,2000).rvs()    #simulating total covid demand
    for i in range (N):
        Demand_Covid[i] = demand* Weight_Region[i] # change demand to a % from excel 

    #Initialize LP Problem
    model = pulp.LpProblem("COVID Beds",pulp.LpMinimize)
    
    #Create decision variables
    for i in range (N):
         Final_Supply[i]=pulp.LpVariable("Supply for Hospital beds in region %s" %i, lowBound = 0, cat = "Integer")
         Beds_Bought[i]=pulp.LpVariable("Beds bought for region %s" %i, lowBound = 0, cat = "Integer")
         for j in range (N):
            Beds_Sent[i,j]=pulp.LpVariable("Beds sent from region %s to region %s" %(i,j), lowBound = 0, cat = "Integer") # region i gives a bed, region j recieves a bed 
        
    #Objective Function
    model +=pulp.lpSum(Final_Supply[i]-Demand_Covid[i] for i in range (N))
    
    
    #Constraints
    #Supply Formula
    for i in range (N):
        model += Final_Supply[i] == Beginning_Supply[i] + Beds_Bought[i] + pulp.lpSum(Beds_Sent[j,i] for j in range (N)) - pulp.lpSum(Beds_Sent[i,j] for j in range (N))
            
    #80% Constraints of supply
    for i in range (N):
        model += Final_Supply[i]>=Demand_Covid[i]*0.8
        
    #Constraint for Beds Sent
    for i in range (N):
        model += pulp.lpSum(Beds_Sent[i,j] for j in range (N))<=Beginning_Supply[i]*(0.2)
    
    Fin_Supply ={} #Supply of hospital beds for region i where i = {14} that we need 
    Bed_Sent= {} #Beds moved for region i where i = {14}
    Bed_Bought ={} #Beds bought for region i where i = {14}    
    
    #Solve our model
    model.solve()
    
    #create outputs that are values and not pulp variables 
    for i in range (N):
        Fin_Supply[i]=Final_Supply[i].varValue
        Bed_Bought[i]=Beds_Bought[i].varValue
        for j in range (N):
            Bed_Sent[i,j]=Beds_Sent[i,j].varValue
    # Return the objective and the beds bought, supplied, sent for each region and the demand in this scenario 
    return(pulp.value(model.objective), Bed_Bought, Fin_Supply, Bed_Sent, demand)

#figure out what the highest can be and what the lowest we tested 

Demand_Max=0 #Variable to hold the highest demand that is simulated
Demand_Min=100000 #Variable to hold the lowest demand that is simulated
All_Demand=[] #List that holds the variables for sum of all demand that is simulated 
trials = 10000 # number of trials
scenarios_beds_bought=0 #counter variable of scenarios where beds were bought
scenarios_beds_moved=0 #counter variable of scenarios where beds were moved 
scenarios_no_change=0 #counter variable of scenarios where no beds are bought or moved
total_region_bought={} #sum of all bought beds for region 
average_region_bought={} #dictionary variable for average of beds bought for a region 
total_region_given={} #sum of all given beds for a region
average_region_given={} #dictionary variable for average of given beds for a region
total_region_received={} #sum of all received beds for a region 
average_region_received={}#Dictionary variable for average of received beds for a region
region_bought = {} 
region_received ={}
region_gave={}
scenarios_region_bought = {}
scenarios_region_received ={}
scenarios_region_gave={}
#delcaring variables
for i in range (N):
    region_bought[i]=0
    scenarios_region_bought[i]=0
    scenarios_region_received[i]=0
    scenarios_region_gave[i]=0
    total_region_bought[i]=0
    total_region_given[i]=0
    total_region_received[i]=0
    
#running simulation 
for trial in range(trials):    
    Additional_Supply, Bought, Final_Supply, Sent, Demand = simulatecovid()    #call method
    for i in range (N): #Reset counters for region received and gave
        region_received[i]=0
        region_gave[i]=0
    for i in range (N):
        if Bought[i]>=1:
            region_bought[i]+=1
            total_region_bought[i]+=Bought[i]
        for j in range (N):
            if (Sent[i,j]>=1):
                region_gave[i]+=1
                region_received[j]+=1
                total_region_given[i]+=Sent[i,j]
                total_region_received[j]+=Sent[i,j]
    for i in range (N):
        if region_gave[i]>=1:
            scenarios_region_gave[i]+=1
        if region_received[i]>=1:
            scenarios_region_received[i]+=1
        
    if sum(Bought.values()) >= 1:
        scenarios_beds_bought+=1
        

    if sum(Sent.values())>=1:
        scenarios_beds_moved+=1
        
    if sum(Bought.values()) == 0:
        if sum(Sent.values())==0:
            scenarios_no_change+=1
               
    if Demand_Max<Demand:
        Demand_Max=Demand
        
    if Demand_Min>Demand:
        Demand_Min=Demand
    All_Demand.append(Demand)
#create histogram of demand
plt.hist(All_Demand, bins = 10)
plt.show()

print("The # of scenarios where beds were bought are " ,scenarios_beds_bought)
print("The # of scenarios where beds were moved are " ,scenarios_beds_moved)
print("The # of scenarios where there was no beds moved or bought were " , scenarios_no_change)
print("The maximum demand scenario ran: ", Demand_Max)
print("The minimum demand scenarios ran: ", Demand_Min)


for i in range(N):
    print("The # of scenarios where region %s bought beds are" %i ,region_bought[i])
    print("The # of scenarios where region %s received beds are" %i ,scenarios_region_received[i])       
    print("The # of scenarios where region %s gave beds are" %i ,scenarios_region_gave[i]) 
    average_region_bought[i]=total_region_bought[i]/trials
    print("The average beds bought by region %s" %i, average_region_bought[i])
    average_region_given[i]=total_region_given[i]/trials
    print("The average beds given by region %s" %i, average_region_given[i])
    average_region_received[i]=total_region_received[i]/trials
    print("The average beds received by region %s" %i, average_region_received[i])   
    
    
    
    
    