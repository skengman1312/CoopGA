import numpy as np

from model import *
from scipy import stats
from scipy.stats import norm


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
        if self.genotype[0] == 1:  # CHANGED HERE
            # print("alt", self.genotype[0])
            if random.random() > self.model.dr:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer(
            ) if a.family == self.family and a.unique_id != self.unique_id]


class MultigeneFamilyModel(FamilyModel):
    """
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        self.mean = 0.5
        self.mean1 = 0.2
        self.mean2 = 0.7
        self.handler = FloatBinHandler(3, 1)
        super().__init__(N=N, r=r, dr=dr, mr=mr)
        # self.datacollector = DataCollector(model_reporters={
        #     "altruistic fraction": lambda x: len(
        #         [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / x.schedule.get_agent_count(),
        #     "mean rep": lambda x: sum([x.reproductive_fitness(a) for a in x.schedule.agent_buffer()]) / len(
        #         [x.reproductive_fitness(a) for a in x.schedule.agent_buffer()]),
        #     "max rep": lambda x: max([x.reproductive_fitness(a) for a in x.schedule.agent_buffer()]),
        #     "min rep": lambda x: min([x.reproductive_fitness(a) for a in x.schedule.agent_buffer()]),
        #     "mean rep1": lambda x: sum([x.reproductive_fitness(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / len(
        #         [x.reproductive_fitness(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 1]),
        #     "mean rep0": lambda x: sum([x.reproductive_fitness(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 0]) / len(
        #         [x.reproductive_fitness(a) for a in x.schedule.agent_buffer() if a.genotype[0] == 0])

        # })

    def add_agents(self, N, r):
        for i in range(int(N * r)):
            trait2 = self.handler.float2bin(random.random())
            agent = MultigeneFamilyAgent(i, self, [1, trait2], i)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            trait2 = self.handler.float2bin(random.random())
            agent = MultigeneFamilyAgent(i, self, [0, trait2], i)
            self.schedule.add(agent)

    def reproductive_fitness(self, agent):
        if self.schedule.steps % 100 == 0:
            self.mean = random.random()
        phenotype = self.handler.bin2float(agent.genotype[1])
        sd = 0.1
        return np.exp(-((phenotype - self.mean) / sd) ** 2)
        # (np.pi * sd) * np.exp(-0.5 * ((phenotype - mean) / sd)**2)  #  phenotype +0.000001
        # TODO: changing fitness with proper timestep

    def reproductive_fitness_multimodal(self, agent):

        if self.schedule.steps % 100 == 0:
            print(self.schedule.steps)
            n1, n2 = False, False
            self.mean1 = random.random()
            if self.mean1 - 0.2 > 0:
                n1 = random.uniform(0, self.mean1 - 0.2)
            else:
                self.mean2 = random.uniform(self.mean1 + 0.2, 1)

            if self.mean1 + 0.2 < 1:
                n2 = random.uniform(self.mean1 + 0.2, 1)
            else:
                self.mean2 = random.uniform(self.mean1 - 0.2, 1)

            if n1 and n2:
                self.mean2 = random.choice([n1, n2])

        phenotype = self.handler.bin2float(agent.genotype[1])
        sd = 0.1
        print(self.mean1, self.mean2)
        return max(np.exp(-((phenotype - self.mean1) / sd) ** 2), np.exp(-((phenotype - self.mean2) / sd) ** 2))

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
        total_rep_fitness = np.array(
            [self.reproductive_fitness_multimodal(a) for a in self.schedule.agents])
        total_rep_fitness /= total_rep_fitness.sum()
        mating_ind = np.random.choice(
            self.schedule.agents, self.N, replace=False, p=total_rep_fitness)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)]

        # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings

        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": [mutate(random.choice([a.genotype[0] for a in p])),
                                self.trait2_computation(p[0], p[1])],
                   "family": p[0].unique_id} for p in mating_pairs for i in range(3)]

        [self.schedule.remove(a) for a in self.schedule.agent_buffer()]
        [self.schedule.add(MultigeneFamilyAgent(
            i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in range(len(newgen))]


if __name__ == "__main__":
    model = MultigeneFamilyModel(N=1000, mr=0.001, r=0.5)
    # model = FamilyModel()

    print("\naltruists before steps\t", len([a for a in model.schedule.agent_buffer()
                                            if a.genotype[0] == 1]) / model.schedule.get_agent_count())

    early_rep_fitness = [model.reproductive_fitness_multimodal(
        a) for a in model.schedule.agents]
    print(model.mean1, model.mean2)
    for i in range(499):
        model.step()

    print(model.mean1, model.mean2)
    # print("\ngen1\tgen2\tfitness")

    # for a in model.schedule.agents:
    #     print(a.genotype[0], "\t", model.handler.bin2float(a.genotype[1]),
    #           "\t", model.reproductive_fitness_multimodal(a))

    # finalpop_trait2 = [a.genotype[1] for a in model.schedule.agent_buffer()]
    final_rep_fitness = [model.handler.bin2float(
        a.genotype[1]) for a in model.schedule.agent_buffer()]

    counts = {f: final_rep_fitness.count(f) for f in set(final_rep_fitness)}
    counts = {k: counts[k] for k in sorted(counts, reverse=True)}
    print(counts)
    # print(max(early_rep_fitness))
    # print(max(final_rep_fitness))

    # print([model.handler.bin2float(t) for t in finalpop_trait2])

    # print(model.mean)

    print("yee<")
