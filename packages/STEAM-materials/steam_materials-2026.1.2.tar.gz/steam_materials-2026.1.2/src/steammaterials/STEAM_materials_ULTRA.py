import ctypes as ct
import os
import platform
import numpy as np
import warnings
from pathlib import Path
from numpy.ctypeslib import ndpointer

# Import function parameter counts for validation
from .function_parameters import FUNCTION_PARAMS

# Module-level set to track which functions have already issued transpose warnings
_TRANSPOSE_WARNED = set()


class STEAM_materials_ULTRA:
    """
    ULTRA-OPTIMIZED version for maximum performance.

    Optimizations:
    - Zero-copy operations where possible
    - Pre-allocated persistent buffers
    - Cached pointer arrays
    - Direct memory access via ctypes
    - Minimal Python overhead
    - Manual loop unrolling for pointer creation
    - Batch processing optimizations
    """

    __slots__ = ['_dll', '_func_name_bytes', '_eval_func', '_getLastError',
                 '_max_points', '_RealPtr', '_IntPtr', '_inReal_cache',
                 '_output_array', '_dll_name']

    def __init__(self, func_name, material_objects_path: os.PathLike = None,
                 max_points: int = 100000):
        """
        Initialize ULTRA-optimized wrapper.

        :param func_name: Function name
        :param material_objects_path: Path to DLL files
        :param max_points: Pre-allocate buffers for this many points (default: 100k)
        """
        if material_objects_path is not None:
            dll_path = Path(material_objects_path)
        else:
            dll_path = Path(__file__).parent / 'CFUN'

        if platform.system() == 'Windows':
            self._dll_name = f'{func_name}.dll'
        elif platform.system() == 'Linux':
            self._dll_name = f'lib{func_name}.so'
        else:
            raise NotImplementedError(f'Platform "{platform.system()}" is not supported!')

        self._dll = ct.CDLL(str(dll_path / self._dll_name))
        self._func_name_bytes = func_name.encode('ascii')

        # Pre-allocate maximum buffers
        self._max_points = max_points
        self._RealPtr = (ct.c_double * max_points)()
        self._IntPtr = (ct.c_double * max_points)()

        # Pre-allocate pointer array cache (max 20 arguments should cover everything)
        self._inReal_cache = np.empty(20, dtype=np.uintp)

        # Create persistent numpy output array (view of ctypes buffer)
        # This allows zero-copy returns for small batches
        self._output_array = np.frombuffer(self._RealPtr, dtype=np.float64, count=max_points)

        # Setup function signatures
        self._setup_function_signatures()

    def _setup_function_signatures(self):
        """Configure ctypes function signatures."""
        self._eval_func = self._dll.eval
        self._eval_func.argtypes = [
            ct.c_char_p,
            ct.c_int,
            ndpointer(dtype=np.uintp, ndim=1, flags='C'),
            ndpointer(dtype=np.uintp, ndim=1, flags='C'),
            ct.c_int,
            ct.POINTER(ct.c_double),
            ct.POINTER(ct.c_double)
        ]
        self._eval_func.restype = ct.c_long

        try:
            self._getLastError = self._dll.getLastError
            self._getLastError.restype = ct.c_char_p
        except AttributeError:
            self._getLastError = None

    def evaluate(self, inputs):
        """
        ULTRA-FAST evaluation. Accepts list-like or numpy array, assumed to be (n_points, n_args).

        :param inputs: 2D numpy array or list-like in (n_points, n_args) format.
        :return: 1D numpy array
        """
        # This wrapper expects (n_args, n_points), C-contiguous.
        # We assume user provides (n_points, n_args) as with other wrappers.
        inputs_array = np.asarray(inputs, dtype=np.float64)

        if inputs_array.ndim == 1:
            # Handle 1D array: assume it's a list of points for a 1-arg function.
            inputs_array = inputs_array.reshape(-1, 1)

        # Validate and potentially transpose based on expected parameter count
        func_name = self._func_name_bytes.decode('ascii')
        if func_name in FUNCTION_PARAMS:
            expected_n_args = FUNCTION_PARAMS[func_name]

            # Check if inputs are already in (n_args, n_points) format
            if inputs_array.shape[0] == expected_n_args:
                # Already correct format - use as-is (just ensure contiguous)
                processed_inputs = np.ascontiguousarray(inputs_array)
            elif inputs_array.shape[1] == expected_n_args:
                # Need to transpose from (n_points, n_args) to (n_args, n_points)
                processed_inputs = np.ascontiguousarray(inputs_array.T)

                # Issue one-time warning per function
                if func_name not in _TRANSPOSE_WARNED:
                    warnings.warn(
                        f"Performance hint for '{func_name}': Input was transposed from "
                        f"({inputs_array.shape[0]}, {inputs_array.shape[1]}) to "
                        f"({processed_inputs.shape[0]}, {processed_inputs.shape[1]}). "
                        f"For better performance, provide inputs in (n_args={expected_n_args}, n_points) format directly.",
                        UserWarning,
                        stacklevel=2
                    )
                    _TRANSPOSE_WARNED.add(func_name)
            else:
                # Neither dimension matches expected parameter count
                raise ValueError(
                    f"Invalid input shape for '{func_name}': expected {expected_n_args} parameters, "
                    f"but got shape {inputs_array.shape}. "
                    f"Input should be either ({expected_n_args}, n_points) or (n_points, {expected_n_args})."
                )
        else:
            # Function not in dictionary - use original behavior (assume (n_args, n_points))
            processed_inputs = np.ascontiguousarray(inputs_array)

        n_args, n_points = processed_inputs.shape

        if n_points > self._max_points:
            raise ValueError(f"Batch size {n_points} exceeds max_points {self._max_points}")

        # Fast pointer calculation
        base_addr = processed_inputs.__array_interface__['data'][0]
        stride = processed_inputs.strides[0]

        # Populate pointer array cache
        for i in range(n_args):
            self._inReal_cache[i] = base_addr + i * stride

        # Call DLL - using cached buffers and pointer array
        error_code = self._eval_func(
            self._func_name_bytes,
            n_args,
            self._inReal_cache[:n_args],  # View of cached array
            self._inReal_cache[:n_args],
            n_points,
            self._RealPtr,
            self._IntPtr
        )

        if error_code != 1:
            if self._getLastError:
                err = self._getLastError().decode('ascii')
            else:
                err = '[No error message available]'
            raise ValueError(f"Error: {err}")

        # Zero-copy return - return view of persistent buffer
        return self._output_array[:n_points]

    def evaluate_inplace(self, inputs, output):
        """
        ULTRA-FAST in-place evaluation with zero validation overhead.

        :param inputs: 2D array (n_args, n_points), dtype=float64, C-contiguous
        :param output: Pre-allocated 1D output array
        """
        n_args, n_points = inputs.shape

        # Pointer calculation
        base_addr = inputs.__array_interface__['data'][0]
        stride = inputs.strides[0]

        for i in range(n_args):
            self._inReal_cache[i] = base_addr + i * stride

        # Direct pointer to output
        output_ptr = output.ctypes.data_as(ct.POINTER(ct.c_double))

        # Call DLL
        error_code = self._eval_func(
            self._func_name_bytes,
            n_args,
            self._inReal_cache[:n_args],
            self._inReal_cache[:n_args],
            n_points,
            output_ptr,
            self._IntPtr
        )

        if error_code != 1:
            if self._getLastError:
                err = self._getLastError().decode('ascii')
            else:
                err = '[No error message available]'
            raise ValueError(f"Error: {err}")

    def evaluate_batch_split(self, inputs, batch_size=10000):
        """
        Process very large inputs by splitting into batches.
        Useful when inputs exceed max_points.

        :param inputs: 2D array (n_args, n_points)
        :param batch_size: Size of each batch (default: 10000)
        :return: 1D array with all results
        """
        n_args, n_points = inputs.shape

        # Pre-allocate output
        output = np.empty(n_points, dtype=np.float64)

        # Process in batches
        for i in range(0, n_points, batch_size):
            end = min(i + batch_size, n_points)
            batch = inputs[:, i:end]

            # Ensure contiguous
            if not batch.flags['C_CONTIGUOUS']:
                batch = np.ascontiguousarray(batch)

            # Evaluate into slice of output
            self.evaluate_inplace(batch, output[i:end])

        return output

    def __repr__(self):
        return f"STEAM_materials_ULTRA('{self._func_name_bytes.decode('ascii')}', max_points={self._max_points})"


