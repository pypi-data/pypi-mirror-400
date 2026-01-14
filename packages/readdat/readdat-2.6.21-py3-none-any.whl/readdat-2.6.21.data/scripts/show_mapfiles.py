#!python

"""
Lit et represente les fichiers de Tomographie de P. Cote (fichiers .map)
avec la meme color bar que celle utiliser par Philippe.
M.L. 10/2022
"""


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import sys


def show_map_file(map_file, ax):
    A = np.genfromtxt(map_file)
    x, y, z = [A[:, i].reshape((199, A.shape[0] // 199)) for i in range(3)]

    z.flat[z.flat[:].argmin()] = 0
    z.flat[z.flat[:].argmax()] = 10000

    cmap = colors.ListedColormap([
        # (254/255.,255/255.,151/255.),
        (255 / 255., 255 / 255., 1 / 255.),
        (240 / 255., 201 / 255., 2 / 255.),
        (238 / 255., 143 / 255., 17 / 255.),
        (255 / 255., 1 / 255., 1 / 255.),
        (255 / 255., 1 / 255., 151 / 255.),
        (31 / 255., 150 / 255., 20 / 255.),
        (1 / 255., 255 / 255., 1 / 255.),
        (1 / 255., 255 / 255., 201 / 255.),
        (0 / 255., 223 / 255., 241 / 255.),
        (2 / 255., 151 / 255., 254 / 255.),
        # (1/255.,1/255.,255/255.),
    ])
    cmap.set_under((254 / 255., 255 / 255., 151 / 255.))
    cmap.set_over((1 / 255., 1 / 255., 255 / 255.))

    plt.colorbar(
        ax.contourf(x, y, z,
            cmap=cmap,
            levels=[2200, 2290, 2380, 2470, 2560, 2650, 2740, 2830, 2920, 3010, 3100],
            extend="both"))


if __name__ == "__main__":

    mapfile = sys.argv[1]

    show_map_file(mapfile, plt.gca())
    plt.show()


