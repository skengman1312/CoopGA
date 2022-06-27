import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
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
        return sum(agent_food)/len(agent_food)


class PredatorAgent(Agent):
    """A Predator Agent seeking for prey agents."""

    def __init__(self, unique_id, model, type="predator", sight=10):
        """
        Food Agent init function
        Type can be either food, creature or predator
        """
        super().__init__(unique_id, model)
        self.hp = 5
        self.type = type
        self.sight = sight

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        self.move()
        self.eat()

    def move(self):
        """
        function to move creatures and predators
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                          include_center=False)  # all the cells at dist = 1

        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        #print(nb)
        nb = [x.pos for x in nb if x.type == "creature"]
        # consider only the "creature" agents as possible food
        # food ad distance r = sight, we may optimize it

        if len(nb) > 0:
            nearest_pray = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            self.hunt(nearest_pray)
            #self.model.schedule.remove(nearest_pray)
            #self.grid.remove_agent(nearest_pray)
            return
        else:
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

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

        if dist(self.pos, nf) < 5:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=4)
        # all the cells at dist = 1

            new_position = min(possible_steps, key=lambda x: sqrt(((nf[0] - x[0]) ** 2) + ((nf[1] - x[1]) ** 2)))
        #self.hp -= 0.5 * dist(self.pos, nf)
            self.model.grid.move_agent(self, new_position)

        else:
            return


# TODO instead of fear, implement herds according to genotype

class PreyAgent(Agent):
    """
    Agent model with fear running from pred
    """
    def __init__(self, unique_id, model, genotype: list, type ="creature", sight=None, ):
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
        # TODO: use numpy for the fector representation
        """
        function to move creatures
        if a predator:
            - move toward the nearest creature (vector weighted by the genotype)
            - if no creature, move in the opposite direction wrt the predator
        if no predator, random move
        """
        all_possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                          include_center=False)  # all the cells at dist = 1

        possible_steps = [x for x in all_possible_steps if self.model.grid.is_cell_empy(x)]
        fear_vect = self.panic()
        print("fear vector:", fear_vect)
        print("self.position:", self.pos)

        np = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        npredator = [x.pos for x in np if x.type == "predator"]
        nprey = [x.pos for x in np if x.type == "creature"]

        mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
        #print("move_vectorize", mov_vectorize)
        move_vect = None
        """
        if fear_vect:
            if nprey:
                # TODO Se sono già in un herd devono muoversi tutti asseme? Cosa succede?

                print(nprey)
                nearest_prey = min(nprey, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
                print("nearest prey:", nearest_prey)
                move_vect = mov_vectorize(nearest_prey, move_vect) if move_vect else nearest_prey  # sum prod nearest prey + move
                vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vect)]
                new_position = min(possible_steps, key=lambda x: sqrt(
                    ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))
            else:
                move_vect = mov_vectorize(fear_vect, move_vect) if move_vect else fear_vect  # sum prod fear + move
                vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vect)]
                new_position = min(possible_steps, key=lambda x: sqrt(
                    ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))
        else:
            new_position = self.random.choice(possible_steps)

        print(new_position)
        self.model.grid.move_agent(self, new_position)


            """ 
        if len(nprey) > 0 or fear_vect:

            mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
            move_vect = None

            # TODO GENOTYPE

            if len(nprey) > 0:
                nearest_prey = min(nprey, key=lambda x: sqrt(((self.pos[0]-x[0])**2) + ((self.pos[1]-x[1])**2)))
                move_vect = mov_vectorize(self.pos, nearest_prey)
            if fear_vect:
                move_vect = mov_vectorize(fear_vect, move_vect) if move_vect else fear_vect #sum prod fear + move -> scappa

                #print(f"Agent ID: {self.unique_id}", f"Move vector: {move_vect}")

            vect_landing = [coord[0]-coord[1] for coord in zip(self.pos, move_vect)]
            new_position = min(possible_steps, key=lambda x: sqrt(((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))

        else:
            new_position = self.pos
            #new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)

    def panic(self):

        mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]

        #retrieve positions of all predators
        np = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        npredator = [x.pos for x in np if x.type == "predator"]
        nprey = [x.pos for x in np if x.type == "creature"]


        #if there is at least one predator (np = True if len(np)>0)
        if npredator:
            #find the nearest predator using the euclidean distance
            #key function specify how to compute the minimum (x is each element in np list)
            nearest_predator = min(npredator, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            print("nearest predator:", nearest_predator)

            # TODO add weight for genotype
            #return mov_vectorize(self.pos, [-x for x in nearest_predator])
            return mov_vectorize([x for x in nearest_predator], self.pos )

        return None


class HerdModel(Model):
    """A model with some number of food, creatures and predators."""

    # TODO non so se avere due tipi di agenti (prey e predator) nello stesso scheduler possa creare problemi

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

        self.running = True
        self.datacollector = DataCollector(model_reporters={
            "Mean predator food": predator_food_stat,
            "Number of creatures": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "creature"]),
            "Number of predators": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "predator"])})#,
            #agent_reporters={"Health": "hp"})

        # Create agents
        # Every prey has a genotype described by a number [-1, 1] that influence its behaviour
        # -1 encodes for "run", 1 encodes for "form a herd"
        for i in range(self.num_agents):
            genotype = [round(random.uniform(-1, 1), 2)]
            a = PreyAgent(i, self, genotype=genotype, type="creature", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents, self.num_agents + self.num_pred):
            a = PredatorAgent(i, self, type="predator", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def reproduce(self, max_child=4):
        """
        function to generate the new population from the parent individuals both for prey and predators
        select 2 random agents. Decide randomly if they will do 2,3 or 4 children. Create children with genotype taken
        randomly from one of the 2 parents
        During the reproduction there is the chance of mutation
        """

        # Prey reproduction
        prey_agents = random.sample([agent for agent in self.schedule.agents if agent.type == "creature"],
                                    k=self.schedule.get_agent_count())

        for i in range(0, len(prey_agents) - 1, 2):
            agent1 = prey_agents[i]
            agent2 = prey_agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                gen1 = []
                if random.random() < self.mr:  # random mutation
                    gen1 = round(random.uniform(-1, 1), 2)
                child = PreyAgent(self.next_id(), self, genotype=gen1, type="creature", sight=self.sight)
                self.schedule.add(child)

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)

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
            self.schedule.remove(agent2)

    def step(self):
        """Advance the model by one step."""
        #self.datacollector.collect(self)
        self.schedule.step()
        self.datacollector.collect(self)
        """ for a in self.schedule.agents:
            if a.hp <= 0:
                self.grid.remove_agent(a)
                self.schedule.remove(a)"""
        if not [agent for agent in self.schedule.agents if agent.type == "creature"]:
            self.running = False

