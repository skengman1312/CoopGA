import random
from math import modf, comb
from itertools import combinations

#if we take 15 individual we can make 105 groups of 2, so we can generate 210 children:
#print(comb(15, 2))

mut_rate = 0.5
cros_rate = 0.8

#create a toy population of 15 individuals
pop = []
for i in range(15):
    ind = []
    for i in range(8):
        n = random.randint(0,1)
        ind.append(n)
    pop.append(ind)

#create 2 individuals from 2 parents by using uniform crossover
def crossover(ind1, ind2, cros_rate):
    for i in range(len(ind1)):
        x = random.uniform(0,1)
        if x <= cros_rate:
            temp = ind1[i]
            ind1[i] = ind2[i]
            ind2[i] = temp

    return ind1, ind2


def mutation(ind, mut_rate):

    for i, n in enumerate(ind):
        x = random.uniform(0,1)
        if x <= mut_rate:
            if n == 1:
                ind[i] = 0
            else:
                ind[i] = 1
    return ind

def gen_offspring(pop, mut_rate = 0.2, cros_rate = 0.6):
    offspring = []
    couples = list(combinations(pop, 2))
    for couple in couples:
        ind1 = couple[0]
        ind2 = couple[1]
        child1, child2 = crossover(ind1, ind2, cros_rate)
        child1 = mutation(child1, mut_rate)
        child2 = mutation(child2, mut_rate)
        offspring.append(child1)
        offspring.append(child2)

    return offspring
