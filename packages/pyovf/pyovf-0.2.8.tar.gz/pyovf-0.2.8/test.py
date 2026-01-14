# (c) 2024 by Prof. Flavio ABREU ARAUJO. All rights reserved.

import pyovf
import numpy as np

print(f'pyOVF version: {pyovf.__version__}')

#* Create a (2, 2, 2, 3) ndarray representing a fictive vector field
data_in = np.array([[[[1.1, 1.2, 1.3],   # vector @ z-comp 0, y-comp 0, x-comp 0
                      [1.4, 1.5, 1.6]],  # vector @ z-comp 0, y-comp 0, x-comp 1
                     [[2.1, 2.2, 2.3],   # vector @ z-comp 0, y-comp 1, x-comp 0
                      [2.4, 2.5, 2.6]]], # vector @ z-comp 0, y-comp 1, x-comp 1
                    [[[3.1, 3.2, 3.3],   # vector @ z-comp 1, y-comp 0, x-comp 0
                      [3.4, 3.5, 3.6]],  # vector @ z-comp 1, y-comp 0, x-comp 1
                     [[4.1, 4.2, 4.3],   # vector @ z-comp 1, y-comp 1, x-comp 0
                      [4.4, 4.5, 4.6]]], # vector @ z-comp 1, y-comp 1, x-comp 1
                   ], dtype=np.float32)

#* Writes data_in into file
pyovf.write('test.ovf', data_in, title="J", Xlim=[0,10e-9],
                Ylim=[0,10e-9], Zlim=[0,10e-9])

#* Reads data and meshgrid (X, Y) from file
X, Y, data_out = pyovf.read('test.ovf', return_mesh=True)
#?INFO output format => data_out[z-comp, y-comp, x-comp, vect-comp]
#?INFO vect-comp = 0 for scalar field data (geam, etc.)
#?INFO vect-comp = {0, 1, 2} for scalar field data (m, B_ext, etc.)
print(data_out.shape)

#? Checks if the data elements correspond
if (data_in == data_out.squeeze()).all():
    print('Test passed!')

#* Reads data (only) from file
data_out2 = pyovf.read_data_only('test.ovf')
#?INFO read_data_only applies squeeze(), so z-comp may desappear
#?INFO if data is scalar field, the vect-comp also desappears
print(data_out2.shape)

#? Checks if the data elements correspond
if (data_in == data_out2).all():
    print('Test passed!')
