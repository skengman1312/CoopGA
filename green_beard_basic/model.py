import random
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler


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


class BeardAgent(Agent):
    """
    Agent class to simulate GreenBeard altruism behaviour based on genotype

    :param Agent: the agent class for Mesa framework
    :type Agent: mesa.agent
    """

    def __init__(self, unique_id, model, genotype):
        """
        BeardAgent init function
        
        :param unique_id: a unique numeric identifier for the agent model
        :type unique_id: int
        :param model:  instance of the model that contains the agent
        :type model: mesa.model
        :param genotype: binary representation of single-gene genotype (0: non-altruist, 1: altruist)
        :type genotype: int
        """

        super().__init__(unique_id, model)
        self.genotype = genotype


class BeardModel(Model):
    """
    A model for simulation of the evolution of Green Beard Altruism.

    :param Model: the model class for Mesa framework
    :type Model: mesa.model
    """

    def __init__(self, N=500, r=0.5, dr=0.95, mr=0.001):
        """
        BeardModel init function

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
        self.tot_N = N
        self.mr = mr
        self.dr = dr

        self.running = True
        self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
            [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count(),
                "n_agents": lambda x: x.schedule.get_agent_count()})

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
            agent = BeardAgent(i, self, 1)
            self.schedule.add(agent)

        # adding non-altruist agents (genotype = 0)
        for i in range(int(N * r), N+1):
            agent = BeardAgent(i, self, 0)
            self.schedule.add(agent)

    def reproduce(self, max_child=4):
        """
        Function to generate the new population from the parent individuals
        1. Sample individuals from current population and Generate pairs of individuals
        2. Create the new generation within a range, defining inherited genotype (mutation applied)
        3. Add the new generation of agents to the model
        4. Remove all the "old" agents from the model
        """
        # TODO still problema sui pairs se la popolazione è
        # TODO modificare assignment of ID to child (mettere self.next_id() e togliere self.tot_N)
        # 1
        agents = random.sample([agent for agent in self.schedule.agents], k=len(self.schedule.agents))

        for i in range(0, len(agents)-1, 2):
            agent1 = agents[i]
            agent2 = agents[i+1]
            n_child = random.randint(2, max_child)

            # 2
            for j in range(n_child):
                self.tot_N += 1
                child_genotype = agent1.genotype if random.random() < 0.50 else agent2.genotype
                mutate = lambda x: x if random.random() > self.mr else 1 - x
                # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings
                child_genotype = mutate(child_genotype)
                child = BeardAgent(self.tot_N, self, child_genotype)

                # 3
                self.schedule.add(child)

            # 4
            self.schedule.remove(agent1)
            self.schedule.remove(agent2)

    def step(self) -> None:
        """
        Model step
        Each agent is randomly assigned to an "interaction room". Each room can contain a maximum of two agents and 
        could be of two different kinds: 
        - danger, at least one agent dies according to the genotype of the agents involved
        - no danger, both agents survive
        
        Scenario 1 - room with danger.
            If there is only one agent in the room, it will die.
            If there are two agents, one of them is randomly chosen to notice the danger. Depending on its genotype:

            1.1: both agents have the GreenBeard (altruistic) genotype,
                 the agent notified of the danger sacrifice itself (altruist) and save the other agent.
            1.2: at least one agent has the non-altruistic genotype,
                 independently of the genotype of the agent notified of the danger, one of them will die
        """

        # creating the "interaction rooms"
        num_agents = len(self.schedule.agents)
        rooms_number = num_agents  # tot number of rooms

        # TODO spiegare la divisione per 1.87
        danger_number = num_agents // 1.87
        danger_dict: dict = {i: [] for i in range(int(danger_number))}

        # assign each agent to an "interaction room"
        for agent in self.schedule.agent_buffer():
            rand = random.randint(1, rooms_number)
            if rand < danger_number:
                if len(danger_dict[rand]) < 2:
                    danger_dict[rand].append(agent)
                else:
                    continue
            else:
                continue

        # action of the agent - Scenario 1
        for key, value in danger_dict.items():
            if len(value) == 0:
                continue
            elif len(value) == 1:
                self.schedule.remove(value[0])
            else:
                agent1 = value[0]
                agent2 = value[1]
                gen1 = agent1.genotype
                gen2 = agent2.genotype

                # 1.1
                if gen1 and gen2:  # both green beard
                    if random.random() < self.dr: # die with 0.50 probability
                        self.schedule.remove(agent1)

                # 1.2
                else:  # both cowardice or 1 cowardice and 1 altruistic, one of the 2 dies.
                    self.schedule.remove(agent1)

        agents_id = [a.unique_id for a in self.schedule.agents]

        self.schedule.step(agents_id)

        self.reproduce()
        self.datacollector.collect(self)


if __name__ == "__main__":

    model = BeardModel()
    print("Initial frequency of green beard allele:",
          len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())

    for i in range(100):
        model.step()

    print("Final frequency of green beard allele:",
          len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())

