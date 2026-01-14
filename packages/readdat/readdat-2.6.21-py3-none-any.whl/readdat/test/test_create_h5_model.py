# moved to ABC
# import os
# from readdat.h5.create_h5 import create_hdf5_model
# from readdat.test.test_filesamples import FILESAMPLES
#
# HERE = os.path.dirname(__file__)
# TEST_FILE_OUT = os.path.join(HERE, '_test_file_out.h5')  # WARNING WILL BE DESTROYED BY THE TEST
#
#
# def test_create_h5_model():
#     if os.path.isfile(TEST_FILE_OUT):
#         os.remove(TEST_FILE_OUT)
#
#     assert not os.path.isfile(TEST_FILE_OUT)
#
#     datamodel = create_hdf5_model(
#         filename_out = TEST_FILE_OUT,
#         acquisition_system = "AUTO",
#         dataset_name = "TESTDATASET",
#         filenames_in = [
#             FILESAMPLES["SEG2FILE_MUSC"],
#             FILESAMPLES["SEG2FILE_MUSC1"],
#             ],
#             )
#
#     datamodel.to_hdf5_file()
#
#     assert os.path.isfile(TEST_FILE_OUT)
#
#     # TODO : TEST THE FILE CONTENT
#
#
#     # ============== clean up
#     if os.path.isfile(TEST_FILE_OUT):
#         os.remove(TEST_FILE_OUT)
#     assert not os.path.isfile(TEST_FILE_OUT)