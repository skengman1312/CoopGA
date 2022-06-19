from model import FamilyModel
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':
    params = {"N": 1000,#range(500, 1100, 100),
              "r": 0.5, #[i*0.1 for i in range(2, 7, 1)]
              "sr":  0.95,
              "mr": [0.001 * x for x in range(1,4)] #0.001




              }
    results = batch_run(
        FamilyModel,
        parameters=params,
        iterations=10,
        max_steps=500,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )
    results_df = pd.DataFrame(results)
    print(results_df)
    results_df.to_csv("multi_result.csv")


#prova
