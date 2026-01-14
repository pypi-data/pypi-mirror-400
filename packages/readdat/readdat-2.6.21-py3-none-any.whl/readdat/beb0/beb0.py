from typing import Optional
import os
import ctypes as ct
import numpy as np


# === load the compiled library
# TODO : find way to compile in the python setup file (linux & windows?)
SOFILE = os.path.join(
    os.path.dirname(__file__),
    os.path.basename(__file__).replace('.py', '.so'))

if not os.path.isfile(SOFILE):
    raise ImportError(f'could not find {SOFILE=}')

LIB = ct.cdll.LoadLibrary(SOFILE)


# === define the mirror python class & signatures
class _Beb0Struct(ct.Structure):
    """
    TODO: find a way to build this structure dynamically from the c code
    """
    _fields_ = [
        ('file_type', ct.c_uint32),
        ('version', ct.c_uint32),
        ('sampling_rate', ct.c_uint32),
        ('number_of_samples', ct.c_uint32),
        ('data_pointer', ct.POINTER(ct.c_double)),
        ]


# TODO : find a way to declrare the function signatures dynamically
LIB.display_beb0.argtypes = [_Beb0Struct]

LIB.read_beb0.restype = ct.c_int
LIB.read_beb0.argtypes = [ct.c_char_p, ct.POINTER(_Beb0Struct)]

LIB.write_beb0.restype = ct.c_int
LIB.write_beb0.argtypes = [_Beb0Struct, ct.c_char_p]

LIB.free_beb0.restype = ct.c_int
LIB.free_beb0.argtypes = [_Beb0Struct]


# === High level class for python
class Beb0File(_Beb0Struct):

    def __init__(self, file_type=0xbe0be0, version=1, sampling_rate=0, number_of_samples=0, data=None):

        if data is None:
            data = np.zeros(number_of_samples, np.dtype('double'))

        elif isinstance(data, np.ndarray):
            if data.dtype != np.dtype('double'):
                data = data.astype('double')

            assert data.shape == (number_of_samples, )

        else:
            raise TypeError(type(data))

        # the ctypes structure must be instantiated with the data pointer, not the data array
        data_pointer = data.ctypes.data_as(ct.POINTER(ct.c_double))

        _Beb0Struct.__init__(self,
            np.uint32(file_type),
            np.uint32(version),
            np.uint32(sampling_rate),
            np.uint32(number_of_samples),
            data_pointer,
            )

        # store a reference to the numpy object
        self._data = data

    @property
    def data(self):
        """Expose directement les données C comme un tableau NumPy."""
        if self.data_pointer:
            return np.ctypeslib.as_array(self.data_pointer, shape=(self.number_of_samples,))
        else:
            return np.array([])

    def display(self):
        LIB.display_beb0(self)
        print('[python]', self.data)

    def write(self, filename: str):
        """initiate self from a file
        usage:
        beb0 = Beb0File().from_file('filename.beb0')
        """
        assert filename.endswith('.beb0')
        LIB.write_beb0(self, filename.encode())
        return self

    def from_file(self, filename: str):
        LIB.read_beb0(filename.encode(), ct.byref(self))
        return self

    def __del__(self):
        print('>> del')
        LIB.free_beb0(self)


if __name__ == '__main__':
    print('MAIN PYTHON')
    if True:
        print("# === test 1: create structure in python and display")
        bf = Beb0File(
            0xBEB0BEB0, 1, 100000, 4,
            data=np.arange(4, dtype=np.dtype('double')))

        bf.display()
        del bf

    if True:
        print("# === test 2: read a file and display")
        bf = Beb0File().from_file("toto.beb0")
        bf.data_pointer[1] += 1000.
        bf.data[1] += 1000.
        bf.display()
        del bf  # explicitly free the memory allocated by C

    if True:
        print("# === test 3: read a file, modify in python, write in c")
        bf = Beb0File().from_file("toto.beb0")
        bf.version = 12346
        bf.data_pointer[4] = 12.3456789  # marche
        bf.write('tutu.beb0')
        del bf
        # re-read the new file
        bf = Beb0File().from_file("tutu.beb0")
        # try modifying a numpy array that was allocated in C
        bf.data[::2] = -1.0
        bf.display()
        # freeing done by the python garbage collector !!

