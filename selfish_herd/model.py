import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from math import sqrt
from mesa.time import BaseScheduler

dist = lambda x, y: sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))


def creature_food_stat(model):
    """
    collects data about creature mean food
    """
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "creature"]
    if len(agent_food) > 0:
        return sum(agent_food) / len(agent_food)


def predator_food_stat(model):
    """
    collects data about predator mean food
    """
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "predator"]
    if len(agent_food) > 0:
        return sum(agent_food) / len(agent_food)


class PreyAgent(Agent):
    """A Food Agent seeking survival."""

    def __init__(self, unique_id, model, genotype: list, type: str, sight=None):
        """
        Prey Agent init function
        Type can be either food or creature #in questo caso non teniamo però conto del food
        """
        super().__init__(unique_id, model)
        self.hp = 5
        self.genotype = genotype
        self.type = type
        self.sight = sight

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        if self.type != "food":
            self.move()
            self.eat()
            self.hp -= 0.2 + 0.1 * self.hp

    def move(self):
        """
        function to move creatures
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                          include_center=False)  # all the cells at dist = 1

        # TODO define the movement according to the genotype of the creatures
        # Every agent has a genotype described by a number [-1, 1] that influence its behaviour
        # -1 encodes for "run", 1 encodes for "form a herd"

        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        nb = [x.pos for x in nb if x.type == "food"] if self.type == "creature" \
            else [x.pos for x in nb if x.type == "creature"]  # food ad distance r = sight, we may optimize it

        if len(nb) > 0:
            nearest_food = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            new_position = min(possible_steps, key=lambda x:
                sqrt(((nearest_food[0] - x[0]) ** 2) + ((nearest_food[1] - x[1]) ** 2)))
        else:
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def eat(self):
        # questa funzione per ora non serve, non guardiamo alla fitness come livello di cibo ma come sopravvivenza
        #function to eat if there is something at hand

        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        foodtype = "food" if self.type == "creature" else "creature"
        for a in cellmates:
            if a.type == foodtype:
                self.model.grid.move_to_empty(a)
                self.hp += 5
                break


class PredatorAgent(Agent):
    """A Food Agent seeking survival."""

    def __init__(self, unique_id, model, type: str, sight=None):
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
        self.hp -= 0.2 + 0.1 * self.hp

    def move(self):
        """
        function to move creatures and predators
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                          include_center=False)  # all the cells at dist = 1

        # TODO consider only movement towards creatures

        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        nb = [x.pos for x in nb if x.type == "food"] if self.type == "creature" \
            else [x.pos for x in nb if x.type == "creature"]  # food ad distance r = sight, we may optimize it

        if len(nb) > 0:
            nearest_food = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            self.hunt(nearest_food)
            return
        else:
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def hunt(self, nf):
        """
        "hunting" function to code for the behaviour of the predators
        nf: nearest creature
        """
        if dist(self.pos, nf) < 5:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False,
                                                              radius=4)  # all the cells at dist = 1
            new_position = min(possible_steps, key=lambda x: sqrt(((nf[0] - x[0]) ** 2) + ((nf[1] - x[1]) ** 2)))
            self.hp -= 0.5 * dist(self.pos, nf)
            self.model.grid.move_agent(self, new_position)


class FoodModel(Model):
    """A model with some number of food, creatures and predators."""

    # TODO non so se avere due tipi di agenti (prey e predator) nello stesso scheduler possa creare problemi

    def __init__(self, n_creatures: int, n_food: int, n_pred: int, sight: int, width: int, height: int, mr=0.001):
        """
        n_creatures: number of creatures
        n_food: number of food
        n_pred: number of predators
        sight: sight of creatures and predators
        """
        self.num_agents = n_creatures
        self.num_food = n_food
        self.num_pred = n_pred
        self.mr = mr
        self.sight = sight
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)

        self.running = True
        self.datacollector = DataCollector(model_reporters={
            "Mean creature food": creature_food_stat,
            "Mean predator food": predator_food_stat,
            "Number of creatures": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "creature"]),
            "Number of predators": lambda x: len(
                [agent for agent in x.schedule.agents if agent.type == "predator"])},
            agent_reporters={"Health": "hp"})

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

        for i in range(self.num_agents, self.num_agents + self.num_food):
            a = PreyAgent(i, self, type="food")
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents + self.num_food, self.num_agents + self.num_food + self.num_pred):
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

        for i in range(0, len(prey_agents)-1, 2):
            agent1 = prey_agents[i]
            agent2 = prey_agents[i + 1]
            n_child = random.randint(2, max_child)

            for j in range(n_child):
                gen1 = []
                if random.random() < self.mr:  #random mutation
                    gen1 = round(random.uniform(-1, 1), 2)
                child = PreyAgent(self.next_id(), self, genotype=gen1, type="creature", sight=self.sight)
                self.schedule.add(child)

            self.schedule.remove(agent1)
            self.schedule.remove(agent2)

        # Predator reproduction
        # non mi è chiaro se facciamo riprodurre anche loro oppure no ma in caso il codice è pronto
        pred_agents = random.sample([agent for agent in self.schedule.agents if agent.type == "predator"],
                                    k=self.schedule.get_agent_count())

        for i in range(0, len(pred_agents)-1, 2):
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
        self.datacollector.collect(self)
        self.schedule.step()
        for a in self.schedule.agents:
            if a.hp <= 0:
                self.grid.remove_agent(a)
                self.schedule.remove(a)
        if not [agent for agent in self.schedule.agents if agent.type == "creature"]:
            self.running = False


