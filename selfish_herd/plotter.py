import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_prevalence(data, title="", params=["n_creatures", "n_pred", "sight", "jump_range", "mr"]):
    """
    Function used to plot the mean of the allele prevalence across several simulation
    
    :param data: all data obtained through the batch run
    :type data: dataframe
    :param title: title of the plot
    :type title: str, optional
    :param params: parameters to be included in the subtitle
    :type params: list
    """

    # creating a boolean mask for each iteration to be plotted
    msk = [data["iteration"] == i for i in data["iteration"].unique()]
    ms = data["Step"].max()
    # grouping all the lines in a single df without other data
    lines = pd.DataFrame(data={m: data[msk[m]]["Selfish gene frequency"].reset_index(
        drop=True) for m in range(len(msk))})
    # computing the mean
    lines['mean'] = lines.mean(axis=1)

    # plotting each run in thin black
    plt.plot(lines, color="black", lw=0.2)
    # plotting mean in red
    plt.plot(lines["mean"], color="red", lw=0.5, label="mean")
    # setting plot limits
    plt.axis((0, ms, 0, 1))
    # filling the background wrt mean line
    plt.legend(loc='best', framealpha=0.2)
    plt.fill_between(list(range(0, ms + 1)), lines["mean"], y2=1, color="#595FB5", alpha=0.9)
    plt.fill_between(list(range(0, ms + 1)), lines["mean"], color="#4DBD60", alpha=0.9)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.xlabel("Steps")
    plt.ylabel("Allele frequency")
    maintitle = f"Selfish herd {title}" if title else "Selfish herd"
    subtitle = " ".join([f"{p}={data[p][0]}" for p in params])
    plt.title(f"{maintitle}\n{subtitle}")
    filename = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filename)
    plt.show()
    pass


def get_param_ID(data, params=["n_creatures", "n_pred", "sight", "jump_range", "mr"]):
    """
    Function used to retrieve data according to their IDs

    :param data: data to compute the paramID on
    :type data: dataframe
    :param params: parameters' name used for the segmentation
    :type params: list
    """

    data["pID"] = data[params].astype(str).sum(axis=1)
    mapdict = {data["pID"].unique()[i]: i for i in range(
        len(data["pID"].unique()))}
    data["pID"] = data["pID"].apply(lambda x: mapdict[x])
    return data


def multi_plot_prevalence(data, params=["n_creatures", "n_pred", "prey_sight", "jump_range", "mr"]):
    """
    function used to plot the mean of the allele prevalence across several simulation and with different hyperparameters
    in multiple plots

    :param data: data to compute the paramID on
    :type data: dataframe
    :param params: parameters' name used for the segmentation and to be included in the subtitle
    :type params: list
    """

    data = get_param_ID(data, params)
    msk = [data["pID"] == i for i in data["pID"].unique()]
    for m in msk:
        plot_prevalence(data[m].reset_index(
            drop=True), title=f"Run {data[m]['pID'].max() + 1}", params=params)


def scatter3D(data, param1, param2, result, labels, all_params, title=""):
    """
    Function used to plot selfish allele frequency (result) against two other parameters of user's choice.
    In the output each color will represent a different combination of parameters' values

    :param data: whole data
    :type data: DataFrame
    :param param1: parameter name of the x axis
    :type param1: str
    :param param2: parameter name of the y axis
    :type param2: str
    :param result: parameter name of the z axis
    :type result: str
    :param labels: labels of the axis in order: x, y, z
    :type labels: list of str
    :param all_params: set of all possible parameters in the DataFrame (exclude non-parameters columns)
    :type all_params: list of str
    :param title: title of the plot, defaults to ""
    :type title: str, optional
    """

    data = get_param_ID(data, all_params)

    # Plot the value of the parameters in the last step of each iteration
    max_step = data["Step"].max()
    results = data[data["Step"] == max_step]

    # initializing the plot
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

    maintitle = f"Selfish Herd {title}" if title else "Selfish Herd"
    plt.title(f"{maintitle}")
    filename = f"{title.replace(' ', '')}_results.png" if title else "results.png"
    plt.savefig(filename)

    plt.show()


if __name__ == '__main__':

    data = pd.read_csv("result.csv", index_col=0)
    multidata = pd.read_csv("multi_result.csv", index_col=0)

    scatter3D(multidata, param1="jump_range", param2="prey_sight", result="Selfish gene frequency",
              labels=["jump_range", "prey_sight", "ending selfish freq "],
              all_params=["n_creatures", "n_pred", "prey_sight", "jump_range", "mr"], title="scatter")

    #scatter3D(data, param1="jump_range", param2="sight", result="Selfish gene frequency",
              #labels=["jump_range", "sight", "ending selfish freq "],
              #all_params=["n_creatures", "n_pred", "sight", "jump_range", "mr"], title="scatter 1")
    #plot_prevalence(data)
    multi_plot_prevalence(multidata)