set passengerId; 
set flightId;
set nodes;

param connected{i in nodes, j in nodes};
param distance{i in nodes, j in nodes};
param startLoc{i in passengerId};
param finalLoc{i in passengerId};

param flightStartLoc{i in flightId};

param passengerDesire{i in passengerId};

param Wprofit;
param Wsatisfy;

param flightPassengerCapacity;
param maxReachTime;
param timeCost;
param totalTime;
param numNodes;
param numFlights;

param ticketCompensation;
param flightPerHourCost;
param ticketPerHourCost;

var passenger{i in passengerId, a in nodes, t in 1..totalTime} binary;
var flight{i in flightId, a in nodes, t in 1..totalTime} binary;
var ticket{i in flightId, j in passengerId, t in 1..(totalTime-1)} binary;
var yp{i in passengerId, a in  nodes, b in nodes, t in 1..(totalTime-1)} binary;
var yf{i in 1..numFlights, a in  nodes, b in nodes, t in 1..(totalTime-1)} binary;

var profit integer;
var ticketCost{i in passengerId};
var flightCost{i in 1..numFlights};

var flightFlow{i in flightId, t in 1..totalTime} integer;
var passengerFlow{i in passengerId, t in 1..totalTime} integer; 
var lossP{i in passengerId, a in nodes, b in nodes};
var lossF{i in 1..numFlights, a in nodes, b in nodes};

# minimize Objective:
#     Wpath*(sum {i in passengerId, t in 1..(totalTime-1), a in nodes, b in nodes} lossP[i, a, b]*yp[i, a, b, t]) - Wsatisfy*sum {i in passengerId} passengerDesire[i]*(passenger[i, finalLoc[i], maxReachTime]-1);

maximize Objective:
    Wsatisfy*sum {i in passengerId} passengerDesire[i]*(passenger[i, finalLoc[i], maxReachTime]-1) + Wprofit*profit;

#------------------------------------------------------
# PROFIT and PRICE DESCRIPTION

subject to profitDefinitionConstraint:
	profit = (sum{i in passengerId} passenger[i, finalLoc[i], maxReachTime]*ticketCost[i] - sum{i in passengerId} (1-passenger[i, finalLoc[i], maxReachTime])*ticketCompensation*flightPassengerCapacity*passengerDesire[i]) 
			-(sum{j in 1..numFlights} flightCost[j]) ;

subject to ticketCostDefinition{i in passengerId}:
	ticketCost[i] = ticketPerHourCost*flightPassengerCapacity*((max{t in 1..totalTime} t*(1-passenger[i, finalLoc[i],t])+1)-(min{t in 1..totalTime} t*(1-passenger[i, startLoc[i], t])-1));

subject to flightCostDefinition{j in 1..numFlights}:
	flightCost[j] = flightPerHourCost*flightPassengerCapacity*((totalTime-1) - sum{t in 1..(totalTime-1)} sum{a in 1..numNodes} yf[j, a, a, t]);
	

#-------------------------------------------------------
# PASSENGER CONSTRAINTS

#  Fixed start position of every passenger
subject to startPos{i in passengerId, a in nodes}:
    passenger[i, a, 1] = if a==startLoc[i] then 1 else 0;

# Passenger must reach his destination in no more than maxReachTime
# subject to finalPos{i in passengerId, a in nodes}:
#     passenger[i, a, maxReachTime] = if a==finalLoc[i] then 1 else 0;
    
# Value of variable passenger[i, t] must be some number in the nodes
subject to passengerLocationConstraint{i in passengerId, t in 1..totalTime}:
    sum{a in nodes} passenger[i, a, t] = 1;
    
# incentive to reach the final location as soon as possible
subject to shortestPathPassenger{i in passengerId, a in nodes, b in nodes}:
	lossP[i, a, b] = if (a==b and a!=0) then 0 else timeCost;

# when two time states connected ( temp variable)
subject to transitionConstraint{i in passengerId, a in nodes, b in nodes, t in 1..(totalTime-1)}:
	yp[i, a, b, t] = passenger[i, a, t]*passenger[i, b, t+1]*connected[a,b];

# for visualization purpose
subject to vizPassengerConstraint{i in passengerId, t in 1..totalTime}:
	passengerFlow[i, t] = sum{a in nodes} a*passenger[i, a, t];  

