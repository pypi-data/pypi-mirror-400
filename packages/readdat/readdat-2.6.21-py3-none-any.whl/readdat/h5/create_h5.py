from typing import List
import obspy
import os, sys, glob

from readdat import read

from HDF5DataModel.Model.h5model import H5DataModel

# from HDF5DataModel.Model import h5model
# from HDF5DataModel.Model.subclasses import Dataset, Acquisition, AcqSig, AcqTrace

def create_hdf5_model(
    filenames_in: List[str],
    acquisition_system: str,
    dataset_name: str,
    filename_out: str,
    ) -> H5DataModel:
    """
    Create an HDF5 model From a list of files that can be read with readdat
    """

    if os.path.isfile(filename_out):
        raise IOError(f'{filename_out} exists already')

    # ======================================
    datamodel = H5DataModel(file_path=filename_out)
    dataset = datamodel.add_dataset(dataset_name)
    # dataset.attrs.version # version of datamodel => private
    dataset.attrs.start_time = 0.
    dataset.attrs.experimenter = ""
    dataset.attrs.description = ""


    for filename_in in filenames_in:
        stream = read(filename_in, format="SEG2", acquisition_system=acquisition_system)
        acquisition_name = os.path.basename(filename_in)

        # ======================================
        acq = dataset.add_acquisition(name=acquisition_name)

        acq.attrs.start_time = 0.        # float = 0.
        acq.attrs.sample = ""            # str = ''
        acq.attrs.environment = ""       # str = ''
        acq.attrs.description = ""       # str = ''

        # ======================================
        acq_sig = acq.add_acq_sig(name=acquisition_name+"_sig")

        # acq_sig.attrs.type                   # : str = 'Acquisition attributes'
        acq_sig.attrs.start_time = stream[0].stats.starttime.timestamp     # : float = 0.
        acq_sig.attrs.traces_number = len(stream)          # : int = 0
        acq_sig.attrs.position_interval = 0.      # : float = 1.1
        acq_sig.attrs.position_offset = 0.        # : float = 0.1
        acq_sig.attrs.hardware = acquisition_system               # : str = ''

        # ======================================
        gen_sig = acq.add_gen_sig(name=acquisition_name+"_gen")

        # gen_sig.attrs.type                      # : str = 'Generation attributes'
        gen_sig.attrs.points_number = 0           # : int = 0
        gen_sig.attrs.central_freq = 0     # : int = 0
        gen_sig.attrs.sampling_freq = 0  # : int = 0
        gen_sig.attrs.duration = 0.               # : float = 0.1
        gen_sig.attrs.transducer = ""       # : str = 'transducer'
        gen_sig.attrs.hardware = acquisition_system           # : str = ''
        gen_sig.attrs.amplitude = 0.              # : float = 0.1
        gen_sig.attrs.position_x = stream[0].stats.source_x
        gen_sig.attrs.position_y = stream[0].stats.source_y
        gen_sig.attrs.position_z = stream[0].stats.source_z

        # ======================================
        for ntrace, trace in enumerate(stream):
            trace: obspy.core.trace.Trace
            acq_trace = acq_sig.add_trace(name=f"trace{ntrace}")

            acq_trace.data = trace.data

            avg = 0
            for _ in trace.stats.seg2.NOTE:
                if _.startswith('NB_AVG'):
                    avg = int(_.split()[1])
                    break

            # champs fixes
            acq_trace.attrs.columns = ["wavefield"]
            acq_trace.attrs.units = ['nanometers']
            acq_trace.attrs.start_time = trace.stats.starttime.timestamp
            acq_trace.attrs.duration = trace.stats.npts * trace.stats.delta
            acq_trace.attrs.position_x = trace.stats.receiver_x
            acq_trace.attrs.position_y = trace.stats.receiver_y
            acq_trace.attrs.position_z = trace.stats.receiver_z
            acq_trace.attrs.points_number = trace.stats.npts
            acq_trace.attrs.range = 0
            acq_trace.attrs.sampling_freq = trace.stats.sampling_rate
            acq_trace.attrs.channel = trace.stats.channel
            acq_trace.attrs.index = ntrace
            acq_trace.attrs.average_number = avg
            acq_trace.attrs.pretrig_duration= -float(trace.stats.seg2.DELAY)

            # champs optionnels
            for key, val in trace.stats.seg2.items():
                setattr(acq_trace.attrs, key, str(val))
                # print(key, acq_trace.attrs.__getattribute__(key))

            print(acq_trace.attrs) # => n'affiche pas les cles optionnelles
            print(acq_trace.data)
            print()
    return datamodel



if __name__ == '__main__':

    datamodel = create_hdf5_model(
        filename_out = "toto.h5",
        acquisition_system = "MUSC",
        dataset_name = "MON_DATASET_20250218",
        filenames_in = glob.glob("../filesamples/seg2file_musc*.sg2"),
        )

    datamodel.to_hdf5_file()







