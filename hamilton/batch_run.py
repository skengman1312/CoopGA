from multigene_model import MultigeneFamilyModel
from ibd_model import IBDFamilyModel
from mesa.batchrunner import batch_run
import pandas as pd

if __name__ == '__main__':
    params = {"N": 140, #range(140, 220, 20),
              "r": 0.5, #[i*1200.1 for i in range(2, 7, 1)]
              "dr":  0.9,
              "mr": 0.001 #[0.001 * x for x in range(1,4)] #0.001
              }

    results = batch_run(
        IBDFamilyModel,
        parameters=params,
        iterations=15,
        max_steps=200,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )
    
    results_df = pd.DataFrame(results)
    print(results_df)
    results_df.to_csv("./data/idb_result.csv")

