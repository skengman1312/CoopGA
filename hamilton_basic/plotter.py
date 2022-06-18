import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import axes3d
import numpy as np

data = pd.read_csv("result.csv", index_col = 0)
print(data)

def plot_prevalence(data):
    """
    function used to plot the mean of the allele prevalence across several simulation
    """
    data = data.drop(columns = ["N", "r", "RunId"])
    #masking the values of each iteration
    msk = [data["iteration"] == i for i in data["iteration"].unique()] #creating a boolean mask for each iteration to be plotted
    ms = data["Step"].max() #max step
    #groupling all the lines in a single df without other data
    lines = pd.DataFrame(data = { m: data[msk[m]]["altruistic fraction"].reset_index(drop=True) for m in range(len(msk))})
    #computing the mean
    lines['mean'] = lines.mean(axis=1)
    #print(lines)
    #plotting each run in thin black
    plt.plot(lines, color = "black", lw = 0.2)
    # plotting mean in red
    plt.plot(lines["mean"], color = "red", lw = 0.5, label = "mean")
    #setting plot limits
    plt.axis((0,ms,0,1))
    #filling the background wrt mean line
    plt.legend(loc='best', framealpha = 0.2)
    plt.fill_between(list(range(-1,ms)), lines["mean"], y2=1, color ="#595FB5", alpha = 0.9 )
    plt.fill_between(list(range(-1,ms)), lines["mean"], color="#4DBD60", alpha=0.9)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.xlabel("Steps")
    plt.ylabel("Population fraction")


    plt.show()
    pass


def scatter3D(data, param1, param2, result, labels):

    # we want to plot just the value of the parameters in the last step of each iteration
    max_step = data["Step"].max()
    # results stores now just the lines of the df where we had the last step of each iteration
    results = data[data["Step"] == max_step]

    # initializing the plot
    fig = plt.figure()
    #ax = plt.axes(projection='3d')
    ax = fig.add_subplot(111, projection='3d')

    # setting the labels
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])

    '''
    FOR THE FUCKING PLANE, TO BE DONE
    # a plane is a*x+b*y+c*z+d=0
    #
    # [a,b,c] is the normal
    normal = np.array([0, 0, 0.5])
    #point = np.array([1, 2, 3])
    #d = -point*normal
    # create x,y
    xx, yy = np.meshgrid(range(10), range(10))
    # calculate corresponding z
    z = np.full_like(np.zeros(100), 0.5, shape=(10, 10))
    # z.fill(0.5)
    print(type(z), z)
    # plot the surface
    ax.plot_surface(xx, yy, z, alpha=0.2)
    '''

    # we obtain the unique labels of the RunId
    # In this case I'm considering each label of RunId correspond to a specific
    # combination of value for the two paramters
    # N.B. adesso RunId value non corrisponde a una combinazione di parametri
    runs = results["RunId"].unique()

    for run in runs:
        # for each combination of parameters we will have a different color
        run_data = results[results["RunId"] == run]
        ax.scatter3D(run_data[param1], run_data[param2],
                     run_data[result])

    plt.show()


labels = ["population size",
          "initial freq altruism", "ending freq altruism"]
#scatter3D(data, "N", "r", "altruistic fraction", labels)

plot_prevalence(data)
