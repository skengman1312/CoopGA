from model import BeardModelAdv
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':
    params = {"N": 1000,
              "r": 0.50,  # 0.25,
              "dr": 0.95,
              "mr": 0.001,  # [0.001 * x for x in range(1, 5)],
              "cr": 0.0002,  # [0.001 * x for x in range(1, 5)],
              "linkage_dis": True}

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

    #results_df.to_csv("result_nolinkage.csv")
    results_df.to_csv("result.csv")

    #results_df.to_csv("multi_result.csv")
    #results_df.to_csv("multi_result_nolinkage.csv")

