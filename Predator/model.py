from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from math import sqrt


dist = lambda x, y: sqrt(((x[0]-y[0])**2) + ((x[1]-y[1])**2))


def creature_food_stat(model):
    """
    collects data about creature mean food
    """
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "creature"]
    if len(agent_food) > 0:
        return sum(agent_food)/len(agent_food)


def predator_food_stat(model):
    """
    collects data about predator mean food
    """
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "predator"]
    if len(agent_food) > 0:
        return sum(agent_food)/len(agent_food)


class FoodAgent(Agent):
    """An Food Agent seeking survival."""

    def __init__(self, unique_id, model, type: str, sight = None):
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
        if self.type != "food":
            self.move()
            self.eat()
            self.hp -= 0.2+ 0.1 * self.hp

    def move(self):
        """
        function to move creatures and predators
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)  #all the cells at dist = 1
        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius= self.sight)
        nb = [x.pos for x in nb if x.type == "food"] if self.type == "creature" \
            else [x.pos for x in nb if x.type == "creature"]  # food ad distance r = sight, we may optimize it

        if len(nb) > 0:
            nearest_food = min(nb, key = lambda x: sqrt(((self.pos[0]-x[0])**2) + ((self.pos[1]-x[1])**2)))

            if self.type == "predator":
                self.hunt(nearest_food)
                return
            else:
                new_position = min(possible_steps, key=lambda x: sqrt(((nearest_food[0] - x[0]) ** 2) + ((nearest_food[1] - x[1]) ** 2)))
        else:
            new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def eat(self):
        """
        function to eat if there is something at hand
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        foodtype = "food" if self.type == "creature" else "creature"
        for a in cellmates:
            if a.type == foodtype:
                self.model.grid.move_to_empty(a)
                self.hp += 5
                break

    def hunt(self, nf):
        """
        "hunting" function to code for the behaviour of the predators
        nf: nearest creature
        """
        if dist(self.pos, nf) < 5:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius= 4)  # all the cells at dist = 1
            new_position = min(possible_steps, key=lambda x: sqrt(((nf[0] - x[0]) ** 2) + ((nf[1] - x[1]) ** 2)))
            self.hp -= 0.5 * dist(self.pos, nf)
            self.model.grid.move_agent(self, new_position)


class FoodModel(Model):
    """A model with some number of food, creatures and predators."""

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

        self.datacollector = DataCollector(model_reporters= {"Mean creature food": creature_food_stat,
                                                             "Mean predator food": predator_food_stat,
                                                             "Number of creatures": lambda x: len([agent for agent in x.schedule.agents if agent.type == "creature"]),
                                                             "Number of predators": lambda x: len([agent for agent in x.schedule.agents if agent.type == "predator"])},
                                           agent_reporters={"Health": "hp"})
        # Create agents
        for i in range(self.num_agents):
            a = FoodAgent(i, self, "creature", sight= sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents, self.num_agents + self.num_food):
            a = FoodAgent(i, self, "food")
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents + self.num_food, self.num_agents + self.num_food + self.num_pred):
            a = FoodAgent(i, self, "predator", sight= sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

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


class CustomFoodAgent(FoodAgent):
    """
     Per testare nuove cose direi di creare nuove classi figlie e modificare quelle; aggiunginedo e
     modificando metodi quando serve.
     Può essere comod per integrare gli algo genetici sulla base di una classse già funzionante.

     """
    pass


class RunningFoodAgent(FoodAgent):
    """
    Agent model with fear running from preds

     """
    def move(self):
        """
        function to move creatures and predators
        """
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)  #all the cells at dist = 1
        nb = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius= self.sight)
        nb = [x.pos for x in nb if x.type == "food"] if self.type == "creature" \
            else [x.pos for x in nb if x.type == "creature"]  # food ad distance r = sight, we may optimize it
        fear_vect = self.panic()
        if len(nb) > 0 or fear_vect:
            mov_vectorize = lambda x, y: [coord[0] - coord[1] for coord in zip(x, y)]
            nearest_food = min(nb, key = lambda x: sqrt(((self.pos[0]-x[0])**2) + ((self.pos[1]-x[1])**2)))
            move_vect = mov_vectorize(self.pos, nearest_food)
            if fear_vect:
                move_vect = 0 #dot prod fear + move

            #print(f"Agent ID: {self.unique_id}", f"Move vector: {move_vect}")

            if self.type == "predator":
                self.hunt(nearest_food)
                return
            else:
                vect_landing = [coord[0]-coord[1] for coord in zip(self.pos, move_vect)]
                new_position = min(possible_steps, key=lambda x: sqrt(((vect_landing[0] - x[0]) ** 2) + ((vect_landing[1] - x[1]) ** 2)))
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
            nearest_predator = min(np, key=lambda x: sqrt(((self.pos[0] - x[0]) ** 2) + ((self.pos[1] - x[1]) ** 2)))
            return mov_vectorize(self.pos, nearest_predator)

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

        self.datacollector = DataCollector(model_reporters= {"Mean creature food": creature_food_stat,
                                                             "Mean predator food": predator_food_stat,
                                                             "Number of creatures": lambda x: len([agent for agent in x.schedule.agents if agent.type == "creature"]),
                                                             "Number of predators": lambda x: len([agent for agent in x.schedule.agents if agent.type == "predator"])},
                                           agent_reporters={"Health": "hp"})
        # Create agents
        for i in range(self.num_agents):
            a = RunningFoodAgent(i, self, "creature", sight= sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents, self.num_agents + self.num_food):
            a = RunningFoodAgent(i, self, "food")
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_agents + self.num_food, self.num_agents + self.num_food + self.num_pred):
            a = RunningFoodAgent(i, self, "predator", sight= sight)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
