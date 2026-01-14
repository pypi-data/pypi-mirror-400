"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h
from multiprocessing.shared_memory import SharedMemory as shared_memory_t

import numpy as nmpy

array_t = nmpy.ndarray

LENGTH_DTYPE = nmpy.uint64
HEADER_SIZE = 3


def NewSharedArray(
    array: array_t, /, *, name: str | None = None
) -> tuple[array_t, str, shared_memory_t]:
    """
    Buffer:
        - dtype: 1 byte
        - order: 1 byte
        - dimension: 1 byte
        - shape: dimension * 8 bytes (nmpy.uint64)
        - array content
    When not needed anymore, call close then unlink on raw.
    """
    assert array.ndim < 256  # Because it will be stored in a byte.

    shape = nmpy.array(array.shape, dtype=LENGTH_DTYPE)
    assert shape.shape == (array.ndim,)  # Just in case of API change.

    while True:
        try:
            raw = shared_memory_t(
                name=name, create=True, size=HEADER_SIZE + shape.nbytes + array.nbytes
            )
        except FileExistsError:
            name += chr(nmpy.random.randint(65, high=91))
        else:
            name = raw.name
            break

    enumeration_order: h.Literal["C", "F"]
    if array.flags["C_CONTIGUOUS"]:
        enumeration_order = "C"
    else:
        enumeration_order = "F"

    raw.buf[0] = ord(array.dtype.char)
    raw.buf[1] = ord(enumeration_order)
    raw.buf[2] = array.ndim

    shape_buffer_portion = nmpy.ndarray(
        (array.ndim,), dtype=LENGTH_DTYPE, buffer=raw.buf[HEADER_SIZE:]
    )
    shape_buffer_portion[...] = shape

    shaped = nmpy.ndarray(
        array.shape,
        dtype=array.dtype,
        order=enumeration_order,
        buffer=raw.buf[(HEADER_SIZE + shape.nbytes) :],
    )
    shaped[...] = array

    return shaped, name, raw


def AdditionalSharedCopy(name: str, /) -> tuple[array_t, shared_memory_t]:
    """
    When not needed anymore, call close on raw.
    """
    raw = shared_memory_t(name)

    dtype_code = chr(raw.buf[0])
    enumeration_order = chr(raw.buf[1])
    dimension = raw.buf[2]
    shape = nmpy.ndarray((dimension,), dtype=LENGTH_DTYPE, buffer=raw.buf[HEADER_SIZE:])

    return (
        nmpy.ndarray(
            shape,
            dtype=dtype_code,
            order=enumeration_order,
            buffer=raw.buf[(HEADER_SIZE + shape.nbytes) :],
        ),
        raw,
    )


def DisposeOriginalSharedArray(raw: shared_memory_t, /) -> None:
    """"""
    raw.close()
    raw.unlink()


def DisposeSharedArrayCopy(raw: shared_memory_t, /) -> None:
    """"""
    raw.close()
