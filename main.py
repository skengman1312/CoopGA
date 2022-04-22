import sys
sys.path.append('prova_0')
from model import FoodModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
# This is a sample Python script.

# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def agent_portrayal(agent):
    portrayal = {"Shape": "rect",
                 "Color": "Color",
                 "Filled": "true",
                 "Layer": 0,
                 "w": 0.5,
                 "h": 0.5}
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
    grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    server = ModularServer(FoodModel,
                          [grid],
                          "Food Model",
                          {"N": 5, "nf": 5, "width": 10, "height": 10})
    server.port = 8521  # The default
    server.launch()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
