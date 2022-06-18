import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
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
        genotype: 1 codes for altruism 0 for cowardice
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
            if random.random() > 0.95:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer() if a.family == self.family and a.unique_id != self.unique_id]
        # return {"family": self.family,"action": bool(self.genotype), "survival": random.random() > 0.95 if self.genotype else True}


class FamilyModel(Model):
    """
    a model for simulation of the evolution of family related altruism
    """

    def __init__(self, N=500, r=0.5):
        """
        N: total number of agents
        r: initial ratio of altruistic allele
        """
        self.schedule = SocialActivation(self)
        self.N = N
        self.running = True
        self.datacollector = DataCollector(model_reporters={"altruistic fraction" : lambda x:  len([a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count() })
        # TODO: add datacollector

        for i in range(int(N * r)):
            agent = FamilyAgent(i, self, 1, i)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            agent = FamilyAgent(i, self, 0, i)
            self.schedule.add(agent)

        self.reproduce()

    def reproduce(self):
        """
        function to generate the new population from the parent individuals
        """
        mating_ind = random.sample([agent for agent in self.schedule.agents], k=self.N)
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2]) for i in range(len(mating_ind) // 2)]
        # print(len(set(mating_ind)))
        # print(mating_pairs)
        mutate = lambda x: x if random.random() < 0.97 else 1 - x  # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), "family": p[0].unique_id} for p in
                  mating_pairs for i in range(4)]
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        [self.schedule.add(FamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in
         range(len(newgen))]

    def step(self) -> None:
        # creating the "interaction rooms"we derived it from the wcs to have at least 500 individuals left,
        # it has to be generalized for n child, now takes as granted 4 childs
        ufid = list(set([a.family for a in self.schedule.agent_buffer()]))
        danger_fam = random.sample(ufid, danger_number)
        rooms = [[x for x in self.schedule.agent_buffer() if x.family == f] for f in danger_fam]
        active = [random.choice(r).unique_id for r in rooms]

        self.schedule.step(active)

        self.reproduce()
        self.datacollector.collect(self)

        # reproduction part

        # mesa.time.RandomActivationByType


if __name__ == "__main__":
    model = FamilyModel()
    print(len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())
    for i in range(400):
        model.step()
    print(len([a for a in model.schedule.agent_buffer() if a.genotype == 1])/model.schedule.get_agent_count() )
    print("yee")
