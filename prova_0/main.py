import sys
sys.path.append('prova_0')
from model import FoodModel
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



def agent_portrayal(agent):
    if agent.type == "creature":
        portrayal = {"Shape": "rect",
                     "Color": "red",
                     "Filled": "true",
                     "Layer": 0,
                     "w": 0.5,
                     "h": 0.5}
    else:
        portrayal = {"Shape": "circle",
                     "Color": "green",
                     "Filled": "true",
                     "Layer": 1,
                     "r": 0.2}

    return portrayal

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #empty_model = FoodModel(10,10,10)
    grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)
    chart = ChartModule([{"Label": "Mean food","Color": "Black"}], data_collector_name='datacollector', canvas_height=100, canvas_width=200)

    server = ModularServer(FoodModel,
                          [grid, chart],
                          "Food Model",
                          {"N": UserSettableParameter("slider", "Creature number", 5, 0, 200, 1), "nf": UserSettableParameter("slider", "Food number", 5, 0, 200, 1),
                           "sight" : UserSettableParameter("slider", "Creature sight", 5, 0, 20, 1),
                           "width": 100, "height": 100})
    server.port = 8521  # The default
    server.launch()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
