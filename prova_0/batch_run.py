from model import FoodModel
from mesa.batchrunner import batch_run
import pandas as pd
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule


if __name__ == '__main__':
    params = {"N": range(150, 200, 10),
              "nf": range(150, 200, 10),
              "sight" : range(15,20,2),
              "width": 100, "height": 100}
    results = batch_run(
        FoodModel,
        parameters=params,
        iterations=5,
        max_steps=100,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

#prova
