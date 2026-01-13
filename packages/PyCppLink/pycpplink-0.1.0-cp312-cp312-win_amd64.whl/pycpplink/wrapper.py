import ctypes
import os
from typing import Optional, Tuple

class ErrorInfo(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_int),
        ("msg", ctypes.c_char * 128),
    ]

ErrorCode = ctypes.c_int

class PyCPPError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Error {code}: {message}")

class MemoryPool:
    def __init__(self):
        self._lib = self._load_library()
        self._pool = None
        self._initialize()

    def _load_library(self):
        import glob
        
        # Try to find the compiled library with platform-specific naming
        lib_dir = os.path.dirname(__file__)
        
        # Look for .pyd files (Windows)
        pyd_files = glob.glob(os.path.join(lib_dir, '_core*.pyd'))
        if pyd_files:
            lib_path = pyd_files[0]
        else:
            # Look for .so files (Linux/macOS)
            so_files = glob.glob(os.path.join(lib_dir, '_core*.so'))
            if so_files:
                lib_path = so_files[0]
            else:
                # Look for .dll files (Windows alternative)
                dll_files = glob.glob(os.path.join(lib_dir, '_core*.dll'))
                if dll_files:
                    lib_path = dll_files[0]
                else:
                    raise FileNotFoundError(f"Could not find compiled library in {lib_dir}. Expected one of: _core*.pyd, _core*.so, _core*.dll")
        
        lib = ctypes.CDLL(lib_path)
        
        lib.memory_pool_create.argtypes = [ctypes.POINTER(ErrorInfo)]
        lib.memory_pool_create.restype = ctypes.c_void_p
        
        lib.memory_pool_destroy.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.memory_pool_destroy.restype = None
        
        lib.memory_pool_allocate.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.memory_pool_allocate.restype = ctypes.c_void_p
        
        lib.memory_pool_reset.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.memory_pool_reset.restype = None
        
        lib.memory_pool_get_remaining.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.memory_pool_get_remaining.restype = ctypes.c_uint32
        
        lib.processor_create.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.processor_create.restype = ctypes.c_void_p
        
        lib.processor_destroy.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.processor_destroy.restype = None
        
        lib.processor_init_data.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        lib.processor_init_data.restype = ctypes.c_int
        
        lib.processor_process_data.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int]
        lib.processor_process_data.restype = ctypes.c_int
        
        lib.processor_get_data.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorCode)]
        lib.processor_get_data.restype = ctypes.c_int
        
        lib.processor_get_last_error.argtypes = [ctypes.c_void_p, ctypes.POINTER(ErrorInfo)]
        lib.processor_get_last_error.restype = None
        
        lib.pointer_write_byte.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint8]
        lib.pointer_write_byte.restype = ctypes.c_int
        
        lib.pointer_write_short.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int16]
        lib.pointer_write_short.restype = ctypes.c_int
        
        lib.pointer_write_int.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int32]
        lib.pointer_write_int.restype = ctypes.c_int
        
        lib.pointer_write_long.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int64]
        lib.pointer_write_long.restype = ctypes.c_int
        
        lib.pointer_write_float.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_float]
        lib.pointer_write_float.restype = ctypes.c_int
        
        lib.pointer_write_double.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_double]
        lib.pointer_write_double.restype = ctypes.c_int
        
        lib.pointer_read_byte.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_byte.restype = ctypes.c_uint8
        
        lib.pointer_read_short.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_short.restype = ctypes.c_int16
        
        lib.pointer_read_int.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_int.restype = ctypes.c_int32
        
        lib.pointer_read_long.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_long.restype = ctypes.c_int64
        
        lib.pointer_read_float.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_float.restype = ctypes.c_float
        
        lib.pointer_read_double.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ErrorInfo)]
        lib.pointer_read_double.restype = ctypes.c_double
        
        lib.pointer_offset.argtypes = [ctypes.c_void_p, ctypes.c_int32]
        lib.pointer_offset.restype = ctypes.c_void_p
        
        lib.pointer_copy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        lib.pointer_copy.restype = ctypes.c_int
        
        lib.pointer_compare.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        lib.pointer_compare.restype = ctypes.c_int
        
        lib.pointer_fill.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint32]
        lib.pointer_fill.restype = ctypes.c_int
        
        lib.pointer_zero.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        lib.pointer_zero.restype = None
        
        return lib

    def _initialize(self):
        err = ErrorInfo()
        self._pool = self._lib.memory_pool_create(ctypes.byref(err))
        if self._pool is None:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))

    def allocate(self, size: int) -> 'Pointer':
        err = ErrorInfo()
        ptr = self._lib.memory_pool_allocate(ctypes.c_void_p(self._pool), ctypes.c_uint32(size), ctypes.byref(err))
        if ptr is None:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return Pointer(self._lib, ptr, size)

    def reset(self):
        err = ErrorInfo()
        self._lib.memory_pool_reset(ctypes.c_void_p(self._pool), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))

    def get_remaining(self) -> int:
        err = ErrorInfo()
        remaining = self._lib.memory_pool_get_remaining(ctypes.c_void_p(self._pool), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return remaining

    def __del__(self):
        if self._pool is not None and self._lib is not None:
            err = ErrorInfo()
            self._lib.memory_pool_destroy(ctypes.c_void_p(self._pool), ctypes.byref(err))

class AdvancedProcessor:
    def __init__(self, pool: MemoryPool):
        self._lib = pool._lib
        self._pool = pool._pool
        self._processor = None
        self._initialize()

    def _initialize(self):
        err = ErrorInfo()
        self._processor = self._lib.processor_create(ctypes.c_void_p(self._pool), ctypes.byref(err))
        if self._processor is None:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))

    def init_data(self, length: int):
        if length <= 0 or length > 100:
            raise ValueError("Data length must be between 1 and 100")
        
        err_code = self._lib.processor_init_data(ctypes.c_void_p(self._processor), ctypes.c_uint32(length))
        if err_code != 0:
            err = ErrorInfo()
            self._lib.processor_get_last_error(ctypes.c_void_p(self._processor), ctypes.byref(err))
            raise PyCPPError(err_code, err.msg.decode('utf-8'))

    def process_data(self, index: int, value: int):
        err_code = self._lib.processor_process_data(
            ctypes.c_void_p(self._processor), 
            ctypes.c_uint32(index), 
            ctypes.c_int(value)
        )
        if err_code != 0:
            err = ErrorInfo()
            self._lib.processor_get_last_error(ctypes.c_void_p(self._processor), ctypes.byref(err))
            raise PyCPPError(err_code, err.msg.decode('utf-8'))

    def get_data(self, index: int) -> int:
        err_code = ErrorCode()
        value = self._lib.processor_get_data(ctypes.c_void_p(self._processor), ctypes.c_uint32(index), ctypes.byref(err_code))
        if err_code.value != 0:
            err = ErrorInfo()
            self._lib.processor_get_last_error(ctypes.c_void_p(self._processor), ctypes.byref(err))
            raise PyCPPError(err_code.value, err.msg.decode('utf-8'))
        return value

    def get_last_error(self) -> Tuple[int, str]:
        err = ErrorInfo()
        self._lib.processor_get_last_error(ctypes.c_void_p(self._processor), ctypes.byref(err))
        return (err.code, err.msg.decode('utf-8'))

    def __del__(self):
        if self._processor is not None and self._lib is not None:
            err = ErrorInfo()
            self._lib.processor_destroy(ctypes.c_void_p(self._processor), ctypes.byref(err))

