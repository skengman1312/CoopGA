from green_beard_basic import model
#from model import BeardModel
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':

    params = {"N": 500,
              }
    print("ciao")
    results = batch_run(
        model.BeardModel,
        parameters=params,
        iterations=20,
        max_steps=5,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    print("ciao1")
    results_df = pd.DataFrame(results)

    print(results_df)
    results_df.to_csv("result.csv")

# prova
