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
        genotype: 1 codes for altruism 0 for cowardice
        """
        super().__init__(unique_id, model)
        self.genotype = genotype


class BeardModel(Model):
    """
    a model for simulation of the evolution of family related altruism
    """

    def __init__(self, N=500, r=0.5, sr=0.95, mr=0.001):
        """
        N: total number of agents
        r: initial ratio of altruistic allele
        sr: survival rate
        mr: mutation rate
        """
        self.schedule = RandomActivation(self)
        self.N = N
        self.tot_N = N
        self.mr = mr
        self.sr = sr
        # self.datacollector = DataCollector(model_reporters={"altruistic fraction": lambda x: len(
        #     [a for a in x.schedule.agent_buffer() if a.genotype == 1]) / x.schedule.get_agent_count()})


        # TODO: add datacollector

        for i in range(int(N * r)):
            agent = BeardAgent(i, self, 1)
            self.schedule.add(agent)

        for i in range(int(N * r), N):
            agent = BeardAgent(i, self, 0)
            self.schedule.add(agent)

        self.reproduce()
        # TODO: reproduction method

    def reproduce(self, max_child=4):
        """
        function to generate the new population from the parent individuals
        select 2 random agents. Decide randomly if they will do 2,3 or 4 children. Create children with genotype taken
        randomly from one of the 2 parents
        """
        #print()
        agents = random.sample([agent for agent in self.schedule.agents], k= len(self.schedule.agents))

        for i in range(0, len(agents)-1, 2):
            agent1 = agents[i]
            agent2 = agents[i+1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                self.tot_N += 1
                child_genotype = agent1.genotype if random.random() < 0.50 else agent2.genotype
                mutate = lambda x: x if random.random() > self.mr else 1 - x
                # 0. is 1-mutation rate: 1-0.03 = 0.97 in accordance to bio findings
                child_genotype = mutate(child_genotype)
                child = BeardAgent(self.tot_N, self, child_genotype)

                self.schedule.add(child)

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)


    def step(self) -> None:

        # creating the "interaction rooms"
        num_agents = len(self.schedule.agents)
        rooms_number = num_agents  # tot number of rooms
        #print("N: ", num_agents)
        danger_number = num_agents // 1.5  # we derived it from the wcs to have at least 500 individuals left,
        danger_dict = {}  # dictionary in which the key is the room number and the value is the list of individuals in that room
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
                if gen1 and gen2:  # both green beard
                    if random.random() < 0.50: # die with 0.50 probability
                        self.schedule.remove(agent1)
                else:  # both cowardice or 1 cowardice and 1 altruistic, one of the 2 dies.
                    self.schedule.remove(agent1)

        self.reproduce()
        # self.datacollector.collect(self)


if __name__ == "__main__":
    model = BeardModel()
    print(len([a for a in model.schedule.agent_buffer() if a.genotype == 1]) / model.schedule.get_agent_count())
    # initial frequency of green beard allele
    for i in range(400):
        print("step: ", i)
        model.step()
    print("number of agents: ", model.schedule.get_agent_count())
    print(len([a for a in model.schedule.agent_buffer() if a.genotype == 1])/model.schedule.get_agent_count() )
    # frequency of green beard allele
    print("yee")
