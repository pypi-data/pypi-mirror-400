"""core representation for binary sequences"""
from __future__ import annotations
from collections.abc import Sequence
from enum import StrEnum
from itertools import groupby
import math
from typing import Iterator, TYPE_CHECKING, Any, Self
__all__ = ("Direction", "BinarySequence")


if TYPE_CHECKING:
    import numpy as np

    NpNDArrayInt = np.ndarray[Any, np.dtype[np.integer]]
    NpDTypeInt = np.dtype[np.integer]


class Direction(StrEnum):
    LEFT = "left"
    RIGHT = "right"


class BinarySequence:
    def __init__(self, bits: Sequence[int | str] | str) -> None:
        self.bits: tuple[int, ...] = self._validate_bits(bits)

    @staticmethod
    def _validate_bits(
        input_bits: Sequence[int | str] | str
    ) -> tuple[int, ...]:
        """Validate input bit sequences."""
        if (input_bits is None) or (not input_bits):
            raise ValueError("Input bits cannot be None or empty.")

        try:
            bits_list: tuple[int, ...] = tuple(int(bit) for bit in input_bits)
        except (TypeError, ValueError) as e:
            raise TypeError(
                "Bits must be an iterable of 0 and 1 values."
            ) from e

        if any(bit not in (0, 1) for bit in bits_list):
            raise ValueError("Bit sequence must only contain 0 or 1.")

        return bits_list

    def _compatible_bits(self, other: object, op: str) -> tuple[int, ...]:
        """Validate that other is a BinarySequence of the same length.

        Args:
            other (object): Object to validate
            op (str): Operation name used for error messages.

        Returns:
            tuple[int, ...]: Other sequences bits as tuple of ints.
        """
        if not isinstance(other, BinarySequence):
            raise TypeError(f"{op} requires a BinarySequence.")
        if self.length != other.length:
            raise ValueError(f"{op} requires both sequences to be the same length.")
        return other.bits

    def __str__(self) -> str:
        return self.bit_string

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"length={self.length}, "
            f"preview='{str(self)}'"
            f")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinarySequence):
            return NotImplemented
        return self.bits == other.bits

    def __len__(self) -> int:
        return self.length

    def __iter__(self) -> Iterator[int]:
        return iter(self.bits)

    def __getitem__(self, key: int | slice) -> int | BinarySequence:
        if isinstance(key, slice):
            return BinarySequence(self.bits[key])
        return self.bits[key]

    def __invert__(self) -> BinarySequence:
        """Return bitwise inversion of this BinarySequence (~seq).
        Equivalent to: seq.inverted()
        """
        return self.inverted()

    def __xor__(self, other: object) -> BinarySequence:
        """Bitwise XOR with another BinarySequence (seq ^ other).
        Equivalent to: seq.xor(other).
        """
        if not isinstance(other, BinarySequence):
            return NotImplemented
        return self.xor(other)

    def __and__(self, other: object) -> BinarySequence:
        """Bitwise AND with another BinarySequence (seq & other).
        Equivalent to: seq.bitwise_and(other).
        """
        if not isinstance(other, BinarySequence):
            return NotImplemented
        return self.bitwise_and(other)

    def __or__(self, other: object) -> BinarySequence:
        """Bitwise OR with another BinarySequence (seq | other).
        Equivalent to: seq.bitwise_or(other).
        """
        if not isinstance(other, BinarySequence):
            return NotImplemented
        return self.bitwise_or(other)

    @property
    def length(self) -> int:
        """Number of bits in sequence."""
        return len(self.bits)

    @property
    def bit_string(self) -> str:
        """Bit sequence as a string of '0's and '1's. No padding."""
        bit_str: str = "".join("1" if bit else "0" for bit in self.bits)
        return bit_str

    @property
    def as_bytes(self) -> bytes:
        """Byte representation of bit sequence (left zero padded)"""
        bit_str: str = self.bit_string
        zero_padding_len: int = (-len(bit_str)) % 8
        bit_str_padded: str = ("0" * zero_padding_len) + bit_str
        byte_conversion: bytes = int(bit_str_padded, 2).to_bytes(
            len(bit_str_padded)//8, "big"
        )

        return byte_conversion

    @property
    def hex_string(self) -> str:
        """Hex string representation of byte sequence"""
        return self.as_bytes.hex()

    @property
    def signed(self) -> tuple[int, ...]:
        """Map bits (0, 1) to (-1, +1)."""
        return tuple(1 if bit else -1 for bit in self.bits)

    @property
    def ones(self) -> int:
        """Return number of 1's in Binary Sequence"""
        return sum(self.bits)

    @property
    def zeros(self) -> int:
        """Return number of 0's in Binary Sequence"""
        return self.length - self.ones

    @property
    def balance(self) -> float:
        """Return % of 1's to 0's in Binary Sequence. (0-1)"""
        return round(self.ones / self.length, 3)

    @property
    def entropy(self) -> float:
        """
        Return Shannon entropy (bits per symbol) for balance of 1's and 0's.

        Range:
            0.0 → fully deterministic (all 0s or all 1s)
            1.0 → maximally random (balanced 0/1)
        """
        if self.length == 0:
            return 0.0

        p1 = self.ones/self.length
        p0 = 1.0 - p1

        entropy = 0.0

        for p in (p1, p0):
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 5)

    @property
    def run_lengths(self):
        """Return list of run lengths [(digit, run count)].

        E.g. 111001 >> [(1, 3), (0, 2), (1, 1)]
        """
        return [(bit, sum(1 for _ in group)) for bit, group in groupby(self.bits)]

    def copy_bits(self) -> BinarySequence:
        """Return a copy of the BinarySequence."""
        return BinarySequence(self.bits)

    def to_length(self, n: int) -> BinarySequence:
        """Repeat or truncate sequence to length n.

        Args:
            n (int): Length to convert sequence to.
        """
        if n <= 0:
            raise ValueError("Target length must be positive and not zero.")
        repeats: int = (n + self.length - 1) // self.length
        bits: tuple[int, ...] = (self.bits * repeats)[:n]
        return BinarySequence(bits)

    def shift(
            self,
            n: int,
            direction: Direction = Direction.LEFT
    ) -> "BinarySequence":
        """Shift sequence (circular)

        Args:
            n (int): How many bits to shift by.
            direction (Direction, optional): 'left' or 'right'.
                Defaults to Direction.LEFT.

        Returns:
            BinarySequence: shifted BinarySequence.
        """
        if self.length == 0:
            return self

        n = n % self.length

        direction = Direction(direction)

        if n < 0:
            n = -n
            direction = (
                Direction.RIGHT if direction == Direction.LEFT
                else Direction.LEFT
            )

        match direction:
            case Direction.LEFT:
                return BinarySequence(self.bits[n:] + self.bits[:n])
            case Direction.RIGHT:
                return BinarySequence(self.bits[-n:] + self.bits[:-n])

        raise ValueError(f"{direction} not a valid direction; 'left', 'right'")

    def autocorr(self):
        raise NotImplementedError("Auto-correlation coming soon.")

    def crosscorr(self):
        raise NotImplementedError("Cross-correlation coming soon.")

    def to_numpy(self, dtype: "NpDTypeInt | None" = None) -> "NpNDArrayInt":
        """Convert BinarySequence to 1D NumPy array.

        NumPy is an optional dependency, only required when calling the to_numpy
        and from_numpy methods.

        Args:
            dtype (NpDTypeInt | None, optional): Optional NumPy integer dtype to use.
                Defaults to None (which then uses np.uint8)

        Returns:
            NpNDArrayInt: 1D NumPy array of 0 and 1 values.
        """
        try:
            import numpy as np
        except ImportError as e:
            raise ImportError("NumPy is required for to_numpy().") from e

        out_dtype = dtype or np.uint8
        if not np.issubdtype(out_dtype, np.integer):
            raise TypeError(
                "dtype must be an integer NumPy dtype (e.g., np.uint8, np.int8)."
            )
        return np.array(self.bits, dtype=out_dtype)

    @classmethod
    def from_numpy(cls, np_array: "NpNDArrayInt") -> Self:
        """Convert 1D NumPy array to BinarySequence.

        Args:
            np_array (NpNDArrayInt): 1D NumPy Array of integers.

        Returns:
            BinarySequence: Binary Sequence
        """
        # try and import numpy
        try:
            import numpy as np
        except ImportError as e:
            raise ImportError("NumPy is required for from_numpy().") from e

        # make sure input np_array is an np.ndarray
        if not isinstance(np_array, np.ndarray):
            raise TypeError("Input must be a NumPy array.")

        # correct dimensions
        if np_array.ndim != 1:
            raise ValueError("NumPy array must be 1D.")

        # integer or bool dtype
        if not np.issubdtype(np_array.dtype, np.integer) and np_array.dtype != np.bool_:
            raise TypeError("Array dtype must be integer or boolean.")

        bits = tuple(int(bit) for bit in np_array.tolist())

        return cls(bits)

    def inverted(self) -> BinarySequence:
        """Return inverted BinarySequence.

        E.g. 0 -> 1, 1 -> 0.
        """
        return BinarySequence(tuple(1 - bit for bit in self.bits))

    def xor(self, other: BinarySequence) -> BinarySequence:
        """XOR current BinarySequence with another of the same length.

        Args:
            other (BinarySequence): Binary Sequence.

        Returns:
            BinarySequence: XOR result.
        """
        other_sequence = self._compatible_bits(other, "xor")
        return BinarySequence(
            tuple(a ^ b for a, b in zip(self.bits, other_sequence))
        )

    def bitwise_and(self, other: BinarySequence) -> BinarySequence:
        """Bitwise AND with another BinarySequence of the same length.

        Args:
            other (BinarySequence): Binary Sequence.

        Returns:
            BinarySequence: AND result.
        """
        other_sequence = self._compatible_bits(other, "and")
        return BinarySequence(
            tuple(a & b for a, b in zip(self.bits, other_sequence))
        )

    def bitwise_or(self, other: BinarySequence) -> BinarySequence:
        """Bitwise OR with another BinarySequence of the same length.

        Args:
            other (BinarySequence): Binary Sequence.

        Returns:
            BinarySequence: OR result.
        """
        other_sequence = self._compatible_bits(other, "or")
        return BinarySequence(
            tuple(a | b for a, b in zip(self.bits, other_sequence))
        )

    def hamming_distance(self):
        raise NotImplementedError("Hamming distance coming soon")
