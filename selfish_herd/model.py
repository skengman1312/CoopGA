import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from math import sqrt

dist = lambda x, y: sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))
mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]


class PredatorAgent(Agent):
    """A Predator Agent seeking for prey agents."""

    def __init__(self, unique_id, model, sight, jump_range=3, type="predator"):
        """
        Predator Agent init function
        :param unique_id: a unique numeric identifier for the agent model
        :type unique_id: int
        :param model:  instance of the model that contains the agent
        :type model: mesa.model
        :param sight: maximum distance radio of interaction with other agents
        :type sight: int
        :param jump_range: maximum range within which predator can hunt a creature
        :type jump_range: int
        :param type: identifier of the agent type, namely all the agents belonging to this class
        :type type: str
        """

        super().__init__(unique_id, model)
        self.hp = 0
        self.type = type
        self.sight = sight
        self.rest_time = sight
        self.jump_range = jump_range

    def step(self):
        """
        A single step of the agent which consists in moving or resting based on hp.
        hp keeps track of the steps between the current one and the one in which the agent ate a prey.
        """

        if self.hp == 0:
            self.move()
        else:
            self.hp -= 1

    def move(self):
        """
        Implementation of agent move according to distance and possible interaction with other agents.
        Scenario 1 - at least one creature in the sight radius
            1.1: the nearest creature is in the jump_range, the agent hunts it
            1.2: the nearest creature is not in the jump_range, the agent chases it
        Scenario 2 - no creatures in the sight radius, random move
        """

        all_possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        possible_steps = [x for x in all_possible_steps if self.model.grid.is_cell_empty(x)]

        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        nb = [x.pos for x in nb if x.type == "creature"]

        # Scenario 1
        if nb:
            nearest_prey = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            if dist(nearest_prey, self.pos) < self.jump_range:
                self.hunt(nearest_prey)

            else:
                if possible_steps:
                    new_position = self.chase(nearest_prey, possible_steps)
                    self.model.grid.move_agent(self, new_position)

        # Scenario 2
        else:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def chase(self, nearest_prey, possible_steps):
        """
        Implementation of agent chasing action.

        :param nearest_prey: position of the nearest creature, namely x and y coordinates
        :type nearest_prey: tuple
        :param possible_steps: all possible cells in which the agent can move defined by x and y coordinates
        :type np: tuple
        """
        move_vector = mov_vectorize(self.pos, nearest_prey)
        vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vector)]
        return min(possible_steps, key=lambda x: sqrt(
            ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))

    def eat(self):
        """
        Implementation of agent eating action.
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for a in cellmates:
            if a.type == "creature":
                self.model.schedule.remove(a)
                self.model.grid.remove_agent(a)
                self.hp = self.rest_time
                break

    def hunt(self, np):
        """
        Implementation of agent hunting action.

        :param np: position of the nearest creature, namely x and y coordinates
        :type np: tuple
        :type np: tuple
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=4)
        new_position = min(possible_steps, key=lambda x: sqrt(((np[0] - x[0]) ** 2) + ((np[1] - x[1]) ** 2)))
        self.model.grid.move_agent(self, new_position)
        self.eat()


