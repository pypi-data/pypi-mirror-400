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


def plot(x, y, x_label=None, y_label=None, title=None, c="black", hline=None):
    plt.plot(x, y, c=c)
    _plot_options(x=x, x_label=x_label, y_label=y_label, title=title, hline=hline)
    plt.show()


def scatter(x, y, x_label=None, y_label=None, title=None, s=1, c="black", hline=None):
    plt.scatter(x, y, s=s, c=c)
    _plot_options(x=x, x_label=x_label, y_label=y_label, title=title, hline=hline)
    plt.show()


def plot_series(x, y: dict, x_label=None, y_label=None, title=None, hline=None):
    for k in y:
        plt.plot(x, y[k], label=k)
    _plot_options(x=x, x_label=x_label, y_label=y_label, title=title, hline=hline)
    plt.legend()
    plt.show()


def _plot_options(x, x_label=None, y_label=None, title=None, hline=None):
    if hline:
        plt.hlines(hline, x.min(), x.max(), linestyles="dashed")
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if title:
        plt.title(title)


def plot_2d_scatter_colorbar(data, title=None, figure_size=(20, 5), color_map="hsv"):
    """
    Plot a 2d scatter plot with colorbar.
    data is a dictionary with keys 'x', 'y' and 'z'
    """
    x, y, z = data.keys()
    fig = plt.figure(figsize=figure_size)
    ax = fig.add_subplot(111)
    p = ax.scatter(data[x], data[y], s=2, c=data[z], cmap=color_map)
    _plot_options(x=None, x_label=x, y_label=y, title=title, hline=None)
    fig.colorbar(p, ax=ax, shrink=0.75, label=z)
    plt.show()
