from matplotlib import projections
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import *
import numpy as np

data = pd.read_csv("result.csv", index_col=0)
data1 = pd.read_csv("result_nolinkage.csv", index_col=0)
multidata = pd.read_csv("multi_result.csv", index_col=0)
multidata1 = pd.read_csv("multi_result_nolinkage.csv", index_col=0)

# ----- FOR ALTRUISTIC FRACTION ------


def plot_prevalence(data, title="", params=["N", "r", "dr", "mr"]):
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
    pass


def get_param_ID(data, params=["N", "r", "dr", "mr", "cr"]):
    """

    """
    data["pID"] = data[params].astype(str).sum(axis=1)
    mapdict = {data["pID"].unique()[i]: i for i in range(
        len(data["pID"].unique()))}
    data["pID"] = data["pID"].apply(lambda x: mapdict[x])
    return data


def multi_plot_prevalence(data, params=["N", "r", "dr", "mr", "cr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation and with different hyperparameters
    in multiple plots
    """
    data = get_param_ID(data, params)
    msk = [data["pID"] == i for i in data["pID"].unique()]
    for m in msk:
        plot_prevalence(data[m].reset_index(
            drop=True), title=f"Run {data[m]['pID'].max() + 1}", params=params)


def scatter3D(data, param1, param2, result, labels, all_params, title=""):
    """
    Function used to plot altruistic allele frequency (result) against two other parameters of user's choice.
    In the output each color will represent a different combination of parameters' values
    """

    data = get_all_param_ID(data, all_params)

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


# ----- FOR 4 ALLELES ------

def plot_all_prevalence(data, title="", params=["N", "r", "dr", "mr", "cr"], frequency= True, fill= True):
    """
    function used to plot the mean of the allele prevalence across several simulation
    """
    # data = data.drop(columns=["N", "r", "RunId"])
    # masking the values of each iteration
    # creating a boolean mask for each iteration to be plotted

    msk = [data["iteration"] == i for i in data["iteration"].unique()]
    ms = data["Step"].max()  # max step  printa step r

    # grouping all the lines in a single df without other data
    if frequency:
        lines_true = pd.DataFrame(data={m: data[msk[m]]["true beards fraction"].reset_index(
            drop=True) for m in range(len(msk))})
        lines_suckers = pd.DataFrame(data={m: data[msk[m]]["suckers fraction"].reset_index(
            drop=True) for m in range(len(msk))})
        lines_impostors = pd.DataFrame(data={m: data[msk[m]]["impostors fraction"].reset_index(
            drop=True) for m in range(len(msk))})
        lines_cowards = pd.DataFrame(data={m: data[msk[m]]["cowards fraction"].reset_index(
            drop=True) for m in range(len(msk))})

    else:
        # plot wrt number of agents
        lines_true = pd.DataFrame(
            data={m: (data[msk[m]]["true beards fraction"] * data[msk[m]]["n_agents"]).reset_index(
                drop=True) for m in range(len(msk))})
        lines_suckers = pd.DataFrame(data={m: (data[msk[m]]["suckers fraction"] * data[msk[m]]["n_agents"]).reset_index(
            drop=True) for m in range(len(msk))})
        lines_impostors = pd.DataFrame(
            data={m: (data[msk[m]]["impostors fraction"] * data[msk[m]]["n_agents"]).reset_index(
                drop=True) for m in range(len(msk))})
        lines_cowards = pd.DataFrame(data={m: (data[msk[m]]["cowards fraction"] * data[msk[m]]["n_agents"]).reset_index(
            drop=True) for m in range(len(msk))})

    # computing the mean
    lines_true['mean'] = lines_true.mean(axis=1)
    lines_suckers['mean'] = lines_suckers.mean(axis=1)
    lines_impostors['mean'] = lines_impostors.mean(axis=1)
    lines_cowards['mean'] = lines_cowards.mean(axis=1)

    # setting plot limits
    if frequency:
        plt.axis((0, ms, 0, 1))
    else:
        plt.axis((0, ms, 0, max(data["n_agents"])))

    if not fill:
        # plot lines
        plt.plot(lines_true['mean'], color="#120A8F", lw=0.5)
        plt.plot(lines_suckers['mean'], color="#FF1493", lw=0.5)
        plt.plot(lines_cowards['mean'], color="#F4A460", lw=0.5)
        plt.plot(lines_impostors['mean'], color="#8FBC8F", lw=0.5)

    else:
        # filling the background wrt mean line values
        # EDO
        plt.fill_between(list(range(0, ms + 1)),
                         y1=0,
                         y2=lines_true["mean"],
                         color="#120A8F",
                         alpha=0.9)

        plt.fill_between(list(range(0, ms + 1)),
                         y1=lines_true["mean"],
                         y2=lines_true["mean"] + lines_suckers["mean"],
                         color="#FF1493", alpha=0.9)
        plt.fill_between(list(range(0, ms + 1)),
                         y1=lines_true["mean"] + lines_suckers["mean"],
                         y2=lines_cowards["mean"] + lines_true["mean"] + lines_suckers["mean"],
                         color="#F4A460",
                         alpha=0.9)

        plt.fill_between(list(range(0, ms + 1)),
                         y1=lines_cowards["mean"] + lines_true["mean"] + lines_suckers["mean"],
                         y2=lines_cowards["mean"] + lines_true["mean"] + lines_impostors["mean"] + lines_suckers["mean"],
                         color="#8FBC8F",
                         alpha=0.9)


    plt.xlabel("Steps")
    plt.ylabel("Allele frequency" if frequency else "Number of individuals")
    maintitle = f"{title}" if title else "Green Beard"
    subtitle = " ".join([f"{p}={data[p][0]}" for p in params])

    plt.title(f"{maintitle}\n{subtitle}")
    plt.legend(["true beards", "suckers", "cowards", "impostors"], loc='best', framealpha=0.2, title="Labels")
    #plt.legend(["impostors","true beards", "cowards","suckers"], loc='best', framealpha=0.2, title="Labels")

    filename = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filename)
    plt.show()

    pass


def get_all_param_ID(data, params=["N", "r", "dr", "mr", "cr"]):

    data["pID"] = data[params].astype(str).sum(axis=1)
    mapdict = {data["pID"].unique()[i]: i for i in range(
        len(data["pID"].unique()))}
    data["pID"] = data["pID"].apply(lambda x: mapdict[x])
    return data


def multi_plot_all_prevalence(data, params=["N", "r", "dr", "mr", "cr"], sub=""):
    """
    function used to plot the mean of the allele prevalence across several simulation and with different hyperparameters
    in multiple plots
    """
    data = get_all_param_ID(data, params)
    msk = [data["pID"] == i for i in data["pID"].unique()]
    for m in msk:
        plot_all_prevalence(data[m].reset_index(
            drop=True), title=f"Run {data[m]['pID'].max() + 1}: " + sub, params=params)


if __name__ == "__main__":

    #### ----- FOR ALTRUISTIC FRACTION ------

    #plot_prevalence(data, title="Green Beard linkage disequilibrium")
    #plot_prevalence(data1, title="Green Beard")

    #multi_plot_prevalence(multidata, sub="Green Beard linkage disequilibrium")
    #multi_plot_prevalence(multidata1, sub="Green Beard")

    labels = ["mutation rate", "death rate", "ending freq altruism"]
    #scatter3D(multidata, param1="mr", param2="dr", result="altruistic fraction", labels=labels,
          #all_params=["N", "r", "dr", "mr"], title="scatter")
    #scatter3D(multidata1, param1="mr", param2="dr", result="altruistic fraction", labels=labels,
          #all_params=["N", "r", "dr", "mr"], title="scatter")


    #### ----- FOR 4 ALLELES ------

    #plot_all_prevalence(data, title="Green Beard linkage disequilibrium", frequency=True)
    # frequency=false do the graph according to the agent numbers
    plot_all_prevalence(data1, title="Green Beard", frequency=True, fill=True)

    #multi_plot_all_prevalence(multidata, sub="Green Beard linkage disequilibrium", frequency=True)
    #multi_plot_all_prevalence(multidata1, sub="Green Beard", frequency=True)


