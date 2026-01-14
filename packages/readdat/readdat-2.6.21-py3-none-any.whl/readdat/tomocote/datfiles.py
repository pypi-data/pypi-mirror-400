from typing import Union
import os
import numpy as np
from matplotlib import colors, pyplot as plt


class Values2Colors(object):
    """
    an object to convert values to colors
    """
    def __init__(self,
                 vmin: float, vmax: float,
                 cmap: Union[str, colors.Colormap] = 'jet'):

        self.cb = plt.cm.ScalarMappable(norm=None, cmap=cmap)
        self.cb.set_array(np.array([vmin, vmax]))
        self.cb.autoscale()

    def rgba(self, values: Union[float, list, np.ndarray]) \
            -> Union[tuple, np.ndarray]:
        return self.cb.to_rgba(values)

    def rgb(self, values: Union[float, list, np.ndarray]) \
            -> Union[tuple, np.ndarray]:
        rgba = self.rgba(values)

        if isinstance(rgba, tuple):
            return rgba[0], rgba[1], rgba[2]
        else:
            return rgba[:, :-1]

    def __call__(self, values: Union[float, list, np.ndarray]) \
            -> Union[tuple, np.ndarray]:
        return self.rgb(values)


def minmax(x):
    return min(x), max(x)


class DatFile:

    @staticmethod
    def read(datfile: str):
        assert os.path.isfile(datfile)

        receivers = {}
        sources = {}
        traveltimes = {}

        with open(datfile, 'r', encoding="latin-1") as fid:
            site = fid.readline().split('\n')[0]   # e.g. Bure
            obj = fid.readline().split('\n')[0]    # e.g. Pilier
            manip = fid.readline().split('\n')[0]  # e.g. Tomo1

            nsource, nrec = np.asarray(fid.readline().split('\n')[0].split(), int)

            for i in range(1, nsource+1):
                l = fid.readline()
                l = l.split('\n')[0].split()

                nsrc = int(l[0])
                x = float(l[1])
                y = float(l[3])
                sources[nsrc] = {"x": x, "y": y}

            for i in range(1, nrec+1):
                l = fid.readline()
                l = l.split('\n')[0].split()
                nrec = int(l[0])
                x = float(l[1])
                y = float(l[3])
                receivers[nrec] = {"x": x, "y": y}

            reclist = np.array(fid.readline().split('\n')[0].split(), int)
            for i in range(1, nsource+1):
                l = fid.readline().split('\n')[0].split()
                nsrc = int(l[0])
                tts = np.asarray(l[1:], float)
                assert len(reclist) == len(reclist)
                traveltimes[nsrc] = {}

                for nrec, tt in zip(reclist, tts):
                    if tt != 0.:
                        traveltimes[nsrc][nrec] = tt

        return site, obj, manip, receivers, sources, traveltimes

    def __init__(self, datfile: str):
        self.site, self.obj, self.manip, self.receivers, self.sources, self.traveltimes = self.read(datfile)

    def paths(self):

        for nsrc, tts in self.traveltimes.items():
            xsrc, ysrc = self.sources[nsrc]['x'], self.sources[nsrc]['y']

            for nrec, tt in tts.items():
                xrec, yrec = self.receivers[nrec]['x'], self.receivers[nrec]['y']
                dist = np.sqrt((xrec - xsrc) ** 2. + (yrec - ysrc) ** 2.)

                yield (nsrc, nrec), (xsrc, xrec), (ysrc, yrec), tt, dist

    def show_receivers(self, ax, *args, **kwargs):
        n_rec = [n for n, recpos in self.receivers.items()]
        x_rec = [recpos['x'] for _, recpos in self.receivers.items()]
        y_rec = [recpos['y'] for _, recpos in self.receivers.items()]

        hdl, = ax.plot(x_rec, y_rec, *args, **kwargs)
        if True:
            for n, x, y in zip(n_rec, x_rec, y_rec):
                ax.text(x, y, f'{n:d}', color=hdl.get_color())

        return hdl

    def show_sources(self, ax, *args, **kwargs):
        n_src = [n for n, srcpos in self.sources.items()]
        x_src = [srcpos['x'] for _, srcpos in self.sources.items()]
        y_src = [srcpos['y'] for _, srcpos in self.sources.items()]
        hdl, = ax.plot(x_src, y_src, *args, **kwargs)
        if True:
            for n, x, y in zip(n_src, x_src, y_src):
                ax.text(x, y, f'{n:d}', color=hdl.get_color(), va="top", ha="right")

        return hdl

    def show(self, ax, which="time"):

        if which == "time":
            vmin, vmax = minmax([tt for _, _, _, tt, _ in self.paths()])
            cmap = "jet"
        elif which == "velocity":
            vmin, vmax = minmax([dd / tt for _, _, _, tt, dd in self.paths()])
            cmap = "jet_r"
        else:
            raise NotImplementedError(which)

        v2c = Values2Colors(
            vmin=vmin, vmax=vmax,
            cmap=plt.get_cmap(cmap))

        for (nsrc, nrec), (xsrc, xrec), (ysrc, yrec), tt, dist in self.paths():
            value = {"time": tt, "velocity": dist / tt}[which]
            ax.plot([xsrc, xrec], [ysrc, yrec], '-',
                color=v2c(value),
                alpha=0.4)

        self.show_receivers(ax, 'kv')
        self.show_sources(ax, 'r*')

        ax.figure.colorbar(v2c.cb, label={"time": "t", "velocity": "v"}[which])
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_aspect(1.0)
        ax.grid(True, linestyle=":", color="k")
        ax.set_title(which)

