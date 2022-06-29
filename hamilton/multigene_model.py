import random
import numpy as np
from model import *
 
class MultigeneFamilyAgent(FamilyAgent):
    """
    Agent class to simulate altruistic behaviour based on relatedness where genotype contains two genes

    :param FamilyAgent: Agent class to simulate altruistic behaviour based on relatedness
    :type FamilyAgent: FamilyAgent
    :param genotype: list of [trait1, trait2]
    
    trait1: binary gene, allele 1 codes for altruism allele 0 for cowardice
    trait2: real number coded as bin, from 0 to 1 
    """

    def altruistic_action(self):
        """
        Implementation of a generic altruistic action. 
        If the actor is altruist he sacrifices and the rest of the family survives (he also have a small
        probability, 1-dr, to survive). If the actor is non-altruist he survives and the rest of the family not. 
        """
        if self.genotype[0] == 1: 
            if random.random() > self.model.dr:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer() 
            if a.family == self.family and a.unique_id != self.unique_id]


class MultigeneFamilyModel(FamilyModel):
    """
    Extension of the FamilyModel in order to deal with genotype with two genes

    :param FamilyModel: A model for simulation of the evolution of families. 
    :type FamilyModel: FamilyModel
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        Extension of the FamilyModel in order to deal with genotype with two genes

        :param N: total number of agents, defaults to 500
        :type N: int, optional
        :param r: initial ratio of altruistic allele, defaults to 0.5
        :type r: float, optional
        :param dr: death rate for sacrificing altruist, defaults to 0.95
        :type dr: float, optional
        :param mr: mutation rate, defaults to 0.001
        :type mr: float, optional
        """
        
        # Defining stddev and mean of first mode for the bimodal fitness landscape for trait2. 
        # Mean of second mode is computed randomly later. 
        self.mean = 0.5
        self.sd = 0.1

        # Setting the conversion from float to binary 
        self.handler = FloatBinHandler(3, 1)
    
        super().__init__(N=N, r=r, dr=dr, mr=mr)
    
        self.datacollector = DataCollector(model_reporters={
            "altruistic fraction": lambda x: len(
                [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / x.schedule.get_agent_count(),
            "mean rep": lambda x: sum([x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer()]) / len(
                [x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer()]),
            "max rep": lambda x: max([x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer()]),
            "min rep": lambda x: min([x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer()]),
            "mean rep1": lambda x: sum([x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / len(
                [x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 1]),
            "mean rep0": lambda x: sum([x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 0]) / len(
                [x.reproductive_fitness_multimodal(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 0])

        })

    def add_agents(self, N, r):
        """
        Add agents to the model with the right proportion (r) of altruistic allele

        :param N: total number of agents
        :type N: int
        :param r: initial ratio of altruistic allele
        :type r: float
        """
        # adding altruist agents (genotype[0] = 1)
        for i in range(int(N * r)):
            trait2 = self.handler.float2bin(random.random())
            agent = MultigeneFamilyAgent(i, self, [1, trait2], i)
            self.schedule.add(agent)

        # adding non-altruist agents (genotype[0] = 0)
        for i in range(int(N * r), N):
            trait2 = self.handler.float2bin(random.random())
            agent = MultigeneFamilyAgent(i, self, [0, trait2], i)
            self.schedule.add(agent)

    def reproductive_fitness_multimodal(self, agent):
        """
        Computing fitness based on trait2 of genotype only. Fitness landscape is a bimodal.
        Minimum fitness is 0 and maximum fitness is 1. 

        :param agent: a model agent
        :type agent: MultigeneFamilyAgent
        :return: fitness of trait2
        :rtype: float
        """
        phenotype = self.handler.bin2float(agent.genotype[1])
        
        return max(np.exp(-((phenotype - self.mean[0]) / self.sd) ** 2), 
                   np.exp(-((phenotype - self.mean[1]) / self.sd) ** 2))

    def update_fitness(self):
        """
        Change the means of the bimodal fitness landscape in order to simulate dynamic environment.
        We impose distance from the two means to be at least 0.2 

        :return: new updated means of the bimodal fitness landscape of trait2
        :rtype: list
        """
        m1 = random.random()
        if m1 < 0.2:
            m2 = random.uniform(m1 + 0.2, 1)
        elif m1 > 0.8:
            m2 = random.uniform(0, m1 - 0.2)
        else:
            m2 = random.choice([random.uniform(m1 + 0.2, 1), random.uniform(0, m1 - 0.2)])
        return [m1, m2]

    def trait2_computation(self, parent1, parent2):
        """
        Inheritance of trait2, based on on trait2 of both parents. Thanks to binary representation 
        we can easily perform both crossover and mutation

        :param parent1: first agent of the couple generating offspring
        :type parent1: MultigeneFamilyAgent
        :param parent2: second agent of the couple generating offspring
        :type parent2: MultigeneFamilyAgent
        :return: trait2 of the offspring
        :rtype: str
        """
        # crossover
        gene_offspring = ''
        for p1, p2 in zip(parent1.genotype[1], parent2.genotype[1]):
            gene_offspring += random.choice((p1, p2))

        # mutation
        mutate = lambda x: x if random.random() > self.mr else str(1 - int(x))
        gene_offspring_mutated = '0b'
        for g in gene_offspring[2:]:
            gene_offspring_mutated += mutate(g)

        return gene_offspring_mutated

    def reproduce(self):
        """
        Function to generate the new population from the parent individuals
        1. Sample N individuals from current population
        2. Generate pairs of inidividuals
        3. Create the new generation, defining inherited genotype (mutation applied) and family ID
        4. Remove all the "old" agents from the model
        5. Add the new generation of agents to the model
        """
        # in first and every 100 steps we change the fitness landscape to simulate dynamic environment
        if self.schedule.steps % 100 == 0:
            self.mean = self.update_fitness()
        
        total_rep_fitness = np.array([self.reproductive_fitness_multimodal(a) for a in self.schedule.agents])
        total_rep_fitness /= total_rep_fitness.sum()
        
        # based on the fitness of trait2 we assign more or less probability to reproduce to each agent
        mating_ind = np.random.choice(self.schedule.agents, self.N, replace=False, p=total_rep_fitness)
        
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]

        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": [mutate(random.choice([a.genotype[0] for a in p])),
                                self.trait2_computation(p[0], p[1])],
                   "family": p[0].unique_id} for p in mating_pairs for i in range(3)]

        [self.schedule.remove(a) for a in self.schedule.agent_buffer()]
        [self.schedule.add(MultigeneFamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"])) 
        for i in range(len(newgen))]


if __name__ == "__main__":
    model = MultigeneFamilyModel(N=1000, mr=0.001, r=0.5)
    for i in range(100):
        model.step()
    