from matplotlib import projections
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import *
import numpy as np

data = pd.read_csv("result.csv", index_col=0)
multidata = pd.read_csv("multi_result.csv", index_col=0)
print(data)


def plot_prevalence(data, title=""):
    """
    function used to plot the mean of the allele prevalence across several simulation
    """
    # data = data.drop(columns=["N", "r", "RunId"])
    # masking the values of each iteration
    # creating a boolean mask for each iteration to be plotted
    msk = [data["iteration"] == i for i in data["iteration"].unique()]
    ms = data["Step"].max()  # max step
    # grouping all the lines in a single df without other data
    lines = pd.DataFrame(data={m: data[msk[m]]["altruistic fraction"].reset_index(
        drop=True) for m in range(len(msk))})
    # computing the mean
    lines['mean'] = lines.mean(axis=1)
    print(lines)
    # print(lines)
    # plotting each run in thin black
    plt.plot(lines, color="black", lw=0.2)
    # plotting mean in red
    plt.plot(lines["mean"], color="red", lw=0.5, label="mean")
    # setting plot limits
    plt.axis((0, ms, 0, 1))
    # filling the background wrt mean line
    plt.legend(loc='best', framealpha=0.2)
    plt.fill_between(list(range(0, ms + 1)),
                     lines["mean"], y2=1, color="#595FB5", alpha=0.9)
    plt.fill_between(list(range(0, ms + 1)),
                     lines["mean"], color="#4DBD60", alpha=0.9)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.xlabel("Steps")
    plt.ylabel("Allele frequency")
    print(data)
    maintitle = f"Kinship altruism {title}" if title else "Kinship altruism"
    plt.title(f"{maintitle}\nN={data['N'][0]} r={data['r'][0]} dr={data['sr'][0]} mr={data['mr'][0]} ")
    filname = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filname)
    plt.show()
    pass


def get_param_ID(data, params=["N", "r", "sr", "mr"]):
    data["pID"] = data[params].astype(str).sum(axis=1)
    mapdict = {data["pID"].unique()[i]: i for i in range(len(data["pID"].unique()))}
    data["pID"] = data["pID"].apply(lambda x: mapdict[x])
    return data


def multi_plot_prevalence(data, params=["N", "r", "sr", "mr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation and with different hyperparameters
    in multiple plots
    """
    data = get_param_ID(data, params)
    # print(mapdict)
    print(data["pID"])
    msk = [data[["N", "r", "sr", "mr"]] == i for i in params]

    # print(msk)
    for m in msk:
        # print(data[m]["iteration"].unique())
        plot_prevalence(data[m].reset_index(drop=True), title=f"Run {data[m]['pID'].max() + 1}")
    # print(data)
    # msk = [data["iteration"] == i for i in data["iteration"].unique()]


def f(x, y, n):
    return np.full_like(np.zeros(100), 0.5, shape=n)


def scatter3D(data, param1, param2, result, labels):
    # we want to plot just the value of the parameters in the last step of each iteration
    max_step = data["Step"].max()
    # results stores now just the lines of the df where we had the last step of each iteration
    results = data[data["Step"] == max_step]

    # initializing the plot
    fig = plt.figure()
    ax = plt.axes(projection='3d')

    # setting the labels
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])

    # we obtain the unique labels of the RunId
    # In this case I'm considering each label of RunId correspond to a specific
    # combination of value for the two paramters
    # N.B. adesso RunId value non corrisponde a una combinazione di parametri
    runs = results["RunId"].unique()

    for run in runs:
        # for each combination of parameters we will have a different color
        run_data = results[results["RunId"] == run]
        ax.scatter(run_data[param1], run_data[param2], run_data[result])

    if results[result].min() > 0.5:
        ax.set_zlim(0.3, 1)

    # plot the surface
    m = results[param1].min()
    n = results[param2].min()
    xx, yy = np.meshgrid(np.arange((m - 0.5), (m + 0.5), 0.1),
                         np.arange((n - 0.5), (n + 0.5), 0.1))

    z = f(xx, yy, xx.shape)

    ax.plot_surface(xx, yy, z, alpha=0.2)

    plt.show()


labels = ["population size",
          "initial freq altruism", "ending freq altruism"]
# scatter3D(data, "N", "r", "altruistic fraction", labels)

multi_plot_prevalence(multidata)
# plot_prevalence(data)