# Once passenger reaches his destination, it must not move
subject to stayAtFinalPos{i in passengerId, t in 1..(totalTime-1)}:
	passenger[i, finalLoc[i], t] = if passenger[i, finalLoc[i], t]=1 then passenger[i, finalLoc[i], t+1] else passenger[i, finalLoc[i], t];

# When is a transition valid?? I.E. 0 TO B when valid when distance A to B is 10 and so on
subject to passengerLandingConstraint{i in passengerId, a in 1..numNodes, b in 1..numNodes, t1 in 1..totalTime, t2 in 1..totalTime}:
    if t1<t2 and passenger[i,a,t1] == 1 and passenger[i,b,t2] == 1 and sum{t in t1+1..t2-1} passenger[i, 0, t]==t2-t1-1 then t2-t1 else distance[a,b]==distance[a,b];

#--------------------------------------------------------
# FLIGHT CONSTRAINTS 

# yf[i, a, b, t]=1 if flight goes from node a to node b at time t to t+1. Valid only for moving flights
subject to flightFlowVar{i in 1..numFlights, a in nodes, b in nodes, t in 1..(totalTime-1)}:
    yf[i, a, b, t] = flight[i, a, t]*flight[i, b, t+1]*connected[a, b];

# incentive to reach the final location as soon as possible
subject to shortestPathFlight{i in 1..numFlights, a in nodes, b in nodes}:
	lossF[i, a, b] = if (a==b and a!=0) then 0 else timeCost;

# for visualization purpose
subject to vizFlightConstraint{i in 1..numFlights, t in 1..totalTime}:
	flightFlow[i, t] = sum{a in nodes} a*flight[i, a, t];  	

# Value of variable flight[i, t] must be some number in the nodes. Valid only for moving flights
subject to flightLocationConstraint{i in 1..numFlights, t in 1..totalTime}:
    sum{a in nodes} flight[i, a, t] = 1;

#  Fixed start position of every flight. Valid only for moving flights-
subject to flightStartPos{i in 1..numFlights, a in nodes}:
    flight[i, a, 1] = if a==flightStartLoc[i] then 1 else 0;

# When is a transition valid?? I.E. 0 TO B when valid when distance A to B is 10 and so on
subject to flightLandingConstraint{i in 1..numFlights, a in 1..numNodes, b in 1..numNodes, t1 in 1..totalTime, t2 in 1..totalTime}:
    if t1<t2 and flight[i, a, t1] == 1 and flight[i, b, t2] == 1 and sum{t in t1+1..t2-1} flight[i, 0, t]==t2-t1-1 then t2-t1 else distance[a,b]==distance[a,b];

#---------------------------------------------------------
# PASSENGER AND FLIGHT CONNECTED

# if passenger not moving, it is associated with flight -1
subject to passengerStillConstraint{i in passengerId, t in 1..(totalTime-1)}: 
	ticket[-1, i, t] = sum{a in 1..numNodes} yp[i, a, a, t];

# each ticket associated with unique passenger at the given time
subject to uniqueTicketConstraint{i in passengerId, t in 1..(totalTime-1)}:
	sum{j in flightId} ticket[j, i, t] = 1;

# number of tickets offered associated with a given plane are at max the flight capacity	
subject to flightPassengerCapacityConstraint{j in 1..numFlights, t in 1..(totalTime-1)}:
   	0<= sum{i in passengerId} ticket[j, i, t] <= flightPassengerCapacity;

# if 'from' or 'to' an intermmediate station the ticket remains same
subject to sameFlyingTicketConstraint{i in passengerId, j in 1..numFlights, t in 2..(totalTime-1)}:
	if passenger[i, 0, t]==1 then ticket[j, i, t-1] else ticket[j, i, t] = ticket[j, i, t];

# WHEN IS A TICKET[I, J, T] = 1?
#  ticket is valid if the associated passenger and plane is flying along that edge
subject to ticketValidityConstraint{i in passengerId, j in 1..numFlights, t in 1..(totalTime-1)}:
	ticket[j, i, t]  = sum{a in nodes, b in nodes} if !(a==b and a!=0) then yp[i, a, b, t]*yf[j, a, b, t] else 0;