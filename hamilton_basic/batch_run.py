from model import FamilyModel
from mesa.batchrunner import batch_run
import pandas as pd
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule


if __name__ == '__main__':
    params = {"N": 1000,#range(500, 1100, 100),
              "r": 0.5#[i*0.1 for i in range(2, 7, 1)]

              }
    results = batch_run(
        FamilyModel,
        parameters=params,
        iterations=5,
        max_steps=1000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )
    results_df = pd.DataFrame(results)
    print(results_df)
    results_df.to_csv("result.csv")


#prova
