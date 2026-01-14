# aiken_eng
This is a collection of tools used by Aiken Engineering Company.
## plotting
Sets the plot defaults for border, gridlines, tick marks, etc. to use with matplotlib.<br>
`plot(x, y, x_label, y_label, title, c, hline)` - a simple one-line plot interface<br>
`scatter(x, y, x_label, y_label, title, c, hline)` - a simple scatter plot interface<br>
`plot_series(x, y, x_label, y_label, title, c, hline)` - plot multiple lines, y is a dict<br>
`plot_2d_scatter_colorbar(data, title, figure_size, color_map)` - plot a 2D scatter plot with a colorbar<br>
## ansys
Provides some tools for handling common outputs from ANSYS APDL.<br>
`read_nodes(filename)` - reads the NLIST file and returns a dict.<br>
`read_prnsol(filename)` - reads the output of a PRNSOL file and retuns a dict.<br>
`read_pretab(filename)` - reads the output of a PRETAB file and returns a dict.<br>
`read_elements(filename)` - returns a dict {ELEM, NODE1, NODE2} for beam elements.<br>
`read_linearized_stress(filename)` - reads the linearized stress output from ANSYS and returns a dict.<br>
## units
This file uses all the scipy.constants units and defines some additional units
that make documentation / implementation easier to follow.<br>
For example, m=1.<br>

Trigger Warning! - This file uses from `scipy.constants import *`