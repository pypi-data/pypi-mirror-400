# aiken_eng
This is a collection of tools used by Aiken Engineering Company.
## plotting
Sets the plot defaults for border, gridlines, tick marks, etc. to use with matplotlib.<br>
`plot(x, y, x_label, y_label, title)` - a simple one-line plot interface
## ansys
Provides some tools for handling common outputs from ANSYS APDL.<br>
`read_nodes(path)` - reads the NLIST file and returns a dict.<br>
`read_prnsol(path)` - reads the output of a PRNSOL file and retuns a dict.<br>
`read_pretab(path)` - reads the output of a PRETAB file and returns a dict.<br>