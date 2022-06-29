from model import HerdModel
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':
    params = {"n_creatures": 300,  # range(50, 200, 10),
              "n_pred": 15,  # range(5, 10, 2),
              "sight": 9,  # range(5, 20, 4),
              "jump_range": range(2, 7, 2),
              "mr": 0,  # [0.001 * x for x in range(1, 2)],
              "width": 100, "height": 100}

    results = batch_run(
        HerdModel,
        parameters=params,
        iterations=10,
        max_steps=1000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)

    results_df.to_csv("result.csv")
    #results_df.to_csv("multi_result.csv")

    print("yeeee")
