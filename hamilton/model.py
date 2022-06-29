import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
import numpy as np
from utils import FloatBinHandler

fam_id = -1

class SocialActivation(BaseScheduler):
    """
    A scheduler which activates each agent once per step, in random order,
    with the order reshuffled every step but only activate the actors.

    :param BaseScheduler: activates agents one at a time, in the order they were added. 
    Assumes that each agent added has a step method which takes no arguments.
    """

    def step(self, actors) -> None:
        """
        Executes the step of all agents, one at a time, in
        random order.
        """
        for agent in self.agent_buffer(shuffled=True):
            if agent.unique_id in actors:
                agent.step()

        self.steps += 1
        self.time += 1


class FamilyAgent(Agent):
    """
    Agent class to simulate altruistic behaviour based on relatedness

    :param Agent: the agent class for Mesa framework
    :type Agent: mesa.agent
    """

    def __init__(self, unique_id, model, genotype, family_id: int):
        """
        Agent class to simulate altruistic behaviour based on relatedness

        :param unique_id: a unique numeric identifier for the agent model
        :type unique_id: int
        :param model:  instance of the model that contains the agent
        :type model: mesa.model
        :param genotype: binary representation of single-gene genotype (0: non-altruist, 1: altruist)
        :type genotype: int
        :param family_id: identifier for the whole family, namely all individuals generated from the same parents
        :type family_id: int
        """
        super().__init__(unique_id, model)
        self.genotype = genotype
        self.family = family_id

    def step(self) -> None:
        """
        A single step of the agent which consists in performing the altruistic action or not
        """
        self.altruistic_action()

    def altruistic_action(self):
        """
        Implementation of a generic altruistic action
        """
        if self.genotype:
            # 1 - death rate (dr) gives the probability for the altruistic agent to survive 
            if random.random() > self.model.dr:
                return
            else:
                self.model.schedule.remove(self)
        else:
            [self.model.schedule.remove(a) for a in self.model.schedule.agent_buffer() 
            if a.family == self.family and a.unique_id != self.unique_id]


class FamilyModel(Model):
    """
    A model for simulation of the evolution of families. 
    All families include all altruists members or all non-altruist members.

    :param Model: the model class for Mesa framework
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
        :param dr: death rate for sacrificing altruist, defaults to 0.95
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
        Add agents to the model with the right proportion (r) of altruistic allele

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
        Function to generate the new population from the parent individuals
        1. Sample N individuals from current population
        2. Generate pairs of inidividuals
        3. Create the new generation, defining inherited genotype (mutation applied) and family ID
        4. Remove all the "old" agents from the model
        5. Add the new generation of agents to the model
        """
        # 1
        mating_ind = random.sample([agent for agent in self.schedule.agents], k=self.N)
        # 2
        mating_pairs = [(mating_ind[i], mating_ind[i + len(mating_ind) // 2])
                        for i in range(len(mating_ind) // 2)] 
        # 3 
        mutate = lambda x: x if random.random() > self.mr else 1 - x
        newgen = [{"genotype": mutate(random.choice([a.genotype for a in p])), "family": p[0].unique_id}
                  for p in mating_pairs for i in range(3)]
        # 4
        [self.schedule.remove((a)) for a in self.schedule.agent_buffer()]
        # 5
        [self.schedule.add(FamilyAgent(i, self, newgen[i]["genotype"], newgen[i]["family"])) for i in range(len(newgen))]

    def step(self) -> None:
        """
        Model step: each family is randomly assigned to an "interaction room". This room could be of two different 
        kinds: 
        Scenario 1: no danger, the whole family survive
        Scenario 2: danger, one actor is randomly chosen from the family group and he will be the agent noticing
        the danger. Depending on his genotype he can sacrifice (altruist) and save the family or he can just run 
        away (non-altruist), sacrificing the rest of the family.
        """

        # creating the "interaction rooms"
        # proportion of the dangerous rooms is compute in such a way to ensure enough agents survive to 
        # generate the next generation
        # TODO: generalize fo x children 
        danger_number = self.N // 4
        ufid = list(set([a.family for a in self.schedule.agent_buffer()]))

        # we just deal with families in dangerous scenario to save computations
        danger_fam = random.sample(ufid, danger_number)
        rooms = [[x for x in self.schedule.agent_buffer() if x.family == f]
                 for f in danger_fam]
        
        # defining the actor randomly
        active = [random.choice(r).unique_id for r in rooms]

        # perform altruistic action
        self.schedule.step(active)

        self.reproduce()

        self.datacollector.collect(self)
