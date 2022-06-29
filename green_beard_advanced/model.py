import random
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler


class SocialActivation(BaseScheduler):
    """A scheduler which activates each agent once per step, in random order,
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
    Agent class to simulate Green Beard altruism

    :param Agent: the agent class for Mesa framework
    :type Agent: mesa.agent
    """

    def __init__(self, unique_id, model, genotype):
        """
        Agent class to simulate Green Beard altruism

        :param unique_id: a unique numeric identifier for the agent model
        :type unique_id: int
        :param model:  instance of the model that contains the agent
        :type model: mesa.model
        :param genotype: list composed of 2 binary representations (allele1, allele2)
        :type genotype: list

        genotype: 1 gene with 2 alleles (a list of 2 integers)
            - allele1: 1 codes for altruism 0 for cowardice
            - allele2: 1 code for beard 0 for non beard
        """

        super().__init__(unique_id, model)
        self.genotype = genotype


def crossover(agent1, agent2):

    """
    Implementation of crossover function, to apply a one point crossover to 2 agents

    :param unique_id: a unique numeric identifier for the agent model
    :type unique_id: int
    :param model:  instance of the model that contains the agent
    :type model: mesa.model
    :param genotype: list composed of 2 binary representations (allele1, allele2)
    :type genotype: list

    RECOMBINATION (CROSSOVER) one point
    """
    allele1 = agent1.genotype[0]
    allele2 = agent2.genotype[1]
    return [allele1, allele2]


class BeardModelAdv(Model):
    """
    a model for simulation of the evolution of Green Beard Altruism
    """

    def __init__(self, N=2000, r=0.25, dr=0.95, mr=0.001, cr=0, linkage_dis=False):
        """
        N: total number of agents
        r: initial ratio of each allele
        dr: survival rate
        mr: mutation rate
        cr: crossover rate
        """

        super().__init__()
        self.schedule = SocialActivation(self)
        self.n_steps = 0
        self.N = N  # N
        self.tot_N = N
        self.current_id = 0
        self.mr = mr
        self.dr = dr
        self.cr = cr
        self.linkage_dis = linkage_dis

        self.running = True
        self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
            [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1]) / x.schedule.get_agent_count(),
                "true beards fraction": lambda x: len(
            [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1 and a.genotype[1] == 1]) / x.schedule.get_agent_count(),
                "suckers fraction": lambda x: len(
                    [a for a in x.schedule.agent_buffer() if a.genotype[0] == 1 and a.genotype[1] == 0]) / x.schedule.get_agent_count(),
                "impostors fraction": lambda x: len(
                    [a for a in x.schedule.agent_buffer() if a.genotype[0] == 0 and a.genotype[1] == 1]) / x.schedule.get_agent_count(),
                "cowards fraction": lambda x: len(
                    [a for a in x.schedule.agent_buffer() if a.genotype[0] == 0 and a.genotype[1] == 0]) / x.schedule.get_agent_count(),
                "n_agents": lambda x: x.schedule.get_agent_count()})

        if not linkage_dis:
            # initialization without linkage disequilibrium
            for i in range(int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 1])
                self.tot_N += 1
                self.schedule.add(agent)

            for i in range(int(N * r), 2 * int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 0])
                self.tot_N += 1
                self.schedule.add(agent)

            for i in range(2 * int(N * r), 3 * int(N * r)):
                agent = BeardAgent(self.next_id(), self, [0, 1])
                self.tot_N += 1
                self.schedule.add(agent)

            for i in range(3 * int(N * r), N + 1):
                agent = BeardAgent(self.next_id(), self, [0, 0])
                self.tot_N += 1
                self.schedule.add(agent)

        else:
            # initialization for linkage disequilibrium
            for i in range(int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 1])
                self.tot_N += 1
                self.schedule.add(agent)

            for i in range(int(N * r), N + 1):
                agent = BeardAgent(self.next_id(), self, [0, 0])
                self.tot_N += 1
                self.schedule.add(agent)

    def reproduce(self, max_child=4):
        """
        function to generate the new population from the parent individuals
        select 2 random agents. Decide randomly if they will do 2,3 or 4 children. Create children with genotype taken
        randomly from one of the 2 parents
        During the reproduction there is the chance of crossover and mutation
        """

        agents = random.sample([agent for agent in self.schedule.agents], k=self.schedule.get_agent_count())

        for i in range(0, len(agents)-1, 2):
            agent1 = agents[i]
            agent2 = agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                self.tot_N += 1
                if random.random() < self.cr:
                    child_genotype = crossover(agent1, agent2)
                else:
                    child_genotype = agent1.genotype if random.random() < 0.50 else agent2.genotype

                # mutate = lambda x: x if random.random() > self.mr else 1 - x
                # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings
                gen1 = child_genotype[0]
                gen2 = child_genotype[1]

                if random.random() < self.mr:
                    gen1 = 1 - gen1

                if random.random() < self.mr:
                    gen2 = 1 - gen2

                child = BeardAgent(self.next_id(), self, [gen1, gen2])
                self.schedule.add(child)

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)

    def step(self) -> None:

        print("numero altruisti: ", len([a for a in self.schedule.agent_buffer() if a.genotype[0] == 1]))
        # creating the "interaction rooms"
        num_agents = len(self.schedule.agents)
        rooms_number = num_agents  # tot number of rooms
        self.n_steps += 1

        if not self.linkage_dis:
            danger_number = num_agents // 1.893  # we derived it from the wcs to have at least 500 individuals left,
        else:
            danger_number = num_agents // 1.9

        danger_dict: dict = {i: [] for i in range(int(danger_number))}
        # dictionary in which the key is the room number and the value is the list of individuals in that room

        # assign each agent to a tree/room
        for agent in self.schedule.agent_buffer():
            rand = random.randint(1, rooms_number)
            if rand < danger_number:  # pred
                if len(danger_dict[rand]) < 2:
                    danger_dict[rand].append(agent)

                else:
                    continue  # goes to no pred room

            else:  # goes to no pred room
                continue

        # action of each agent
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

                if gen1[0] and gen2[1]:  # agent1 is altruistic and gen2 has green beard
                    if random.random() < self.dr:  # die with 0.50 probability
                        self.schedule.remove(agent1)
                else:
                    self.schedule.remove(agent2)

        agents_id = [a.unique_id for a in self.schedule.agents]
        self.schedule.step(agents_id)

        self.reproduce()
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = BeardModelAdv()

    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq TRUE BEARDS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq SUCKERS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq IMPOSTORS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq COWARDS

    # initial frequency of green beard allele
    for i in range(500):
        #print("step: ", i)
        model.step()
    print("number of agents: ", model.schedule.get_agent_count())

    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq TRUE BEARDS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq SUCKERS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq IMPOSTORS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq COWARDS

    # frequency of green beard allele
    print("yee")
