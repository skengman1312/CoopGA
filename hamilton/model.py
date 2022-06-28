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
    A model for simulation of the evolution of families. 
    All families includes all altruists members or all non-altruist members.

    :param Model: The model class for Mesa framework
    :type Model: mesa.model
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        A model for simulation of the evolution of families. 
        All families includes all altruists members or all non-altruist members.

        :param N: total number of agents, defaults to 500
        :type N: int, optional
        :param r: initial ratio of altruistic allele, defaults to 0.5
        :type r: float, optional
        :param dr: death rate, defaults to 0.95
        :type dr: float, optional
        :param mr: mutation rate, defaults to 0.001
        :type mr: float, optional
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
        """
        Add agents to the model with the 
        right proportion (r) of altruistic allele

        :param N: total number of agents
        :type N: int
        :param r: initial ratio of altruistic allele
        :type r: float
        """
        # adding altruist agents (genotype = 1)
        for i in range(int(N * r)):
            agent = FamilyAgent(i, self, 1, i)
            self.schedule.add(agent)

        # adding non-altruist agents (genotype = 1)
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