class CustomFoodModel(FoodModel):
    """
    Per testare nuove cose direi di creare nuove classi figlie e modificare quelle; aggiunginedo e
    modificando metodi quando serve.
    Può essere comod per integrare gli algo genetici sulla base di una classse già funzionante.

    """
    pass


class CustomFoodAgent(PreyAgent):
    """
     Per testare nuove cose direi di creare nuove classi figlie e modificare quelle; aggiunginedo e
     modificando metodi quando serve.
     Può essere comod per integrare gli algo genetici sulla base di una classse già funzionante.

     """
    pass

# TODO instead of fear, implement herds according to genotype

class RunningFoodAgent(PreyAgent):
    """
    Agent model with fear running from preds

     """

    def move(self):
        #### TODO: use numpy for the fector representation
        """
        function to move creatures and predators
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True,
                                                          include_center=False)  # all the cells at dist = 1
        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
        nb = [x.pos for x in nb if x.type == "food"] if self.type == "creature" \
            else [x.pos for x in nb if x.type == "creature"]  # food ad distance r = sight, we may optimize it
        fear_vect = self.panic()
        if len(nb) > 0 or fear_vect:
            mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
            move_vect = None
            if len(nb) > 0:
                nearest_food = min(nb, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
                move_vect = mov_vectorize(self.pos, nearest_food)
            if fear_vect:
                move_vect = mov_vectorize(fear_vect, move_vect) if move_vect else fear_vect  # sum prod fear + move

            # print(f"Agent ID: {self.unique_id}", f"Move vector: {move_vect}")

            if self.type == "predator":
                self.hunt(nearest_food)
                return
            else:
                vect_landing = [coord[0] - coord[1] for coord in zip(self.pos, move_vect)]
                new_position = min(possible_steps, key=lambda x: sqrt(
                    ((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))
        else:
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def panic(self):
        mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
        if self.type != "creature":
            return None
        else:
            np = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.sight)
            np = [x.pos for x in np if x.type == "predator"]
            if np:
                nearest_predator = min(np,
                                       key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
                return mov_vectorize(self.pos, [-x for x in nearest_predator])
            else:
                return None


class RunningFoodModel(FoodModel):
    """
    Model to test running agent with fear

    """

    def __init__(self, ncreatures: int, nfood: int, npred: int, sight: int, width: int, height: int):
        """
        ncreatures: number of creatures
        nfood: number of food
        npred: number of predators
        sight: sight of creatures and predators
        """
        self.num_agents = ncreatures
        self.num_food = nfood
        self.num_pred = npred
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.running = True

        self.datacollector = DataCollector(model_reporters={"Mean creature food": creature_food_stat,
                                                            "Mean predator food": predator_food_stat,
                                                            "Number of creatures": lambda x: len(
                                                                [agent for agent in x.schedule.agents if
                                                                 agent.type == "creature"]),
                                                            "Number of predators": lambda x: len(
                                                                [agent for agent in x.schedule.agents if
                                                                 agent.type == "predator"])},
                                           agent_reporters={"Health": "hp"})
        # Create agents
        for i in range(self.num_agents):
            genotype = [round(random.uniform(-1, 1), 2)]
            a = RunningFoodAgent(i, self, genotype=genotype, type="creature", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents, self.num_agents + self.num_food):
            a = RunningFoodAgent(i, self, genotype=[], type="food")
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents + self.num_food, self.num_agents + self.num_food + self.num_pred):
            a = RunningFoodAgent(i, self, genotype=[], type="predator", sight=sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
