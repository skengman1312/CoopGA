from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from math import sqrt


dist = lambda x, y: sqrt(((x[0]-y[0])**2) + ((x[1]-y[1])**2))

def food_stat(model):
    agent_food = [agent.hp for agent in model.schedule.agents if agent.type == "creature"]
    if len(agent_food) > 0:
        return sum(agent_food)/len(agent_food)

class FoodAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, type, sight = None):
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
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False) #all the cells at dist = 1
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
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        foodtype = "food" if self.type == "creature" else "creature"
        for a in cellmates:
            if a.type == foodtype:
                self.model.grid.move_to_empty(a)
                self.hp += 5
                break

    def hunt(self, nf):
        if dist(self.pos, nf) < 5:
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius= 4)  # all the cells at dist = 1
            new_position = min(possible_steps, key=lambda x: sqrt(((nf[0] - x[0]) ** 2) + ((nf[1] - x[1]) ** 2)))
            self.hp -= 0.5 * dist(self.pos, nf)
            self.model.grid.move_agent(self, new_position)



class FoodModel(Model):
    """A model with some number of agents."""

    def __init__(self, ncreatures, nfood, npred,sight, width, height):
        self.num_agents = ncreatures
        self.num_food = nfood
        self.num_pred = npred
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.running = True

        self.datacollector = DataCollector(model_reporters= {"Mean food": food_stat,
                                                             "Number of creatures": lambda x: len([agent for agent in x.schedule.agents if agent.type == "creature"])},
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