class Pointer:
    def __init__(self, lib: ctypes.CDLL, ptr: ctypes.c_void_p, size: int = 0):
        self._lib = lib
        self._ptr = ptr
        self._size = size

    def write_byte(self, offset: int, value: int):
        err_code = self._lib.pointer_write_byte(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_uint8(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write byte")

    def write_short(self, offset: int, value: int):
        err_code = self._lib.pointer_write_short(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_int16(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write short")

    def write_int(self, offset: int, value: int):
        err_code = self._lib.pointer_write_int(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_int32(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write int")

    def write_long(self, offset: int, value: int):
        err_code = self._lib.pointer_write_long(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_int64(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write long")

    def write_float(self, offset: int, value: float):
        err_code = self._lib.pointer_write_float(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_float(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write float")

    def write_double(self, offset: int, value: float):
        err_code = self._lib.pointer_write_double(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.c_double(value))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to write double")

    def read_byte(self, offset: int) -> int:
        err = ErrorInfo()
        value = self._lib.pointer_read_byte(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def read_short(self, offset: int) -> int:
        err = ErrorInfo()
        value = self._lib.pointer_read_short(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def read_int(self, offset: int) -> int:
        err = ErrorInfo()
        value = self._lib.pointer_read_int(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def read_long(self, offset: int) -> int:
        err = ErrorInfo()
        value = self._lib.pointer_read_long(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def read_float(self, offset: int) -> float:
        err = ErrorInfo()
        value = self._lib.pointer_read_float(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def read_double(self, offset: int) -> float:
        err = ErrorInfo()
        value = self._lib.pointer_read_double(ctypes.c_void_p(self._ptr), ctypes.c_uint32(offset), ctypes.byref(err))
        if err.code != 0:
            raise PyCPPError(err.code, err.msg.decode('utf-8'))
        return value

    def offset(self, offset: int):
        new_ptr = self._lib.pointer_offset(ctypes.c_void_p(self._ptr), ctypes.c_int32(offset))
        if new_ptr is None:
            raise ValueError("Failed to offset pointer")
        return Pointer(self._lib, new_ptr, self._size - offset if offset > 0 else self._size + offset)

    def copy(self, dest: 'Pointer', size: int):
        err_code = self._lib.pointer_copy(ctypes.c_void_p(dest._ptr), ctypes.c_void_p(self._ptr), ctypes.c_uint32(size))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to copy memory")

    def compare(self, other: 'Pointer', size: int) -> int:
        result = self._lib.pointer_compare(ctypes.c_void_p(self._ptr), ctypes.c_void_p(other._ptr), ctypes.c_uint32(size))
        return result

    def fill(self, value: int, size: int):
        err_code = self._lib.pointer_fill(ctypes.c_void_p(self._ptr), ctypes.c_uint32(self._size), ctypes.c_uint8(value), ctypes.c_uint32(size))
        if err_code != 0:
            raise PyCPPError(err_code, "Failed to fill memory")

    def zero(self):
        self._lib.pointer_zero(ctypes.c_void_p(self._ptr), ctypes.c_uint32(self._size))

    @property
    def address(self) -> int:
        return ctypes.addressof(self._ptr.contents) if hasattr(self._ptr, 'contents') else 0

    @property
    def size(self) -> int:
        return self._size
