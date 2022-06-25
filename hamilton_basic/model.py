import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
import numpy as np
from utils import FloatBinHandler

fam_id = -1


class SocialActivation(BaseScheduler):
    """A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step but only activate the actors.

    Assumes that all agents have a step(model) method.

    """

    def step(self, actors) -> None:
        """Executes the step of all agents, one at a time, in
        random order.

        """
        for agent in self.agent_buffer(shuffled=True):
            if agent.unique_id in actors:
                agent.step()

        self.steps += 1
        self.time += 1


class FamilyAgent(Agent):
    """
    an agent to simulate the altruistic behaviour based on relatedness
    """

    def __init__(self, unique_id, model, genotype, family_id: int):
        """
        :param genotype: 1 codes for altruism 0 for cowardice
        """
        super().__init__(unique_id, model)
        self.genotype = genotype
        self.family = family_id

    def step(self) -> None:
        self.altruistic_action()

    def altruistic_action(self):
        """
        Implementation of a generic altruistic action
        """
        if self.genotype:
            if random.random() > self.model.dr:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer(
            ) if a.family == self.family and a.unique_id != self.unique_id]
        # return {"family": self.family,"action": bool(self.genotype), "survival": random.random() > 0.95 if self.genotype else True}


class FamilyModel(Model):
    """
    a model for simulation of the evolution of family related altruism
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        :param N: total number of agents
        :param r: initial ratio of altruistic allele
        :param dr: survival rate
        :param mr: mutation rate
        """
        self.schedule = SocialActivation(self)
        self.N = N
        self.mr = mr
        self.dr = dr
        self.running = True
        self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
            [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count()})

        self.add_agents(N, r)

        self.reproduce()

    def add_agents(self, N, r):
        for i in range(int(N * r)):
            agent = FamilyAgent(i, self, 1, i)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            agent = FamilyAgent(i, self, 0, i)
            self.schedule.add(agent)

    def reproduce(self):
        """
        function to generate the new population from the parent individuals
        """
        mating_ind = random.sample(
            [agent for agent in self.schedule.agents], k=self.N)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]
        # print(len(set(mating_ind)))
        # print(mating_pairs)
        # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings

        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), "family": p[0].unique_id} for p in
                  mating_pairs for i in range(3)]
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        [self.schedule.add(FamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in
         range(len(newgen))]

    def step(self) -> None:
        # creating the "interaction rooms"
        # we derived it from the wcs to have at least 500 individuals left,
        danger_number = self.N // 4
        # it has to be generalized for n child, now takes as granted 4 childs
        ufid = list(set([a.family for a in self.schedule.agent_buffer()]))
        danger_fam = random.sample(ufid, danger_number)
        rooms = [[x for x in self.schedule.agent_buffer() if x.family == f]
                 for f in danger_fam]
        active = [random.choice(r).unique_id for r in rooms]

        self.schedule.step(active)

        self.reproduce()
        self.datacollector.collect(self)

        # reproduction part

        # mesa.time.RandomActivationByType


class MultigeneFamilyAgent(FamilyAgent):
    """
    :param genotype: list of [traint1, trait2]
    trait1: binary gene, allele 1 codes for altruism allele 0 for cowardice
    trait2: real number coded as bin, from 0 (ugly) to 1 (beautiful)
    """

    def altruistic_action(self):
        """
        Implementation of a generic altruistic action
        """
        if self.genotype[0]:  # CHANGED HERE
            if random.random() > self.model.dr:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer(
            ) if a.family == self.family and a.unique_id != self.unique_id]

    pass


class MultigeneFamilyModel(FamilyModel):
    """
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        self.handler = FloatBinHandler(3, 1)
        super().__init__(N=N, r=r, dr=dr, mr=mr)
        self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
            [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / x.schedule.get_agent_count()})

    def add_agents(self, N, r):
        for i in range(int(N * r)):
            trait2 = self.handler.float2bin(random.random())
            agent = FamilyAgent(i, self, [1, trait2], i)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            trait2 = self.handler.float2bin(random.random())
            agent = FamilyAgent(i, self, [0, trait2], i)
            self.schedule.add(agent)

    def reproductive_fitness(self, agent):
        phenotype = self.handler.bin2float(agent.genotype[1])
        mean, sd = 0.6, 0.1
        return phenotype #@(np.pi * sd) * np.exp(-0.5 * ((phenotype - mean) / sd)**2)

    def trait2_computation(self, parent1, parent2):
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
        function to generate the new population from the parent individuals
        """
        total_rep_fitness = np.array([self.reproductive_fitness(a) for a in self.schedule.agents])
        #print(len(total_rep_fitness))
        total_rep_fitness /= total_rep_fitness.sum()
        #print(len(total_rep_fitness))
        print(total_rep_fitness)
        mating_ind = np.random.choice(self.schedule.agents, self.N, replace=False, p=total_rep_fitness)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]
        # print(len(set(mating_ind)))
        # print(mating_pairs)
        # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings

        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": [mutate(random.choice([a.genotype[0] for a in p])),
                                self.trait2_computation(p[0], p[1])],
                   "family": p[0].unique_id} for p in mating_pairs for i in range(3)]

        [self.schedule.remove(a) for a in self.schedule.agent_buffer()]
        [self.schedule.add(FamilyAgent(
            i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in range(len(newgen))]


if __name__ == "__main__":
    model = MultigeneFamilyModel(N = 10, mr = 0.001, r = 0.5)
    # model = FamilyModel()
    print(len([a for a in model.schedule.agent_buffer()
          if a.genotype[0] == 1]) / model.schedule.get_agent_count())
    early_rep_fitness = [model.reproductive_fitness(a) for a in model.schedule.agents]
    for i in range(5):
        model.step()
    print(len([a for a in model.schedule.agent_buffer()
          if a.genotype[0] == 1])/model.schedule.get_agent_count())
    finalpop_trait2 = [a.genotype[1] for a in model.schedule.agent_buffer()]
    final_rep_fitnes = [model.reproductive_fitness(a) for a in model.schedule.agents]
    counts = {f: final_rep_fitnes.count(f) for f in set(final_rep_fitnes)}
    counts = {k : counts[k] for k in sorted(counts, reverse=True)}
    print(max(early_rep_fitness))
    print(max(final_rep_fitnes))
    #print(finalpop_trait2)
    print(counts)
    print("yee")
