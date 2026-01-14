from typing import Optional
import os, warnings
import numpy as np
import obspy.core
from readdat.segy.write_obspymusc_as_segymusc import write_obspymusc_as_segymusc
from readdat.su.write_obspymusc_as_sumusc import write_obspymusc_as_sumusc

# from numpy.lib.npyio import _savez  # => no longer accepted 
from numpy import savez  # => this forces us to allow pickling which can be dangerous


def write(
        stream: obspy.core.stream.Stream, filename: str,
        acquisition_system: Optional[str] = None,
        format: str="npz",
        allow_overwrite: bool=False,
        **kwargs) -> None:
    """
    :param stream: obspy.core.stream.Stream object
    :param filename: name of file to write
    :param acquisition_system: acquisition system, e.g. "MUSC"
    :param format: format of the file, e.g. "npz"
    :param allow_overwrite: whether to overwrite existing file

    """

    if os.path.isfile(filename):
        if not allow_overwrite:
            raise IOError(f'{filename} exists already, use allow_overwrite=True to overwrite')

        else:
            # remove the file to let the method write the same name without errors
            os.remove(filename)

    if format.lower() in ['seg2', 'sg2']:
        # import this dep only on demand
        from pyseg2.toobspy import write_obspy_stream_as_seg2

        ext = filename.split('.')[-1]
        assert ext.lower() in ['seg2', 'sg2'], "extension must be .sg2 or .seg2"

        if acquisition_system is None:
            try:
                stream.stats
            except AttributeError:
                stream.stats = obspy.core.AttribDict()

            try:
                stream.stats['seg2']

            except (AttributeError, KeyError):
                stream.stats['seg2'] = obspy.core.AttribDict()

            try:
                stream.stats['seg2']['NOTE']

            except (AttributeError, KeyError):
                stream.stats['seg2']['NOTE'] = []

            if "WRITTEN_BY_READDAT" not in stream.stats['seg2']['NOTE']:
                stream.stats['seg2']['NOTE'].append("WRITTEN_BY_READDAT")

            write_obspy_stream_as_seg2(
                stream=stream,
                filename=filename,
                )
        else:
            raise NotImplementedError(
                f'cannot write SEG2{acquisition_system} for now')

    elif format.lower() == 'npz':
        assert filename.lower().endswith('.npz')
        if os.path.isfile(filename):
            assert input(f'{filename} exists already, continue? y/[n]') == "y", "exit"

        output = {
            "starttimes": np.asarray([trace.stats.starttime.timestamp for trace in stream], float),
            "delta":      np.asarray([trace.stats.delta      for trace in stream], float),
            "receiver_x": np.asarray([trace.stats.receiver_x for trace in stream], float),
            "receiver_y": np.asarray([trace.stats.receiver_y for trace in stream], float),
            "receiver_z": np.asarray([trace.stats.receiver_z for trace in stream], float),
            "source_x":   np.asarray([trace.stats.source_x   for trace in stream], float),
            "source_y":   np.asarray([trace.stats.source_y   for trace in stream], float),
            "source_z":   np.asarray([trace.stats.source_z   for trace in stream], float),
            }

        # TODO: extract more attributes there ?
        # please contact me!

        for n, trace in enumerate(stream):
            output[f'trace_{n:03d}'] = trace.data

        #_savez(filename, args=(), compress=True, allow_pickle=False, kwds=output)
        savez(filename, args=(), compress=True, kwds=output)

    elif format.lower() == "su":
        assert filename.lower().endswith('.su')
        if os.path.isfile(filename):
            assert input(f'{filename} exists already, continue? y/[n]') == "y", "exit"

        if acquisition_system == "MUSC":
            if all([trace.stats.station == "MUSC" for trace in stream]):
                write_obspymusc_as_sumusc(stream_in=stream, filename_out=filename, **kwargs)
            else:
                raise ValueError('not a MUSC file?')

        else:
            raise NotImplementedError(
                'write to su only available for MUSC data, '
                'you may also use obspy.stream.Stream.write method'
                'but the coordinate fields will be lost')

    elif format.lower() == "segy":
        assert filename.lower().endswith('.segy')
        if os.path.isfile(filename):
            assert input(f'{filename} exists already, continue? y/[n]') == "y", "exit"

        if acquisition_system == "MUSC":
            if all([trace.stats.station == "MUSC" for trace in stream]):
                write_obspymusc_as_segymusc(stream_in=stream, filename_out=filename, **kwargs)
            else:
                raise ValueError('not a MUSC file?')

        else:
            raise NotImplementedError(
                'write to segy only available for MUSC data, '
                'you may also use obspy.stream.Stream.write method'
                'but the coordinate fields will be lost')

    else:
        raise NotImplementedError(format)

    return

