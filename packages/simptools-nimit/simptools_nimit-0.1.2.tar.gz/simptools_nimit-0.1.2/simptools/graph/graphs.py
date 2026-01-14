import matplotlib.pyplot as plt

def save_graph(fig, filename, dpi=300):
    """
    Docstring for save_graph
    
    :param fig: It is a matplotlib figure object to be saved.
    :param filename: It is the path where the graph image will be saved.
    :param dpi: It is the resolution of the saved image in dots per inch. Default is 300.

    Example:
        >>> fig = line_graph([1, 2, 3], [4, 5, 6])
        >>> save_graph(fig, "output/line_graph.png", dpi=200)
    """
    fig.savefig(filename, dpi=dpi)

def line_graph(x, y, title="Line Graph", xlabel="X-axis", ylabel="Y-axis", marker='o', line_style='-', line_color='b', show_grid=True):
    """
    Docstring for line_graph
    
    :param x: It is the coordinate of x axis. (For multiple lines, provide a list of x data)
    :param y: It is the coordinate of y axis. (For multiple lines, provide a list of y data)
    :param title: It is the title of the graph.
    :param xlabel: It is the label for x axis.
    :param ylabel: It is the label for y axis.
    :param marker: It is the marker style for the line.
    :param line_style: It is the line style.
    :param line_color: It is the color of the line.
    """
    plt.figure()
    plt.plot(x, y, marker=marker, linestyle=line_style, color=line_color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(show_grid)
    plt.show()

    return plt.gcf()  # Return the current figure object
def bar_graph(categories, values, title="Bar Graph", xlabel="Categories", ylabel="Values", bar_color='b', show_grid=True):
    """
    Docstring for bar_graph

    :param categories: It is the categories on the x-axis.
    :param values: It is the values on the y-axis.
    :param title: It is the title of the graph.
    :param xlabel: It is the label for x axis.
    :param ylabel: It is the label for y axis.
    :param bar_color: It is the color of the bars.
    :param show_grid: It is a boolean value to show or hide the grid.
    """
    plt.figure()
    plt.bar(categories, values, color=bar_color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(show_grid)
    plt.show()

    return plt.gcf()  # Return the current figure object

def scatter_plot(x, y, title="Scatter Plot", xlabel="X-axis", ylabel="Y-axis", point_color='b', point_size=20, show_grid=True):
    """
    Docstring for scatter_plot

    :param x: It is the x-coordinates of the data points.
    :param y: It is the y-coordinates of the data points.
    :param title: It is the title of the graph.
    :param xlabel: It is the label for x axis.
    :param ylabel: It is the label for y axis.
    :param point_color: It is the color of the data points.
    :param point_size: It is the size of the data points.
    :param show_grid: It is a boolean value to show or hide the grid.
    """
    plt.figure()
    plt.scatter(x, y, c=point_color, s=point_size)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(show_grid)
    plt.show()

    return plt.gcf()  # Return the current figure object

def histogram(data, bins=10, title="Histogram", xlabel="Value", ylabel="Frequency", bar_color='b', show_grid=True):
    """
    Docstring for histogram

    :param data: It is the data to be plotted in the histogram.
    :param bins: It is the number of bins for the histogram.
    :param title: It is the title of the graph.
    :param xlabel: It is the label for x axis.
    :param ylabel: It is the label for y axis.
    :param bar_color: It is the color of the bars.
    :param show_grid: It is a boolean value to show or hide the grid.
    """
    plt.figure()
    plt.hist(data, bins=bins, color=bar_color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(show_grid)
    plt.show()

    return plt.gcf()  # Return the current figure object