from model import HerdModel
from mesa.batchrunner import batch_run
import pandas as pd
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule


if __name__ == '__main__':
    params = {"n_creatures": 150, #range(50, 200, 10),
              "n_pred": 70, #range(50, 100, 10),
              "sight": 15, #range(15, 20, 2),
              "mr": 0.001, #[0.001 * x for x in range(1, 2)],
              "width": 100, "height": 100}

    results = batch_run(
        HerdModel,
        parameters=params,
        iterations=10,
        max_steps=100,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)

    results_df.to_csv("result.csv")
    #results_df.to_csv("multi_result.csv")

