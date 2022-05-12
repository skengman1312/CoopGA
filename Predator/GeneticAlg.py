import random

ind = [1,0,0,1,0,1,0,1,0,1]

mut_rate = 0.5


def crossover(cros_rate, ind1, ind2):
    for i in range(len(ind1)):
        x = random.uniform(0,1)
        if x <= cros_rate:
            temp = ind1[i]
            ind1[i] = ind2[i]
            ind2[i] = temp

    return ind1, ind2


def mutation(mut_rate, ind):

    for i, n in enumerate(ind):
        x = random.uniform(0,1)
        if x <= mut_rate:
            if n == 1:
                ind[i] = 0
            else:
                ind[i] = 1
    return ind


print(mutation(mut_rate, ind))