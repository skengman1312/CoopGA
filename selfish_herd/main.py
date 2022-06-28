import sys
sys.path.append('prova_0')
from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

#prima prova di simulazione con visualzazione su server in tempo reale

#regole molto semplici:
# 5hp di partenza; -1hp a step; +5hp per unità di cibo consumata
# movimento di una casella a step per ogni creatura;
# se c'è cibo nelle vicinanze il movimento sarà verso il cibo, altrimenti sarà randomico.
# se gli hp scendono a 0 la creatura è eliminata
# il numero di cibo è costante

# TODO plots in interface starts from zero, resolve this problem

def agent_portrayal(agent):
    if agent.type == "creature":
        if agent.genotype[0] >= 0:
            portrayal = {"Shape": "rect",
                         "Color": "blue",
                         "Filled": "true",
                         "Layer": 0,
                         "w": 0.5,
                         "h": 0.5}
        else:
            portrayal = {"Shape": "rect",
                         "Color": "green",
                         "Filled": "true",
                         "Layer": 0,
                         "w": 0.5,
                         "h": 0.5}

    elif agent.type == "predator":

        portrayal = {"Shape": "rect",
                     "Color": "red",
                     "Filled": "true",
                     "Layer": 0,
                     "w": 0.9,
                     "h": 0.9}

    else:
        portrayal = {"Shape": "circle",
                     "Color": "green",
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.5}

    return portrayal

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #empty_model = FoodModel(10,10,10)

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
                          {"n_creatures": UserSettableParameter("slider", "Creature number", 50, 0, 200, 1),
                           "n_pred": UserSettableParameter("slider", "Predator number", 50, 0, 200, 1),
                           "sight": UserSettableParameter("slider", "Creature sight", 5, 0, 20, 1),
                           "rest_time": UserSettableParameter("slider", "Rest_time", 5, 0, 20, 1),
                           "mr": UserSettableParameter("slider", "Mutation rate", 0.01, 0, 1, 0.01),
                           "width": 100, "height": 100})

    server.port = 8521  # The default
    server.launch()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
