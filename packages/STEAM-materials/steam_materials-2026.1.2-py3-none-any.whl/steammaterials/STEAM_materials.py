import ctypes as ct
import os
import platform
import numpy as np
from pathlib import Path
from numpy.ctypeslib import ndpointer
#import matlab.engine


class STEAM_materials:

    def __init__(self, func_name, n_arg, n_points, material_objects_path: os.PathLike=None):
        """
        :param func_name: string with function name corresponding to dll file name (without the .dll in the string)
        :param n_arg:	number of arguments of the func_name function. This corresponds to number of columns in 2D numpy array, numpy2d, to be used in the method. Use numpy2d.shape[1] to get the number.
        :param n_points: number of points to evaluate. This corresponds to number of rows in 2D numpy array, numpy2d, to be used in the eval method. Use numpy2d.shape[0] to get the number.
        :param material_objects_path: If not specified, the code assumes the .dll files are in a folder called CFUN in the same directory as this script. Otherwise a full path to a folder needs to be given.
        """
        if material_objects_path is not None:
            dll_path: Path = Path(material_objects_path)  # allows user to specify full path to folder with .dlls
        else:
            dll_path: Path = Path(__file__).parent / 'CFUN'  # Assumes .dlls are in a folder called CFUN in the same directory as this script

        if platform.system() == 'Windows':
            self._dll_name = f'{func_name}.dll'
        elif platform.system() == 'Linux':
            self._dll_name = f'lib{func_name}.so'
        else:
            raise NotImplementedError(f'Platform "{platform.system()}" is not supported!')

        _dll = ct.CDLL(str(dll_path / self._dll_name))
        self.func_name = func_name.encode('ascii')
        self.n_points = n_points
        self.n_arg = n_arg
        array_type = ct.c_double * self.n_points
        self.RealPtr = array_type()
        self.Int_Ptr = array_type()
        str_type_yaml = ct.c_char_p
        self.yaml_string = str_type_yaml()
        _doublepp = ndpointer(dtype=np.uintp, ndim=1, flags='C')
        f_name = ct.c_char_p
        n_arg = ct.c_int
        b_size = ct.c_int
        ifail = ct.c_long
        _dll.init.argtypes = []
        _dll.init.restype = ct.c_long
        self.eval = _dll.eval
        self.eval.argtypes = [f_name, n_arg, _doublepp, _doublepp, b_size, array_type, array_type]
        self.eval.restype = ifail
        # Binding to the shared library error function
        try:
            self.return_test_yaml = _dll.return_test_yaml
            self.return_test_yaml.argtypes = []
            self.return_test_yaml.restype = str_type_yaml
        except:
            pass
        try:
            self.getLastError = _dll.getLastError
            self.getLastError.restype = ct.c_char_p
        except AttributeError:
            self.getLastError = None

    def evaluate(self, numpy2d):
        """
        DLL funcion call. It can take a tuple with arguments or numpy array where each row is a set of arguments
        :param numpy2d: Numpy array with number of columns corresponding to number of function arguments and points to evaluate in rows
        :return: Numpy array with values calculated by .dll function
        """
        if not isinstance(numpy2d, np.ndarray):
            numpy2d = np.array(numpy2d, dtype=np.float64, order='C')
        else:
            numpy2d = np.ascontiguousarray(numpy2d, dtype=np.float64)
        inReal = (numpy2d.__array_interface__['data'][0] + np.arange(numpy2d.shape[0]) * numpy2d.strides[0]).astype(np.uintp)
        error_out = self.eval(self.func_name, self.n_arg, inReal, inReal, self.n_points, self.RealPtr, self.Int_Ptr)
        if error_out == 1:
            pass
        else:
            if self.getLastError:
                err = self.getLastError().decode('ascii')
            else:
                err = '[No message. Material does not implement getLastError]'
            raise ValueError(f"There was a problem with calling {self._dll_name} with arguments {numpy2d}. \nError: {err}")
        return np.array(self.RealPtr)

    def get_yaml_name(self):
        """
        DLL funcion call. It will output the test filename.
        """
        string_out = self.return_test_yaml()
        return string_out.decode('utf-8')


class STEAM_materials_Matlab:
    def __init__(self,func_name:str,arg_list:str):
        self.arguments=arg_list
        self.func=func_name

    def evaluate(self):
        eng = matlab.engine.start_matlab()
        result=eng.eval(self.func+self.arguments)
        print(result)

