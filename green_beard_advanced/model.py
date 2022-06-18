import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler

import random
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.time import BaseScheduler


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


class BeardAgent(Agent):
    """
    an agent to simulate the altruistic behaviour based on relatedness
    """

    def __init__(self, unique_id, model, genotype):
        """
        genotype: 1 gene with 2 alleles (a list of 2 integers)
        allele1: 1 codes for altruism 0 for cowardice
        allele2: 1 code for beard 0 for non beard
        """
        super().__init__(unique_id, model)
        self.genotype = genotype


def crossover(agent1, agent2):
    """
    RECOMBINATION (CROSSOVER) one point
    """
    allele1 = agent1.genotype[0]
    allele2 = agent2.genotype[1]
    return [allele1, allele2]


class BeardModel(Model):
    """
    a model for simulation of the evolution of family related altruism
    """

    def __init__(self, N=500, r=0.25):
        """
        N: total number of agents
        r: initial ratio of each allele
        """
        self.schedule = RandomActivation(self)
        self.N = N
        self.tot_N = N
        # self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
        #     [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count()})

        # TODO: add datacollector

        for i in range(int(N * r)):
            agent = BeardAgent(i, self, [1, 1])
            self.schedule.add(agent)

        for i in range(int(N * r), 2 * int(N * r)):
            agent = BeardAgent(i, self, [1, 0])
            self.schedule.add(agent)

        for i in range(2 * int(N * r), 3 * int(N * r)):
            agent = BeardAgent(i, self, [0, 1])
            self.schedule.add(agent)

        for i in range(3 * int(N * r), N):
            agent = BeardAgent(i, self, [0, 0])
            self.schedule.add(agent)

        self.reproduce()
        # TODO: reproduction method

    def reproduce(self, max_child=4, cross_prob=0.02):
        """
        function to generate the new population from the parent individuals
        select 2 random agents. Decide randomly if they will do 2,3 or 4 children. Create children with genotype taken
        randomly from one of the 2 parents
        """
        # print()
        agents = random.sample([agent for agent in self.schedule.agents], k=len(self.schedule.agents))
        for i in range(0, len(agents) - 1, 2):
            self.tot_N += 1
            agent1 = agents[i]
            agent2 = agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                self.tot_N += 1
                if random.random() < cross_prob:
                    child_genotype = crossover(agent1, agent2)
                else:
                    child_genotype = agent1.genotype if random.random() < 0.50 else agent2.genotype

                child = BeardAgent(self.tot_N, self, child_genotype)
                self.schedule.add(child)
            # print("è natooo")
            # print("hanno bombato")
            self.schedule.remove(agent1)
            self.schedule.remove(agent2)

    def step(self) -> None:

        # creating the "interaction rooms"
        num_agents = len(self.schedule.agents)
        rooms_number = num_agents  # tot number of rooms
        # print("N: ", num_agents)
        danger_number = num_agents // 1.9  # we derived it from the wcs to have at least 500 individuals left,
        danger_dict = {}
        # dictionary in which the key is the room number and the value is the list of individuals in that room
        for i in range(int(danger_number)):
            danger_dict[i] = []

        # assign each agent to a tree
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

                if gen1[0] and gen2[1]:  #agent1 is altruistic and gen2 has green beard
                    if random.random() < 0.50:  # die with 0.50 probability
                        self.schedule.remove(agent1)
                else:
                    self.schedule.remove(agent2)

        self.reproduce()
        # self.datacollector.collect(self)


if __name__ == "__main__":
    model = BeardModel()
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq TRUE BEARDS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 1 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq SUCKERS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 1]) / model.schedule.get_agent_count())  # freq IMPOSTORS
    print(len([a for a in model.schedule.agent_buffer() if
               a.genotype[0] == 0 and a.genotype[1] == 0]) / model.schedule.get_agent_count())  # freq COWARDS

    # initial frequency of green beard allele
    for i in range(400):
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
