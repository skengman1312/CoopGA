from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class FoodAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, type):
        super().__init__(unique_id, model)
        self.hp = 5
        self.type = type

    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        if self.type == "creature":
            self.move()
            self.eat()
            self.hp -= 1


    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = self.random.choice(possible_steps)
        for s in self.model.grid.get_neighbors(self.pos, moore=True, include_center=False):
            if s.type == "food":
                new_position = s.pos
                break


        self.model.grid.move_agent(self, new_position)

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for a in cellmates:
            if a.type == "food":
                self.model.grid.move_to_empty(a)
                self.hp += 5
                break


class FoodModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, nf, width, height):
        self.num_agents = N
        self.num_food = nf
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.running = True
        # Create agents
        for i in range(self.num_agents):
            a = FoodAgent(i, self, "creature")
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



    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        for a in self.schedule.agents:
            if a.hp <= 0:
                self.grid.remove_agent(a)
                self.schedule.remove(a)


