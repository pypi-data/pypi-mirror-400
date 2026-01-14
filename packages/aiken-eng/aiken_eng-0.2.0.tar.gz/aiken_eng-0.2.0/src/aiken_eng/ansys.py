from pathlib import Path

def read_nodes(filename: str|Path) -> dict:
    """
    Reads the NLIST file from ANSYS APDL and returns a dictionary of the nodes.  This can be useful to create a
    pandas.Dataframe.
    """
    path = Path(filename)
    nodes = {}

    with path.open(mode="r", encoding="utf-8") as f:
        content = f.readlines()

    node = []
    x = []
    y = []
    z = []

    for line in content:
        if len(line.split()) > 0:
            if (line.split()[0]).isnumeric():
                node.append(int(line.split()[0]))
                x.append(float(line.split()[1]))
                y.append(float(line.split()[2]))
                z.append(float(line.split()[3]))

    nodes["NODE"] = node
    nodes["X"] = x
    nodes["Y"] = y
    nodes["Z"] = z

    return nodes

def read_prnsol(filename: str | Path) -> dict:
    """
    Reads the PRNSOL output and returns a dict {NODE, KEY} where KEY is
    the value of the output to the prnsol file.
    """
    path = Path(filename)
    nodes = {}

    with open(path) as f:
        content = f.readlines()

    node = []
    ux = []
    key = None

    for line in content:
        if len(line.split()) > 0:
            if line.split()[0] == "NODE" and key is None:
                key = line.split()[1]
            if (line.split()[0]).isnumeric():
                node.append(int(line.split()[0]))
                ux.append(float(line.split()[1]))

    nodes["NODE"] = node
    nodes[key] = ux

    return nodes

def read_pretab(filename: str | Path) -> dict:
    """
    Reads the PRETAB output and returns a dict {ELEMENT, KEY} where KEY is
    the value of the output to the PRETAB file.
    """
    path = Path(filename)
    elements = {}

    with open(path) as f:
        content = f.readlines()

    for line in content:
        if len(line.split()) > 0:
            if line.split()[0] == "ELEM" and len(elements.keys()) == 0:
                keys = line.split()
                for key in keys:
                    elements[key] = []
            if (line.split()[0]).isnumeric():
                for i, key in enumerate(keys):
                    if key == "ELEM":
                        elements[key].append(int(line.split()[i]))
                    else:
                        elements[key].append(float(line.split()[i]))

    return elements