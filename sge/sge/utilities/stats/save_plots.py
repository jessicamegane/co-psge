from os import path, pathsep

import matplotlib
import numpy as np
import pandas as pd
from sge.utilities.stats.trackers import first_pareto_list

matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rc('font', family='Times New Roman')


def save_pareto_fitness_plot():
    """
    Saves a plot of the current fitness for a pareto front.

    :return: Nothing
    """

    from sge.parameters import params

    # Initialise up figure instance.
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    # Set up iterator for color plotting.
    color = iter(plt.cm.jet(np.linspace(0, 1, len(first_pareto_list))))

    # Get labels for individual fitnesses.
    ffs = params['FITNESS_FUNCTION'].fitness_functions

    # Find the direction for step lines to "bend"
    step_dir = 'pre' if ffs[0].maximise else 'post'

    # Plot data.
    for i, gen in enumerate(first_pareto_list):
        c = next(color)
        ax1.step(gen[0], gen[1], linestyle='--',
                 where=step_dir, color=c, lw=0.35, alpha=0.25)
        ax1.plot(gen[0], gen[1], 'o', color=c, ms=1)

    # Set labels with class names.
    ax1.set_xlabel(ffs[0].__class__.__name__, fontsize=14)
    ax1.set_ylabel(ffs[1].__class__.__name__, fontsize=14)

    # Plot title and legend.
    plt.title("First pareto fronts by generation")

    # Set up colorbar instead of legend. Normalise axis to scale of data.
    sm = plt.cm.ScalarMappable(cmap="jet",
                               norm=plt.Normalize(vmin=0, vmax=len(
                                   first_pareto_list) - 1))

    # Fake up the array of the scalar mappable.
    sm._A = []

    # Plot the colorbar.
    cbar = plt.colorbar(sm, ticks=[0, len(first_pareto_list) - 1])

    # Set label of colorbar.
    # cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel('Generation', rotation=90)

    # Save plot and close.
    plt.savefig(path.join(params['FILE_PATH'], "fitness.pdf"))
    plt.close()


def save_plot_from_data(data, name):
    """
    Saves a plot of a given set of data.

    :param data: the data to be plotted
    :param name: the name of the data to be plotted.
    :return: Nothing.
    """

    from sge.parameters import params

    # Initialise up figure instance.
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    # Plot data.
    ax1.plot(data)

    # Set labels.
    ax1.set_ylabel(name, fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)

    # Plot title.
    plt.title(name)

    # Save plot and close.
    plt.savefig(path.join(params['FILE_PATH'], (name + '.pdf')))
    plt.close()


def save_plot_from_file(filename, stat_name):
    """
    Saves a plot of a given stat from the stats file.

    :param filename: a full specified path to a .csv stats file.
    :param stat_name: the stat of interest for plotting.
    :return: Nothing.
    """

    # Read in the data
    data = pd.read_csv(filename, sep="\t")
    try:
        stat = list(data[stat_name])
    except KeyError:
        s = "utilities.stats.save_plots.save_plot_from_file\n" \
            "Error: stat %s does not exist" % stat_name
        raise Exception(s)

        # Set up the figure.
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    # Plot the data.
    ax1.plot(stat)

    # Plot title.
    plt.title(stat_name)

    # Get save path
    save_path = pathsep.join(filename.split(pathsep)[:-1])

    # Save plot and close.
    plt.savefig(path.join(save_path, (stat_name + '.pdf')))
    plt.close()


def save_box_plot(data, names, title):
    """
    Given an array of some data, and a list of names of that data, generate
    and save a box plot of that data.

    :param data: An array of some data to be plotted.
    :param names: A list of names of that data.
    :param title: The title of the plot.
    :return: Nothing
    """

    from algorithm.parameters import params

    import matplotlib.pyplot as plt
    plt.rc('font', family='Times New Roman')

    # Set up the figure.
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    # Plot tight layout.
    plt.tight_layout()

    # Plot the data.
    ax1.boxplot(np.transpose(data), 1)

    # Plot title.
    plt.title(title)

    # Generate list of numbers for plotting names.
    nums = list(range(len(data))[1:]) + [len(data)]

    # Plot names for each data point.
    plt.xticks(nums, names, rotation='vertical', fontsize=8)

    # Save plot.
    plt.savefig(path.join(params['FILE_PATH'], (title + '.pdf')))

    # Close plot.
    plt.close()
