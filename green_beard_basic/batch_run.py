from model import BeardModel
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':
    params = {"N": 1000,
              "r": 0.5,
              "dr": 0.95,
              "mr": 0.001}  #[0.001 * x for x in range(1, 2)]}


    results = batch_run(
        BeardModel,
        parameters=params,
        iterations=20,
        max_steps=1000,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)


    results_df.to_csv("result.csv")
    #results_df.to_csv("multi_result.csv")
