"""
This file uses all the scipy.constants units and defines some additional units
that make documentation / implementation easier to follow.  For example, m=1.
Trigger Warning! - This file uses from `scipy.constants import *`
"""

from scipy.constants import *

# define some additional common units
m = 1.0
N = 1.0
s = 1.0
kg = 1.0
J = 1.0
kJ = 1000
mm = 1 / 1000 * m
cm = 1/ 100 * m
ksi = 1000 * psi
MPa = N / mm ** 2
kPa = 1000 * N / m ** 2
kN = 1000 * N
ft = 12 * inch
psf = 144 * psi
kip = 1000 * pound_force
L = .001 * m ** 3
