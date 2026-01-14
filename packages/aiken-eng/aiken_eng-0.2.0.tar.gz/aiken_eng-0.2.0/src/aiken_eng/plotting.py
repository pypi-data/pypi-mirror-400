import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["axes.titlesize"] = "medium"
mpl.rcParams["axes.grid"] = True
mpl.rcParams["axes.formatter.use_mathtext"] = True
mpl.rcParams["xtick.top"] = True
mpl.rcParams["xtick.labelsize"] = "small"
mpl.rcParams["xtick.direction"] = "in"
mpl.rcParams["xtick.minor.visible"] = True
mpl.rcParams["ytick.right"] = True
mpl.rcParams["ytick.labelsize"] = "small"
mpl.rcParams["ytick.direction"] = "in"
mpl.rcParams["ytick.minor.visible"] = True
mpl.rcParams["grid.linewidth"] = 0.5
mpl.rcParams["legend.fontsize"] = "small"
mpl.rcParams["legend.framealpha"] = 1.0

print("aiken_plot_defaults.py imported.")


def plot(x, y, x_label=None, y_label=None, title=None):
    plt.plot(x, y)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.show()

def scatter(x, y, x_label=None, y_label=None, title=None):
    plt.scatter(x, y)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.show()
