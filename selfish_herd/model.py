import random
from typing import List, Any

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.space import Grid
from mesa.datacollection import DataCollector
from math import sqrt
from mesa.time import BaseScheduler

dist = lambda x, y: sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))


def predator_food_stat(model):
    """
    collects data about predator mean food
    """
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "predator"]
    if len(agent_food) > 0:
        return sum(agent_food) / len(agent_food)


class PredatorAgent(Agent):
    """A Predator Agent seeking for prey agents."""

    def __init__(self, unique_id, model, type="predator", sight=10, rest_time=5):
        """
        Food Agent init function
        Type can be either food, creature or predator
        """
        super().__init__(unique_id, model)
        self.count_rest = 0
        self.rest_time = rest_time
        self.type = type
        self.sight = sight

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        if self.count_rest>0:
            self.move()


    def move(self):
        """
        function to move creatures and predators
        """
        mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]

        all_possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                              include_center=False)  # all the cells at dist = 1
        possible_steps = [x for x in all_possible_steps if self.model.grid.is_cell_empty(x)]

        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        # print(nb)
        nb = [x.pos for x in nb if x.type == "creature"]
        # consider only the "creature" agents as possible food
        # food ad distance r = sight, we may optimize it

        if nb:
            nearest_prey = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            if dist(nearest_prey, self.pos) < 5:
                self.hunt(nearest_prey)
            else:  # follow the prey
                move_vector = mov_vectorize(self.pos, nearest_prey)
                vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vector)]
                if possible_steps:
                    new_position = min(possible_steps, key=lambda x: sqrt(
                        ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))
                    self.model.grid.move_agent(self, new_position)
                self.hp = self.hp - 1 if self.hp > 0 else self.hp
            # self.model.schedule.remove(nearest_pray)
            # self.grid.remove_agent(nearest_pray)
        else:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
            self.hp = self.hp - 1 if self.hp else self.hp

    def eat(self):
        """
        function to eat if there is something at hand
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for a in cellmates:
            if a.type == "creature":
                self.model.schedule.remove(a)
                self.model.grid.remove_agent(a)
                self.hp += 5
                break

    def hunt(self, nf):

        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=4)
        # all the cells at dist = 1

        new_position = min(possible_steps, key=lambda x: sqrt(((nf[0] - x[0]) ** 2) + ((nf[1] - x[1]) ** 2)))
        # self.hp -= 0.5 * dist(self.pos, nf)
        self.model.grid.move_agent(self, new_position)
        self.eat()


class PreyAgent(Agent):
    """
    Agent model with fear running from pred
    """

    def __init__(self, unique_id, model, genotype: list, type="creature", sight=None, ):
        """
        Food Agent init function
        Type can be either food, creature or predator
        """
        super().__init__(unique_id, model)
        self.genotype = genotype
        self.type = type
        self.sight = sight

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        self.move()

    def move(self):
        """
        function to move creatures
        if a predator:
            - move toward the nearest creature (vector weighted by the genotype)
            - if no creature, move in the opposite direction wrt the predator
        if no predator, random move
        """
        all_possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                              include_center=False)  # all the cells at dist = 1

        possible_steps = [x for x in all_possible_steps if self.model.grid.is_cell_empty(x)]

        # print("self.position:", self.pos)

        np = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        npredator = [x.pos for x in np if x.type == "predator"]
        nprey = [x.pos for x in np if x.type == "creature"]

        mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
        # print("move_vectorize", mov_vectorize)

        if possible_steps:

            fear_vect = self.panic(npredator, mov_vectorize)
            # print("fear vector:", fear_vect)
            # print(len(nprey))
            # print("fear vector:", fear_vect)
            # print(len(nprey))
            if len(nprey) > 0 or fear_vect:

                # add the contribution of both the nearest creature and the nearest predator
                move_vect = None

                # TODO GENOTYPE

                if len(nprey) > 0:
                    nearest_prey = min(nprey,
                                       key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
                    # print("nearest prey", nearest_prey)
                    move_vect = mov_vectorize(self.pos, nearest_prey)
                    # print(f"Agent ID: {self.unique_id}", f"Move vector: {move_vect}", f"Genotype: {self.genotype}")
                    move_vect = [round(self.genotype[0] * x, 2) for x in move_vect]
                    # print("move vect", move_vect)

                if fear_vect:
                    # print("fear vector:", fear_vect)
                    move_vect = mov_vectorize(fear_vect,
                                              move_vect) if move_vect else fear_vect  # sum prod fear + move -> scappa

                    # print(f"Agent ID: {self.unique_id}", f"Move vector: {move_vect}")

                vect_landing: list[Any] = [coord[0] - coord[1] for coord in zip(self.pos, move_vect)]
                new_position = min(possible_steps, key=lambda x: sqrt(
                    ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))

            else:
                new_position = self.random.choice(possible_steps)

        else:
            new_position = self.pos

        # print("new position", new_position)
        self.model.grid.move_agent(self, new_position)

    def panic(self, npredator, mov_vectorize):

        # if there is at least one predator (np = True if len(np)>0)
        if npredator:
            # find the nearest predator using the euclidean distance
            # key function specify how to compute the minimum (x is each element in np list)
            nearest_predator = min(npredator,
                                   key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            # print("nearest predator:", nearest_predator)

            # return mov_vectorize(self.pos, [-x for x in nearest_predator])
            return mov_vectorize([x for x in nearest_predator], self.pos)

        return None


# TODO think about adding rest time as hyperparameter
class HerdModel(Model):
    """A model with some number of food, creatures and predators."""

    def __init__(self, n_creatures: int, n_pred: int, sight: int, mr: int, width: int, height: int):
        """
        n_creatures: number of creatures
        n_pred: number of predators
        sight: sight of creatures and predators
        """
        self.num_agents = n_creatures
        self.num_pred = n_pred
        self.sight = sight
        self.mr = mr
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.current_id = 0
        # self.grid = Grid(width, height, True)

        self.running = True
        self.datacollector = DataCollector(model_reporters={
            "Mean predator food": predator_food_stat,
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
            if len([agent for agent in x.schedule.agents if agent.type == "creature"]) != 0 else 0
        })  # ,
        # agent_reporters={"Health": "hp"})

        # Create agents
        # Every prey has a genotype described by a number [-1, 1] that influence its behaviour
        # -1 encodes for "run", 1 encodes for "form a herd"
        for i in range(self.num_agents // 2):
            genotype = [1]
            a = PreyAgent(self.next_id(), self, genotype=genotype, type="creature", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents // 2):
            genotype = [-1]
            a = PreyAgent(self.next_id(), self, genotype=genotype, type="creature", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(0, self.num_pred):
            a = PredatorAgent(self.next_id(), self, type="predator", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def reproduce(self, max_child=10):
        """
        function to generate the new population from the parent individuals both for prey and predators
        select 2 random agents. Decide randomly if they will do 2,3 or 4 children. Create children with genotype taken
        randomly from one of the 2 parents
        During the reproduction there is the chance of mutation
        """

        # Prey reproduction
        preys = [agent for agent in self.schedule.agents if agent.type == "creature"]
        prey_agents = random.sample(preys, k=len(preys))

        for i in range(0, len(prey_agents) - 1, 2):
            agent1 = prey_agents[i]
            agent2 = prey_agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                gen1 = []
                gen1.append(agent1.genotype[0] if random.random() < 0.50 else agent2.genotype[0])

                if random.random() < self.mr:  # random mutation
                    gen1[0] = round(random.uniform(-1, 1), 2)

                child = PreyAgent(self.next_id(), self, genotype=gen1, type="creature", sight=self.sight)

                self.schedule.add(child)

                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(child, (x, y))

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)
            self.grid.remove_agent(agent1)
            self.grid.remove_agent(agent2)

        """
        # Predator reproduction
        # non mi è chiaro se facciamo riprodurre anche loro oppure no ma in caso il codice è pronto
        pred_agents = random.sample([agent for agent in self.schedule.agents if agent.type == "predator"],
                                    k=self.schedule.get_agent_count())

        for i in range(0, len(pred_agents) - 1, 2):
            agent1 = pred_agents[i]
            agent2 = pred_agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                child = PredatorAgent(self.next_id(), self, type="predator", sight=self.sight)
                self.schedule.add(child)

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)"""

    def step(self):
        """Advance the model by one step."""

        self.schedule.step()

        """ for a in self.schedule.agents:
            if a.hp <= 0:
                self.grid.remove_agent(a)
                self.schedule.remove(a)"""
        if len([agent for agent in self.schedule.agents if agent.type == "creature"]) <= 40:
            self.reproduce()

        if not [agent for agent in self.schedule.agents if agent.type == "creature"]:
            self.running = False

        self.datacollector.collect(self)
