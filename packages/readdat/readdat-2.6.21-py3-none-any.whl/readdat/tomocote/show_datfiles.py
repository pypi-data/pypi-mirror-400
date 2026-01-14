#!/usr/bin/env python

"""
Lit et represente les fichiers de temps de trajet des Tomographie de P. Cote (fichiers .dat)
M.L. 10/2022
"""

import sys
import matplotlib.pyplot as plt
from readdat.tomocote.datfiles import DatFile


if __name__ == "__main__":

    datfile = DatFile(sys.argv[1])

    plt.subplot(121)
    datfile.show(plt.gca(), which="time")

    plt.subplot(122, sharex=plt.gca(), sharey=plt.gca())
    datfile.show(plt.gca(), which="velocity")

    plt.show()