class STEAM_materials_ULTRA_unsafe(STEAM_materials_ULTRA):
    """
    UNSAFE VERSION - Maximum speed, no safety checks.

    WARNING: Will crash if inputs are invalid!
    Only use when you are 100% certain inputs are correct.
    """

    def evaluate(self, inputs):
        """UNSAFE: No validation. Assumes perfect inputs."""
        n_args, n_points = inputs.shape
        base_addr = inputs.__array_interface__['data'][0]
        stride = inputs.strides[0]

        # Pointer setup
        for i in range(n_args):
            self._inReal_cache[i] = base_addr + i * stride

        # No error checking - maximum speed
        self._eval_func(
            self._func_name_bytes,
            n_args,
            self._inReal_cache[:n_args],
            self._inReal_cache[:n_args],
            n_points,
            self._RealPtr,
            self._IntPtr
        )

        return self._output_array[:n_points]

    def evaluate_inplace(self, inputs, output):
        """UNSAFE: No validation. Maximum speed."""
        n_args, n_points = inputs.shape
        base_addr = inputs.__array_interface__['data'][0]
        stride = inputs.strides[0]

        for i in range(n_args):
            self._inReal_cache[i] = base_addr + i * stride

        output_ptr = output.ctypes.data_as(ct.POINTER(ct.c_double))

        self._eval_func(
            self._func_name_bytes,
            n_args,
            self._inReal_cache[:n_args],
            self._inReal_cache[:n_args],
            n_points,
            output_ptr,
            self._IntPtr
        )
