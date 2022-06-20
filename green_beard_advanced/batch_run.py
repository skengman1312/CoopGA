from model import BeardModelAdv
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':

    params = {"N": 1000,
              "r": 0.5, #[i*0.1 for i in range(2, 7, 1)], #0.5,
              "dr": 0.95,
              "mr": 0.001,#[0.001 * x for x in range(1, 4)]} #0.001
              "cr": 0.02}

    results = batch_run(
        BeardModelAdv,
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