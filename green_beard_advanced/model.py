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
    Agent class to simulate Green Beard altruism considering 2 alleles

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
        :param genotype: list composed of 2 binary representations [allele1, allele2]
            - allele1: 1 codes for altruism, 0 for cowardice
            - allele2: 1 code for green beard, 0 for non beard
        :type genotype: list
        """

        super().__init__(unique_id, model)
        self.genotype = genotype


def crossover(agent1, agent2):

    """
    Implementation of crossover function, to apply a one point crossover to 2 agents

    :param agent1: a unique numeric identifier for the agent model
    :type agent1: int
    :param agent2:  instance of the model that contains the agent
    :type agent2: mesa.model
    """

    allele1 = agent1.genotype[0]
    allele2 = agent2.genotype[1]
    return [allele1, allele2]


class BeardModelAdv(Model):
    """
    A model for simulation of the evolution of Green Beard Altruism.

    :param Model: the model class for Mesa framework
    :type Model: mesa.model
    """

    def __init__(self, N=2000, r=0.25, dr=0.95, mr=0.001, cr=0, linkage_dis=False):
        """
        BeardModelAdv init function

        :param N: total number of agents, defaults to 500
        :type N: int, optional
        :param r: initial ratio of altruistic allele, defaults to 0.5
        :type r: float, optional
        :param dr: death rate for sacrificing altruist, defaults to 0.95
        :type dr: float, optional
        :param mr: mutation rate, defaults to 0.001
        :type mr: float, optional
        :param cr: cross-over rate, defaults to 0
        :type cr: float, optional
        :param linkage_dis: flag to preform linkage equilibrium or disequilibrium simulation, defaults to False
        :type linkage_dis: bool, optional
        """

        super().__init__()
        self.schedule = SocialActivation(self)
        self.N = N
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

        self.add_agents(N, r, linkage_dis)

    def add_agents(self, N, r, linkage_dis):
        """
        Add agents to the model with the right proportion (r) of altruistic allele

        :param N: total number of agents
        :type N: int
        :param r: initial ratio of altruistic allele
        :type r: float
        :param linkage_dis: flag to preform linkage equilibrium or disequilibrium simulation, defaults to False
        :type linkage_dis: bool, optional
        """

        if not linkage_dis:
            # initialization without linkage disequilibrium
            for i in range(int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 1])
                self.schedule.add(agent)

            for i in range(int(N * r), 2 * int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 0])
                self.schedule.add(agent)

            for i in range(2 * int(N * r), 3 * int(N * r)):
                agent = BeardAgent(self.next_id(), self, [0, 1])
                self.schedule.add(agent)

            for i in range(3 * int(N * r), N + 1):
                agent = BeardAgent(self.next_id(), self, [0, 0])
                self.schedule.add(agent)

        else:
            # initialization for linkage disequilibrium
            for i in range(int(N * r)):
                agent = BeardAgent(self.next_id(), self, [1, 1])
                self.schedule.add(agent)

            for i in range(int(N * r), N + 1):
                agent = BeardAgent(self.next_id(), self, [0, 0])
                self.schedule.add(agent)

    def reproduce(self, max_child=4):
        """
        Function to generate the new population from the parent individuals
        1. Sample individuals from current population and Generate pairs of individuals
        2. Create the new generation within a range, defining inherited genotype (cross-over and mutation applied)
        3. Add the new generation of agents to the model
        4. Remove all the "old" agents from the model
        """

        # 1
        agents = random.sample([agent for agent in self.schedule.agents], k=self.schedule.get_agent_count())

        for i in range(0, len(agents)-1, 2):
            agent1 = agents[i]
            agent2 = agents[i + 1]
            n_child = random.randint(2, max_child)

            # 2
            for j in range(n_child):
                if random.random() < self.cr:
                    child_genotype = crossover(agent1, agent2)
                else:
                    child_genotype = agent1.genotype if random.random() < 0.50 else agent2.genotype

                gen1 = child_genotype[0]
                gen2 = child_genotype[1]

                if random.random() < self.mr:
                    gen1 = 1 - gen1

                if random.random() < self.mr:
                    gen2 = 1 - gen2

                child = BeardAgent(self.next_id(), self, [gen1, gen2])

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
            If there are two agents, one of them is randomly notified of the danger. Depending on its genotype:

            1.1: one agent has the green-beard genotype and the other the altruistic genotype,
                 the agent notified of the danger (with the altruistic allele) sacrifice itself (altruist) and save the
                 other agent carrying the green-beard allele.
            1.2: at least one agent has the non-green-beard genotype,
                 independently of the genotype of the agent notified of the danger, one of them will die
        """

        # creating the "interaction rooms"
        # proportion of the dangerous rooms is computed in such a way to ensure enough agents survive to
        # generate the next generation according to the predefined scenario (linkage eq. or diseq.)
        num_agents = len(self.schedule.agents)
        rooms_number = num_agents

        if not self.linkage_dis:
            danger_number = num_agents // 1.893
        else:
            danger_number = num_agents // 1.9

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

        # action of each agent - Scenario 1
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
                if gen1[0] and gen2[1]:
                    if random.random() < self.dr:
                        self.schedule.remove(agent1)
                # 1.2
                else:
                    self.schedule.remove(agent2)

        agents_id = [a.unique_id for a in self.schedule.agents]
        self.schedule.step(agents_id)

        self.reproduce()
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = BeardModelAdv()

    print("Initial freq TRUE BEARDS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq TRUE BEARDS
    print("Initial freq SUCKERS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq SUCKERS
    print("Initial freq IMPOSTORS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq IMPOSTORS
    print("Initial freq COWARDS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq COWARDS

    # initial frequency of green beard allele
    for i in range(500):
        model.step()

    print("Final freq TRUE BEARDS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq TRUE BEARDS
    print("Final freq SUCKERS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq SUCKERS
    print("Final freq IMPOSTORS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq IMPOSTORS
    print("Final freq COWARDS:", len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq COWARDS

