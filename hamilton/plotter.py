from matplotlib import projections
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import *
import numpy as np

data = pd.read_csv("result.csv", index_col=0)
multidata = pd.read_csv("multi_result.csv", index_col=0)
print(multidata)


def plot_prevalence(data, title="", params=["N", "r", "dr", "mr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation
    :param title: title of the plot
    :param params: parameters to be included in the subtitle
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
    maintitle = f"Kinship altruism {title}" if title else "Kinship altruism"
    subtitle = " ".join([f"{p}={data[p][0]}" for p in params])
    plt.title(f"{maintitle}\n{subtitle}")
    filename = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filename)
    plt.show()

def get_param_ID(data, params=["N", "r", "dr", "mr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation
    :param data: data to compute the paramID on
    :param params: parameters to nìbe used for the segmentation
    """
    data["pID"] = data[params].astype(str).sum(axis=1)
    mapdict = {data["pID"].unique()[i]: i for i in range(
        len(data["pID"].unique()))}
    data["pID"] = data["pID"].apply(lambda x: mapdict[x])
    return data

def multi_plot_prevalence(data, params=["N", "r", "dr", "mr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation and with different hyperparameters
    in multiple plots
    :param data: data for the plot
    :param params: parameters to be included in the subtitle
    """
    data = get_param_ID(data, params)
    msk = [data["pID"] == i for i in data["pID"].unique()]
    for m in msk:
        plot_prevalence(data[m].reset_index(
            drop=True), title=f"Run {data[m]['pID'].max() + 1}", params=params)

def plot_rep_fitness(data, s = 100, title = "", params=["N", "r", "dr", "mr"]):
    msk = [data["iteration"] == i for i in data["iteration"].unique()]
    ms = data["Step"].max()
    finallines = {}
    for c in ["mean rep", "min rep", "max rep", "mean rep0", "mean rep1"]:
        lines = pd.DataFrame(data={m: data[msk[m]][c].reset_index(
            drop=True) for m in range(len(msk))})
        finallines[c] = lines.mean(axis=1)
    plt.plot(finallines["mean rep"], color="black", lw=1, label = "Overall mean")
    plt.plot(finallines["min rep"], color = "red", lw = 0.5, label = "Minimum")
    plt.plot(finallines["max rep"], color = "magenta", lw = 0.5, label = "Maximum")
    plt.plot(finallines["mean rep0"], color= "#4DBD60", lw=0.5, label = "Altruistic mean")
    plt.plot(finallines["mean rep1"], color= "#595FB5", lw=0.5, label = "Egoistic mean")
    plt.legend(loc='lower center', framealpha=0.8, bbox_to_anchor=(0.5, -0.3), ncol = 3, fancybox=True, prop={'size': 8})
    plt.axis((0, ms, -0.1, 1.1))
    maintitle = f"Secondary fitness {title}" if title else "Secondary fitness"
    subtitle = " ".join([f"{p}={data[p][0]}" for p in params])
    plt.title(f"{maintitle}\n{subtitle}")
    filename = f"{title.replace(' ', '')}_fitness_results.png" if title else "fitness_results.png"
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def scatter3D(data, param1, param2, result, labels, all_params, title=""):
    """
    Function used to plot altruistic allele frequency (result) against two other parameters of user's choice.
    In the output each color will represent a different combination of parameters' values
    """

    data = get_param_ID(data, all_params)

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

    # we obtain the unique labels of the pID
    # Each label of RunId correspond to a specific combination of values for the paramters
    runs = results["pID"].unique()

    handles = []

    for run in runs:
        # for each combination of parameters we will have a different color
        run_data = results[results["pID"] == run]
        prova = ax.scatter(
            run_data[param1], run_data[param2], run_data[result])
        handles.append(prova)

    if results[result].min() > 0.5:
        ax.set_zlim(0.3, 1)

    # adjusting the axes limits
    p1_min = results[param1].min()-results[param1].min() * 20/100
    p1_max = results[param1].max()+results[param1].min() * 20/100
    p2_min = results[param2].min()-results[param2].min() * 20/100
    p2_max = results[param2].max()+results[param2].min() * 20/100

    ax.set_xlim(p1_min, p1_max)
    ax.set_ylim(p2_min, p2_max)

    # plot the surface
    xx, yy = np.meshgrid(np.arange(p1_min, p1_max, (p1_max-p1_min)/100),
                         np.arange(p2_min, p2_max, (p1_max-p1_min)/100))
    z = np.full_like(np.zeros(100), 0.5, shape=xx.shape)

    ax.plot_surface(xx, yy, z, alpha=0.2)

    ax.legend(handles, runs.data)

    maintitle = f"Kinship altruism {title}" if title else "Kinship altruism"
    plt.title(f"{maintitle}")
    filename = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filename)

    plt.show()


labels = ["mutation rate", "death rate", "ending freq altruism"]
#scatter3D(multidata, param1="mr", param2="dr", result="altruistic fraction", labels=labels,
#          all_params=["N", "r", "dr", "mr"], title="scatter")

#multi_plot_prevalence(multidata)
#plot_prevalence(multidata)
plot_rep_fitness(data)
