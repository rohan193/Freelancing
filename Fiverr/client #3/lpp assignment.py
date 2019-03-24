#A. The Silly Nut Company makes two mixtures of nuts: Mixture A and Mixture B. A pound of 
#Mixture A contains 12 oz of peanuts, 3 oz of almonds and 1 oz of cashews and sells for $4. A
#pound of Mixture B contains 12 oz of peanuts, 2 oz of almonds and 2 oz of cashews and sells
#for $5. The company has 1080 lb. of peanuts, 240 lb. of almonds, 160 lb. of cashews. How
#many pounds of each of mixtures A and B should the company make to maximize profit?
#[Note: You need to check your units whenever you calculate an optimization problem. In this
#case you need to either use ounces for all values or pounds.]

import pulp

sales = pulp.LpProblem('sales', pulp.LpMaximize)
na = pulp.LpVariable('Quantity of mixture A(in pounds)', cat = 'Continuous', lowBound=0)
nb = pulp.LpVariable('Quantity of mixture B(in pounds)', cat = 'Continuous', lowBound=0)
sales += 4*na + 5*nb
sales += (12/16)*na + (12/16)*nb <= 1080
sales += (3/16)*na + (2/16)*nb <= 240
sales += (1/16)*na + (2/16)*nb <= 160
sales.solve()
print(pulp.LpStatus[sales.status])
print(pulp.value(sales.objective))
for var in sales.variables():
    print('{} = {}'.format(var.name,var.varValue))

#B. Dr. Lum teaches part-time at two different community colleges, Hilltop College and Serra
#College. Dr. Lum can teach up to 5 classes per semester. For every class taught by him at
#Hilltop College, he needs to spend 3 hours per week preparing lessons and grading papers,
#and for each class at Serra College, he must do 4 hours of work per week. He has
#determined that he cannot spend more than 18 hours per week preparing lessons and
#grading papers. If he earns $4,000 per class at Hilltop College and $5,000 per class at Serra
#College, how many classes should he teach at each college to maximize his income, and
#what will be his income?

import pulp

income = pulp.LpProblem('income', pulp.LpMaximize)
nch = pulp.LpVariable('Number of classes in Hilltop college', cat = 'Integer', lowBound=0)
ncs = pulp.LpVariable('Number of classes in Sierra college', cat = 'Integer', lowBound=0)

income += 4000*nch + 5000*ncs, 'income'
income += nch + ncs <= 5
income += 3*nch + 4*ncs <= 18

income.solve()
print(pulp.LpStatus[income.status])
print(pulp.value(income.objective))
for var in income.variables():
#    print(var)
    print("{} = {}".format(var.name, var.varValue))
