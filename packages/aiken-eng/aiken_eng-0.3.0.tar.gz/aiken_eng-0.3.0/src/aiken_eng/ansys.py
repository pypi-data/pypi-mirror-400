from pathlib import Path


def read_nodes(filename: str | Path) -> dict:
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

    with path.open(mode="r", encoding="utf-8") as f:
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

    with path.open(mode="r", encoding="utf-8") as f:
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


def read_elements(filename: str | Path) -> dict:
    """Returns a dict {ELEM, NODE1, NODE2} for beam elements."""
    path = Path(filename)
    elements = {}

    with path.open(mode="r", encoding="utf-8") as f:
        content = f.readlines()

    elem = []
    node_1 = []
    node_2 = []

    for line in content:
        if len(line.split()) > 0:
            if (line.split()[0]).isnumeric():
                elem.append(int(line.split()[0]))
                node_1.append(int(line.split()[6]))
                node_2.append(int(line.split()[7]))

    elements["ELEM"] = elem
    elements["NODE1"] = node_1
    elements["NODE2"] = node_2

    return elements

def read_linearized_stress(filename: str) -> dict:
    """This file reads the linearized stress output from ANSYS and returns a dict."""
    path = Path(filename)
    results = {}
    with path.open(mode="r", encoding="utf-8") as f:
        content = f.readlines()

    results["path"] = content[1].split()[9]

    if content[3].split()[0] == "RADIUS":
        addlines = 0
        results["radius"] = float(content[3].split()[4])
        results["inside node"] = int(content[6].split()[3])
        results["outside node"] = int(content[6].split()[7])

    else:
        addlines = -3
        results["inside node"] = int(content[4].split()[3])
        results["outside node"] = int(content[4].split()[7])

    results["SXm"] = float(content[16 + addlines].split()[0])
    results["SYm"] = float(content[16 + addlines].split()[1])
    results["SZm"] = float(content[16 + addlines].split()[2])
    results["SXYm"] = float(content[16 + addlines].split()[3])
    results["SYZm"] = float(content[16 + addlines].split()[4])
    results["SXZm"] = float(content[16 + addlines].split()[5])
    results["S1m"] = float(content[18 + addlines].split()[0])
    results["S2m"] = float(content[18 + addlines].split()[1])
    results["S3m"] = float(content[18 + addlines].split()[2])
    results["SINTm"] = float(content[18 + addlines].split()[3])
    results["SEQVm"] = float(content[18 + addlines].split()[4])
    results["SXb inside"] = float(content[22 + addlines].split()[1])
    results["SXb outside"] = float(content[24 + addlines].split()[1])
    results["SYb inside"] = float(content[22 + addlines].split()[2])
    results["SYb outside"] = float(content[24 + addlines].split()[2])
    results["SZb inside"] = float(content[22 + addlines].split()[3])
    results["SZb outside"] = float(content[24 + addlines].split()[3])
    results["SXYb inside"] = float(content[22 + addlines].split()[4])
    results["SXYb outside"] = float(content[24 + addlines].split()[4])
    results["SYZb inside"] = float(content[22 + addlines].split()[5])
    results["SYZb outside"] = float(content[24 + addlines].split()[5])
    results["S1b inside"] = float(content[26 + addlines].split()[1])
    results["S1b outside"] = float(content[28 + addlines].split()[1])
    results["S2b inside"] = float(content[26 + addlines].split()[2])
    results["S2b outside"] = float(content[28 + addlines].split()[2])
    results["S3b inside"] = float(content[26 + addlines].split()[3])
    results["S3b outside"] = float(content[28 + addlines].split()[3])
    results["SINTb inside"] = float(content[26 + addlines].split()[4])
    results["SINTb outside"] = float(content[28 + addlines].split()[4])
    results["SEQVb inside"] = float(content[26 + addlines].split()[5])
    results["SEQVb outside"] = float(content[28 + addlines].split()[5])
    results["SXp inside"] = float(content[42 + addlines].split()[1])
    results["SXp outside"] = float(content[44 + addlines].split()[1])
    results["SYp inside"] = float(content[42 + addlines].split()[2])
    results["SYp outside"] = float(content[44 + addlines].split()[2])
    results["SZp inside"] = float(content[42 + addlines].split()[3])
    results["SZp outside"] = float(content[44 + addlines].split()[3])
    results["SXYp inside"] = float(content[42 + addlines].split()[4])
    results["SXYp outside"] = float(content[44 + addlines].split()[4])
    results["SYZp inside"] = float(content[42 + addlines].split()[5])
    results["SYZp outside"] = float(content[44 + addlines].split()[5])
    results["S1p inside"] = float(content[46 + addlines].split()[1])
    results["S1p outside"] = float(content[48 + addlines].split()[1])
    results["S2p inside"] = float(content[46 + addlines].split()[2])
    results["S2p outside"] = float(content[48 + addlines].split()[2])
    results["S3p inside"] = float(content[46 + addlines].split()[3])
    results["S3p outside"] = float(content[48 + addlines].split()[3])
    results["SINTp inside"] = float(content[46 + addlines].split()[4])
    results["SINTp outside"] = float(content[48 + addlines].split()[4])
    results["SEQVp inside"] = float(content[46 + addlines].split()[5])
    results["SEQVp outside"] = float(content[48 + addlines].split()[5])
    return results