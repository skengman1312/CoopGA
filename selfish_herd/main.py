from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

"""
Visual simulation test on server in real time following the HerbModel described in model.py
PreyAgents are coloured according to the genotype (blu if >= 0, green otherwise)
PredatorAgents are coloured in red
"""

# TODO plots in interface starts from zero, resolve this problem


def agent_portrayal(agent):
    if agent.type == "creature":
        if agent.genotype[0] >= 0:
            portrayal = {"Shape": "circle",
                         "Color": "blue",
                         "Filled": "true",
                         "Layer": 0,
                         "r": 1}
        else:
            portrayal = {"Shape": "circle",
                         "Color": "green",
                         "Filled": "true",
                         "Layer": 0,
                         "r": 1}

    else:
        # agent.type == "predator"
        portrayal = {"Shape": "rect",
                     "Color": "red",
                     "Filled": "true",
                     "Layer": 0,
                     "w": 0.9,
                     "h": 0.9}

    return portrayal


if __name__ == '__main__':
    grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)
    chart_0 = ChartModule([{"Label": "Selfish gene frequency", "Color": "Blue"},
                           {"Label": "Fear frequency", "Color": "Green"}],
                          data_collector_name='datacollector', canvas_height=100, canvas_width=200)

    chart_1 = ChartModule([{"Label": "Number of creatures", "Color": "Blue"},
                           {"Label": "Number of predators", "Color": "Red"}],
                          data_collector_name='datacollector', canvas_height=100, canvas_width=200)

    server = ModularServer(HerdModel,
                           [grid, chart_0, chart_1],
                           "HerdModel",
                           {"n_creatures": UserSettableParameter("slider", "Creature number", 100, 0, 200, 1),
                            "n_pred": UserSettableParameter("slider", "Predator number", 10, 0, 20, 1),
                            "prey_sight": UserSettableParameter("slider", "Prey sight", 9, 0, 20, 1),
                            "jump_range": UserSettableParameter("slider", "Jump_range", 3, 0, 10, 1),
                            "mr": UserSettableParameter("slider", "Mutation rate", 0.01, 0, 1, 0.01),
                            "width": 100, "height": 100})

    server.port = 8521  # The default
    server.launch()
