# Evolution of Cooperative Behaviour, a Computational Perspective
Bio Inspired project for the simulation of evolutionary theories on cooperative and altruistic behaviour.
Work submitted as final project for Bio-Inspired Artificial Intelligence course of Artificial Intelligents Systems held at University of Trento

Each folder contains different models, to get further theoretical background please read the associated report.

## Kinship domain
In the `kinship` folder there are all the files concerning the kinship domain.
`model.py` contains the class of the basic model, `multigene_model.py` the class of the model considering the additional 
fitness and `ibd_model.py` the class of the model based on common ancestry. \
`batch_run.py` is the script which is used to run multiple iteration of a specified model, the results are saved as a 
`.csv` file. `plotter.py` and `utils.py` code respectively for the plotting function and for utility classes used inside
the model files. \
Please note that this scenario has no interactive simulation.
## Green Beard
`green_beard_basic` and `green_beard_advance` directories contain respectiovely the single and multitrait Green Beard simulations. \
In each folder thee is a `model.py` script coding for the model class a dedicated `plotter.py` and `batch_run.py`. \
Please note that this scenario has no interactive simulation.

## Selfish herb
The selfish_herb directory has a similar structure as the already described folder; the model class is defined in `model.py`
and there are dedicated `plotter.py` and `batch_run.py`. \
In addition, this scenario supports also an interactive web based simulation, to access it run `main.py` and open your 
web browser at local host.