class PreyAgent(Agent):
    """A Prey Agent."""

    def __init__(self, unique_id, model, genotype: list, type="creature", sight=None):
        """
        Prey Agent init function

        :param unique_id: a unique numeric identifier for the agent model
        :type unique_id: int
        :param model:  instance of the model that contains the agent
        :type model: mesa.model
        :param genotype: representation of single-gene genotype in [-1,1] (-1: non-selfish, 1: selfish)
        :type genotype: list
        :param type: identifier of the agent type, namely all the agents belonging to this class
        :type type: str
        :param sight: maximum distance radio of interaction with other agents
        :type sight: int
        """

        super().__init__(unique_id, model)
        self.genotype = genotype
        self.type = type
        self.sight = sight

    def step(self):
        """
        A single step of the agent which consists in moving.
        The agent moves only if there is at least one empty cell in neighbour cells.
        """
        all_possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        possible_steps = [x for x in all_possible_steps if self.model.grid.is_cell_empty(x)]

        if possible_steps:
            self.move(possible_steps)

    def move(self, possible_steps):
        """
        Implementation of agent move according to distance and possible interaction with other agents.

        :param possible_steps: all possible cells in which the agent can move defined by x and y coordinates
        :type possible_steps: tuple

        Scenario 1 - at least one agent in the sight radius
            1.1: the agents in the sight radius are all creatures,
                 the agent moves according to the center of mass of the others agents weighted by the genotype
                 - negative genotype [-1,0[ -> the agent move in the opposite direction wrt the center of mass
                 - positive genotype [0,1] -> the agent move in the direction of the center of mass
            1.2: the agents in the sight radius are all predators,
                 the agent runs away in the opposite direction wrt the nearest predator
                 (if more than one predator, it moves in the opposite direction wrt the center of mass of the predators)
            1.3: the agents in the sight radius are creatures and predators,
                 the agent runs away in the opposite direction wrt the nearest predator
        Scenario 2 - no agents in the sight radius, random move
        """

        np = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        npredator = [x.pos for x in np if x.type == "predator"]
        nprey = [x.pos for x in np if x.type == "creature"]

        fear_vect = None
        if npredator:
            fear_vect = self.panic(npredator)

        # Scenario 1
        if len(nprey) > 0 or fear_vect:
            move_vect = None

            if len(nprey) > 0:
                prey_cm_x = sum(x[0] for x in nprey) / len(nprey)
                prey_cm_y = sum(y[1] for y in nprey) / len(nprey)
                cm_vect = [prey_cm_x, prey_cm_y]
                move_vect = mov_vectorize(self.pos, cm_vect)
                move_vect = [round(self.genotype[0] * x, 2) for x in move_vect]

            if fear_vect:
                move_vect = fear_vect

            vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vect)]
            new_position = min(possible_steps, key=lambda x: sqrt(
                ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))

        # Scenario 2
        else:
            new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)

    def panic(self, npredator):
        """
        Implementation of fear vector, namely the distance between the creature and the nearest predator.

        :param npredator: positions (x and y coordinates) of all predators in the sight radius of the agent
        :type npredator: tuple
        """
        # TODO CENTRE OF MASS OF PREDATORS
        # se c'è più di un predator scappi da entrambi e non solo dal nearest

        nearest_predator = min(npredator,
                               key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
        return mov_vectorize([x for x in nearest_predator], self.pos)


class HerdModel(Model):
    """
    A model for simulation of the evolution.

    :param Model: the model class for Mesa framework
    :type Model: mesa.model
    """

    def __init__(self, n_creatures: int, n_pred: int, sight: int, jump_range: int, mr: int, width: int, height: int):
        """
        HerdModel init function

        :param n_creatures: total number of PreyAgents
        :type n_creatures: int
        :param n_pred: total number of PredatorAgents
        :type n_pred: int
        :param sight: maximum distance radio of interaction of Predators with Preys agents
        :type sight: int
        :param jump_range: maximum range within which predator can hunt a creature
        :type jump_range: int
        :param mr: mutation rate
        :type mr: float
        :param width, height: The mesa grid’s width and height
        :type width, height: int
        """

        self.num_agents = n_creatures
        self.num_pred = n_pred
        self.sight = sight
        self.mr = mr
        self.jump_range = jump_range
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.current_id = 0

        self.running = True
        self.datacollector = DataCollector(model_reporters={
            "Number of creatures": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "creature"]),
            "Number of predators": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "predator"]),
            "n_agents": lambda x: x.schedule.get_agent_count(),
            "Selfish gene frequency": lambda x: len(
                [a for a in x.schedule.agents if a.type == "creature" and a.genotype[0] >= 0]) /
                                        len([agent for agent in x.schedule.agents if agent.type == "creature"])
            if len([agent for agent in x.schedule.agents if agent.type == "creature"]) != 0 else 0,
            "Fear frequency": lambda x: len(
                [a for a in x.schedule.agents if a.type == "creature" and a.genotype[0] < 0]) /
                                        len([agent for agent in x.schedule.agents if agent.type == "creature"])
            if len([agent for agent in x.schedule.agents if agent.type == "creature"]) != 0 else 0})

        # TODO SISTEMARE IL DATA COLLECTOR
        self.add_agents(n_creatures, n_pred)

    def add_agents(self, num_agents, num_pred):
        """
        Add agents to the model. PreyAgents will be initialized with the same frequencies for -1 and 1 genotypes.

        :param num_agents: total number of PreyAgents
        :type num_agents: int
        :param num_pred: total number of PredatorAgents
        :type num_pred: int
        """

        # adding selfish PreyAgents (genotype = 1)
        for i in range(0, num_agents // 2):
            a = PreyAgent(self.next_id(), self, genotype=[1], type="creature", sight=self.sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # adding non-selfish PreyAgents (genotype = -1)
        for i in range(0, num_agents // 2):
            a = PreyAgent(self.next_id(), self, genotype=[-1], type="creature", sight=self.sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(0, num_pred):
            a = PredatorAgent(self.next_id(), self, type="predator", sight=self.sight, jump_range=self.jump_range)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def reproduce(self, max_child=4):
        """
        Function to generate the new population from the parent PreyAgents
        1. Sample PreyAgents from current population and generate pairs of individuals
        2. Create the new generation within a range, defining inherited genotype (mutation applied)
        3. Add the new generation of agents to the model and to the grid (in a random position)
        4. Remove all the "old" agents from the model and the grid
        """
        # TODO PROBLEMI CON LA REPRODUCTION, PROVARE CON k=self.num_agents
        # loro fanno il reproduce sopra

        # 1
        preys = [agent for agent in self.schedule.agents if agent.type == "creature"]
        prey_agents = random.sample(preys, k=len(preys))

        # 2
        for i in range(0, len(prey_agents) - 1, 2):
            agent1 = prey_agents[i]
            agent2 = prey_agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                gen1 = [agent1.genotype[0] if random.random() < 0.50 else agent2.genotype[0]]

                """# TODO MUTATION
                if random.random() < self.mr:  # random mutation
                    gen1[0] = round(random.uniform(-1, 1), 2)"""

                child = PreyAgent(self.next_id(), self, genotype=gen1, type="creature", sight=self.sight)

                # 3
                self.schedule.add(child)

                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(child, (x, y))

            # 4
            self.schedule.remove(agent1)
            self.schedule.remove(agent2)
            self.grid.remove_agent(agent1)
            self.grid.remove_agent(agent2)

    def step(self):
        """
        Model step
        Reproduction is performed every time the number of creatures reaches a threshold.
        """
        # TODO FORSE MEGLIO FARE LA REPRODUCTION OGNI TOT STEP?

        self.schedule.step()

        n_creature = len([agent for agent in self.schedule.agents if agent.type == "creature"])
        if n_creature <= self.num_agents / 1.5:
            self.reproduce()

        """if len([a for a in self.schedule.agents if a.type == "creature" and a.genotype[0]]) / n_creature == 0: #selfish frequency == 0
            self.running = False"""

        self.datacollector.collect(self)
