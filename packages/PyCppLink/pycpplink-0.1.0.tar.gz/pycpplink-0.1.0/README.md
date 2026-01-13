# PyCppLink

A Python library that provides direct access to advanced C++ functionality including memory pools, data processing, and error handling.

## Features

- **Memory Pool**: Efficient stack-based memory management with zero-copy operations
- **Advanced Processor**: High-performance data processing with C++ backend
- **Pointer Operations**: Comprehensive pointer manipulation for low-level memory access
- **Error Handling**: Comprehensive error reporting with detailed messages
- **Cross-platform**: Works on Windows, Linux, and macOS

## Installation

### From Source

```bash
cd pycpplink
pip install .
```

### Development Mode

```bash
cd pycpplink
pip install -e .
```

## Usage

### Basic Example

```python
from pycpplink import MemoryPool, AdvancedProcessor, PyCPPError

try:
    # Create a memory pool
    pool = MemoryPool()
    print(f"Memory pool created with {pool.get_remaining()} bytes remaining")

    # Create a processor
    processor = AdvancedProcessor(pool)

    # Initialize data
    processor.init_data(10)
    print("Data initialized with 10 elements")

    # Process data
    processor.process_data(0, 100)
    processor.process_data(5, 500)

    # Get data
    value = processor.get_data(0)
    print(f"Value at index 0: {value}")

    value = processor.get_data(5)
    print(f"Value at index 5: {value}")

    # Reset memory pool
    pool.reset()
    print("Memory pool reset")

except PyCPPError as e:
    print(f"Error occurred: {e}")
```

### Advanced Example

```python
from pycpplink import MemoryPool, AdvancedProcessor, PyCPPError

def process_large_dataset():
    pool = MemoryPool()
    processor = AdvancedProcessor(pool)

    try:
        # Initialize with maximum allowed size
        processor.init_data(100)

        # Process all elements
        for i in range(100):
            processor.process_data(i, i * 10)

        # Verify data
        for i in range(100):
            value = processor.get_data(i)
            assert value == i * 10, f"Expected {i * 10}, got {value}"

        print("All data processed successfully!")

### Pointer Operations Example

```python
from pycpplink import MemoryPool, Pointer, PyCPPError

def pointer_operations():
    pool = MemoryPool()

    try:
        # Allocate memory
        ptr = pool.allocate(64)
        print(f"Allocated {ptr.size} bytes")

        # Write various data types
        ptr.write_byte(0, 0x01)
        ptr.write_short(1, 0x0203)
        ptr.write_int(3, 0x04050607)
        ptr.write_long(7, 0x08090A0B0C0D0E0F)
        ptr.write_float(15, 3.14159)
        ptr.write_double(19, 2.71828)

        # Read back
        print(f"Byte: {hex(ptr.read_byte(0))}")
        print(f"Short: {hex(ptr.read_short(1))}")
        print(f"Int: {hex(ptr.read_int(3))}")
        print(f"Long: {hex(ptr.read_long(7))}")
        print(f"Float: {ptr.read_float(15)}")
        print(f"Double: {ptr.read_double(19)}")

        # Pointer offset
        offset_ptr = ptr.offset(10)
        print(f"Read from offset: {hex(offset_ptr.read_byte(0))}")

        # Memory copy
        ptr2 = pool.allocate(64)
        ptr.copy(ptr2, 32)
        print(f"Copied value: {hex(ptr2.read_int(3))}")

        # Memory fill
        ptr.fill(0xFF, 20)
        print(f"Filled value: {hex(ptr.read_byte(5))}")

        # Memory zero
        ptr.zero()
        print(f"Zeroed value: {hex(ptr.read_byte(0))}")

    except PyCPPError as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    pointer_operations()
```

## API Reference

### MemoryPool

#### Methods

- `allocate(size: int) -> Pointer`: Allocate memory from the pool
- `reset()`: Reset the memory pool
- `get_remaining() -> int`: Get remaining bytes in the pool

### AdvancedProcessor

#### Methods

- `init_data(length: int)`: Initialize data array (1-100 elements)
- `process_data(index: int, value: int)`: Set value at index
- `get_data(index: int) -> int`: Get value at index
- `get_last_error() -> Tuple[int, str]`: Get last error code and message

### Pointer

#### Methods

**Write Operations:**
- `write_byte(offset: int, value: int)`: Write a byte (8-bit) at the specified offset
- `write_short(offset: int, value: int)`: Write a short (16-bit) at the specified offset
- `write_int(offset: int, value: int)`: Write an int (32-bit) at the specified offset
- `write_long(offset: int, value: int)`: Write a long (64-bit) at the specified offset
- `write_float(offset: int, value: float)`: Write a float (32-bit) at the specified offset
- `write_double(offset: int, value: float)`: Write a double (64-bit) at the specified offset

**Read Operations:**
- `read_byte(offset: int) -> int`: Read a byte (8-bit) from the specified offset
- `read_short(offset: int) -> int`: Read a short (16-bit) from the specified offset
- `read_int(offset: int) -> int`: Read an int (32-bit) from the specified offset
- `read_long(offset: int) -> int`: Read a long (64-bit) from the specified offset
- `read_float(offset: int) -> float`: Read a float (32-bit) from the specified offset
- `read_double(offset: int) -> float`: Read a double (64-bit) from the specified offset

**Memory Operations:**
- `offset(offset: int) -> Pointer`: Create a new pointer with the specified byte offset
- `copy(dest: Pointer, size: int)`: Copy memory to another pointer
- `compare(other: Pointer, size: int) -> int`: Compare memory with another pointer (returns -1, 0, or 1)
- `fill(value: int, size: int)`: Fill memory with a byte value
- `zero()`: Zero all memory in the pointer

**Properties:**
- `address -> int`: Get the memory address of the pointer
- `size -> int`: Get the size of the allocated memory

### PyCPPError

Exception raised when C++ operations fail.

#### Attributes

- `code`: Error code (int)
- `message`: Error message (str)

## Error Codes

- `0`: Success
- `1`: Memory allocation failed
- `2`: Invalid parameter
- `3`: Out of range
- `4`: Internal error

## Building from Source

The library automatically compiles the C++ code during installation. No pre-compiled binaries are required.

### Requirements

- Python 3.7+
- C++ compiler (MSVC on Windows, GCC on Linux, Clang on macOS)

### Build Commands

```bash
# Build wheel
python setup.py bdist_wheel

# Install from wheel
pip install dist/pycpp-0.1.0-*.whl
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
