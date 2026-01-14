"""
[`TokenizeCodec`][numcodecs_tokenize.TokenizeCodec] for the [`numcodecs`][numcodecs] buffer compression API.
"""

__all__ = ["TokenizeCodec"]

from io import BytesIO

import leb128
import numcodecs.compat
import numcodecs.registry
import numpy as np
from numcodecs.abc import Codec

from .typing import S, T, U


class TokenizeCodec(Codec):
    """
    Codec that tokenizes the unique data values and encodes the token indices
    and token lookup table.

    Encoding produces a 1D array of unsigned integers, most of which will be
    the token indices. Tokenization can improve compressibility since the
    indices may only require a smaller data type and may have many zero bytes.
    Applying a byte shuffle codec after tokenization can improve compression
    by a byte-based lossless compressor.
    """

    __slots__ = ()

    codec_id: str = "tokenize"  # type: ignore

    def encode(
        self, buf: np.ndarray[S, np.dtype[T]]
    ) -> np.ndarray[tuple[int], np.dtype[U]]:
        """
        Encode the data in `buf` by tokenizing the unique values in `buf`.

        Parameters
        ----------
        buf : np.ndarray[S, np.dtype[T]]
            Array to be tokenized.

        Returns
        -------
        enc : np.ndarray[tuple[int], np.dtype[U]]
            Tokenized 1D array with an unsigned integer dtype.
        """

        a = numcodecs.compat.ensure_ndarray(buf)
        dtype, shape = a.dtype, a.shape
        a = _as_bits(a.flatten())

        # FIXME: MPSV 3.11 numpy 2.3: sorted=True
        unique, inverse, counts = np.unique(a, return_inverse=True, return_counts=True)
        argsort = np.argsort(-counts, stable=True)  # sort with decreasing order
        argsortinv = np.argsort(argsort, stable=True)

        # message: dtype shape [padding] table indices
        message: list[bytes | bytearray] = []

        message.append(leb128.u.encode(len(dtype.str)))
        message.append(dtype.str.encode("ascii"))

        message.append(leb128.u.encode(len(shape)))
        for s in shape:
            message.append(leb128.u.encode(s))

        message.append(leb128.u.encode(unique.size))

        # select the smallest output data type that can encode the indices
        utype: np.dtype[np.unsignedinteger]
        if unique.size <= 2**8:
            utype = np.dtype(np.uint8)
        elif unique.size <= 2**16:
            utype = np.dtype(np.uint16)
        elif unique.size <= 2**32:
            utype = np.dtype(np.uint32)
        elif unique.size <= 2**64:
            utype = np.dtype(np.uint64)
        else:
            utype = a.dtype

        assert (dtype.itemsize % utype.itemsize) == 0

        # insert padding to align with itemsize
        message.append(
            b"\0" * (utype.itemsize - (sum(len(m) for m in message) % utype.itemsize))
        )

        # ensure that the table keys are encoded in little endian binary
        table_keys_array = unique[argsort]
        message.append(
            table_keys_array.astype(table_keys_array.dtype.newbyteorder("<")).tobytes()
        )

        indices = argsortinv[inverse].astype(utype)
        message.append(indices.astype(indices.dtype.newbyteorder("<")).tobytes())

        encoded_bytes = b"".join(message)

        encoded: np.ndarray[tuple[int], np.dtype[np.unsignedinteger]] = np.frombuffer(
            encoded_bytes,
            dtype=utype.newbyteorder("<"),
            count=len(encoded_bytes) // utype.itemsize,
        )

        return encoded  # type: ignore

    def decode(
        self,
        buf: np.ndarray[tuple[int], np.dtype[U]],
        out: None | np.ndarray[S, np.dtype[T]] = None,
    ) -> np.ndarray[S, np.dtype[T]]:
        """
        Decode the data in `buf`.

        Parameters
        ----------
        buf : np.ndarray[tuple[int], np.dtype[U]]
            Tokenized 1D array with an unsigned integer dtype.
        out : None | np.ndarray[S, np.dtype[T]]
            Writeable array to store decoded data.

        Returns
        -------
        dec : np.ndarray[S, np.dtype[T]]
            Un-tokenized array.
        """

        b = numcodecs.compat.ensure_bytes(buf)
        b_io = BytesIO(b)

        dtype = np.dtype(b_io.read(leb128.u.decode_reader(b_io)[0]).decode("ascii"))

        shape = tuple(
            leb128.u.decode_reader(b_io)[0]
            for _ in range(leb128.u.decode_reader(b_io)[0])
        )

        table_len, _ = leb128.u.decode_reader(b_io)

        # select the smallest output data type that can encode the indices
        utype: np.dtype[np.unsignedinteger]
        if table_len <= 2**8:
            utype = np.dtype(np.uint8)
        elif table_len <= 2**16:
            utype = np.dtype(np.uint16)
        elif table_len <= 2**32:
            utype = np.dtype(np.uint32)
        elif table_len <= 2**64:
            utype = np.dtype(np.uint64)
        else:
            utype = _dtype_bits(dtype)

        # remove padding to align with itemsize
        b_io.read(utype.itemsize - (b_io.tell() % utype.itemsize))

        # decode the table keys from little endian binary
        # change them back to dtype_bits byte order
        table_keys: np.ndarray = np.frombuffer(
            b_io.read(table_len * dtype.itemsize),
            dtype=_dtype_bits(dtype).newbyteorder("<"),
            count=table_len,
        )

        indices = np.frombuffer(
            b_io.read(),
            dtype=utype.newbyteorder("<"),
            count=np.prod(shape, dtype=np.uintp),
        )

        decoded = (
            table_keys[indices].astype(_dtype_bits(dtype)).view(dtype).reshape(shape)
        )

        return numcodecs.compat.ndarray_copy(decoded, out)  # type: ignore


numcodecs.registry.register_codec(TokenizeCodec)


def _as_bits(a: np.ndarray[S, np.dtype[T]], /) -> np.ndarray[S, np.dtype[U]]:
    """
    Reinterprets the array `a` to its binary (unsigned integer) representation.

    Parameters
    ----------
    a : np.ndarray[S, np.dtype[T]]
        The array to reinterpret as binary.

    Returns
    -------
    binary : np.ndarray[S, np.dtype[U]]
        The binary representation of the array `a`.
    """

    return a.view(_dtype_bits(a.dtype))


def _dtype_bits(dtype: np.dtype[T]) -> np.dtype[U]:
    """
    Converts the `dtype` to its binary (unsigned integer) representation.

    Parameters
    ----------
    dtype : np.dtype[T]
        The dtype to convert.

    Returns
    -------
    binary : np.dtype[U]
        The binary dtype with equivalent size and alignment but unsigned
        integer kind.
    """

    return np.dtype(dtype.str.replace("f", "u").replace("i", "u"))
