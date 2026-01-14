"""
[`BitmapIndexCodec`][numcodecs_bitmap_index.BitmapIndexCodec] for the [`numcodecs`][numcodecs] buffer compression API.
"""

__all__ = ["BitmapIndexCodec"]

from functools import reduce
from io import BytesIO

import leb128
import numcodecs.compat
import numcodecs.registry
import numpy as np
from numcodecs.abc import Codec

from .typing import S, T, U


class BitmapIndexCodec(Codec):
    """
    Codec that uses bitmaps to encode the most frequent bitpatterns in the data
    and encodes any remaining values as-is.

    A simple heuristic is used to only encode bitpatterns with bitmaps where
    the direct savings outweigh the costs. The codec can be configured to bound
    the number of bitmaps or scale the cost.

    Encoding produces a 1D array of unsigned integers with the same itemsize
    as the original data.

    Parameters
    ----------
    max_bitmaps : None | int
        Maximum number of bitmaps to use.
    cost_factor : float
        Factor for the cost of a bitmap. Use >1 if bitmaps compress worse than
        the original data, or <1 if they compress better.
    """

    __slots__: tuple[str, ...] = ("_max_bitmaps", "_cost_factor")
    _max_bitmaps: None | int
    _cost_factor: float

    codec_id: str = "bitmap-index"  # type: ignore

    def __init__(
        self, *, max_bitmaps: None | int = None, cost_factor: float = 1
    ) -> None:
        if max_bitmaps is not None and max_bitmaps <= 0:
            raise ValueError("max_bitmaps must be positive")

        if cost_factor < 0:
            raise ValueError("cost_factor must be non-negative")

        self._max_bitmaps = max_bitmaps
        self._cost_factor = cost_factor

    def encode(
        self, buf: np.ndarray[S, np.dtype[T]]
    ) -> np.ndarray[tuple[int], np.dtype[U]]:
        """
        Encode the data in `buf` by replacing the most frequent bitpatterns
        with bitmaps.

        Parameters
        ----------
        buf : np.ndarray[S, np.dtype[T]]
            Array to be encoded.

        Returns
        -------
        enc : np.ndarray[tuple[int], np.dtype[U]]
            Encoded 1D array with an unsigned integer dtype.
        """

        a = numcodecs.compat.ensure_ndarray(buf)
        dtype, shape = a.dtype, a.shape
        a = _as_bits(a.flatten())

        # FIXME: MPSV 3.11 numpy 2.3: sorted=True
        unique, counts = np.unique(a, return_counts=True)
        argsort = np.argsort(-counts, stable=True)  # sort with decreasing order
        unique, counts = unique[argsort], counts[argsort]

        # savings: bitmap-encoded values only cost 1 bit per element,
        #  so the saving is all the bits we no longer need to store
        bitsavings = counts * (dtype.itemsize * 8 - 1)
        # costs: each bitmap costs 1 bit per (remaining) array element plus the
        #  size of the value that is encoded in the bitmap
        bitcosts = a.size - np.cumsum(counts) + dtype.itemsize * 8

        # encode as many bitmaps as possible while saving bits
        num_bitmaps = (
            int(np.argmax((bitcosts * self._cost_factor) >= bitsavings))
            if counts.size > 0
            else 0
        )
        if self._max_bitmaps is not None:
            num_bitmaps = min(num_bitmaps, self._max_bitmaps)

        # message: dtype shape num-bitmaps { value is-value } [padding] rest
        message: list[bytes | bytearray] = []

        message.append(leb128.u.encode(len(dtype.str)))
        message.append(dtype.str.encode("ascii"))

        message.append(leb128.u.encode(len(shape)))
        for s in shape:
            message.append(leb128.u.encode(s))

        message.append(leb128.u.encode(num_bitmaps))

        for u in unique[:num_bitmaps]:
            # ensure that the values are encoded in little endian binary
            message.append(u.astype(u.dtype.newbyteorder("<")).tobytes())

            is_u = a == u
            packed_is_u = np.packbits(is_u, axis=None, bitorder="big")
            a = np.extract(~is_u, a)

            message.append(packed_is_u.tobytes())

        # insert padding to align with itemsize
        message.append(
            b"\0" * (dtype.itemsize - (sum(len(m) for m in message) % dtype.itemsize))
        )

        # ensure that the values are encoded in little endian binary
        message.append(a.astype(a.dtype.newbyteorder("<")).tobytes())

        encoded_bytes = b"".join(message)

        encoded: np.ndarray[tuple[int], np.dtype[np.unsignedinteger]] = np.frombuffer(
            encoded_bytes,
            dtype=a.dtype.newbyteorder("<"),
            count=len(encoded_bytes) // dtype.itemsize,
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
            Encoded 1D array with an unsigned integer dtype.
        out : None | np.ndarray[S, np.dtype[T]]
            Writeable array to store the decoded data.

        Returns
        -------
        dec : np.ndarray[S, np.dtype[T]]
            Decoded array.
        """

        b = numcodecs.compat.ensure_bytes(buf)
        b_io = BytesIO(b)

        dtype = np.dtype(b_io.read(leb128.u.decode_reader(b_io)[0]).decode("ascii"))

        shape = tuple(
            leb128.u.decode_reader(b_io)[0]
            for _ in range(leb128.u.decode_reader(b_io)[0])
        )
        size = reduce(lambda a, b: a * b, shape, 1)

        num_bitmaps, _ = leb128.u.decode_reader(b_io)

        # track which indices remain in successive bitmaps
        indices = np.arange(size)

        decoded: np.ndarray = np.zeros(size, _dtype_bits(dtype))

        for i in range(num_bitmaps):
            u: np.ndarray = np.frombuffer(
                b_io.read(dtype.itemsize),
                dtype=_dtype_bits(dtype).newbyteorder("<"),
                count=1,
            )

            packed_is_u = np.frombuffer(
                b_io.read((indices.size + 7) // 8),
                dtype=np.uint8,
                count=(indices.size + 7) // 8,
            )
            is_u = np.unpackbits(
                packed_is_u, axis=None, count=indices.size, bitorder="big"
            ).astype(np.bool)

            decoded[indices[is_u]] = u
            indices = np.extract(~is_u, indices)

        # remove padding to align with itemsize
        b_io.read(dtype.itemsize - (b_io.tell() % dtype.itemsize))

        rest: np.ndarray = np.frombuffer(
            b_io.read(indices.size * dtype.itemsize),
            dtype=_dtype_bits(dtype).newbyteorder("<"),
            count=indices.size,
        )
        decoded[indices] = rest

        decoded = decoded.view(dtype).reshape(shape)

        return numcodecs.compat.ndarray_copy(decoded, out)  # type: ignore

    def get_config(self) -> dict:
        """
        Returns the configuration of the codec.

        [`numcodecs.registry.get_codec(config)`][numcodecs.registry.get_codec]
        can be used to reconstruct this codec from the returned config.

        Returns
        -------
        config : dict
            Configuration of the codec.
        """

        return dict(
            id=type(self).codec_id,
            max_bitmaps=self._max_bitmaps,
            cost_factor=self._cost_factor,
        )


numcodecs.registry.register_codec(BitmapIndexCodec)


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
