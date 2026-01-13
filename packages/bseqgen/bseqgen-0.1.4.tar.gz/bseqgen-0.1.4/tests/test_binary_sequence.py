import pytest

from bseqgen.base import BinarySequence, Direction


@pytest.fixture
def test_seq() -> BinarySequence:
    return BinarySequence((1, 1, 0))


def test_create_sequence_valid() -> None:
    test_sequence = BinarySequence([0, 1, 0])

    assert test_sequence.bits == (0, 1, 0)
    assert test_sequence.length == 3


def test_create_sequence_none() -> None:
    with pytest.raises(ValueError):
        BinarySequence(None)  # type: ignore[arg-type]


def test_create_sequence_empty() -> None:
    with pytest.raises(ValueError):
        BinarySequence([])


def test_create_sequence_string_bin() -> None:
    test_sequence = BinarySequence("1101")

    assert test_sequence.bits == (1, 1, 0, 1)
    assert test_sequence.length == 4


def test_create_sequence_other_values() -> None:
    with pytest.raises(ValueError):
        BinarySequence([3, 8])


def test_create_sequence_tuple() -> None:
    test_sequence = BinarySequence((0, 1, 1))

    assert test_sequence.bits == (0, 1, 1)
    assert test_sequence.length == 3


def test_create_sequence_strlist() -> None:
    test_sequence = BinarySequence(["1", "0"])

    assert test_sequence.bits == (1, 0)
    assert test_sequence.length == 2


def test__str__(test_seq: BinarySequence) -> None:
    assert str(test_seq) == "110"


def test_str_long_seq() -> None:
    bits = [1, 0] * 100
    seq = BinarySequence(bits)
    seq_str = str(seq)

    assert seq_str == seq.bit_string


def test_repr_contains_class_and_len(test_seq: BinarySequence) -> None:
    r = repr(test_seq)

    assert "BinarySequence" in r
    assert "length=3" in r


def test_eq_same_bits() -> None:
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 0, 1))
    assert a == b


def test_eq_diff_bits() -> None:
    a = BinarySequence((1, 0, 1))
    b = BinarySequence((1, 1, 1, 1))
    assert a != b


def test_eq_other_type(test_seq: BinarySequence) -> None:
    assert test_seq != (1, 1, 0)
    assert test_seq != "110"


def test_len_matches_length(test_seq: BinarySequence) -> None:
    assert len(test_seq) == 3
    assert len(test_seq) == test_seq.length


def test__iter__(test_seq: BinarySequence) -> None:
    assert [b for b in test_seq] == [1, 1, 0]


def test__getitem__(test_seq: BinarySequence) -> None:
    assert test_seq[1:].bits == (1, 0)  # type: ignore


def test__invert__(test_seq: BinarySequence) -> None:
    assert (~test_seq).bits == (0, 0, 1)


def test__xor__(test_seq: BinarySequence) -> None:
    other_seq = BinarySequence("111")
    assert (test_seq ^ other_seq).bits == (0, 0, 1)


def test__and__(test_seq: BinarySequence) -> None:
    other = BinarySequence("101")
    assert (test_seq & other).bits == (1 & 1, 1 & 0, 0 & 1)  # (1, 0, 0)


def test__or__(test_seq: BinarySequence) -> None:
    other = BinarySequence("101")
    assert (test_seq | other).bits == (1 | 1, 1 | 0, 0 | 1)  # (1, 1, 1)


def test__xor__type_error(test_seq: BinarySequence) -> None:
    with pytest.raises(TypeError):
        test_seq ^ 3  # type: ignore[operator]


def test__and__type_error(test_seq: BinarySequence) -> None:
    with pytest.raises(TypeError):
        test_seq & "110"  # type: ignore[operator]


def test__or__type_error(test_seq: BinarySequence) -> None:
    with pytest.raises(TypeError):
        test_seq | "110"  # type: ignore[operator]


def test__xor__length_mismatch(test_seq: BinarySequence) -> None:
    with pytest.raises(ValueError):
        test_seq ^ BinarySequence("1111")  # type: ignore[operator]


def test_bit_string_success(test_seq: BinarySequence) -> None:
    assert test_seq.bit_string == "110"


def test_as_bytes_len3(test_seq: BinarySequence) -> None:
    assert test_seq.as_bytes == b"\x06"


def test_as_bytes_len5() -> None:
    s = BinarySequence((1, 1, 1, 0, 0, 0, 1, 0, 1))
    assert s.as_bytes == b"\x01\xc5"


def test_as_bytes_exact_8_bits() -> None:
    s = BinarySequence("11110000")
    assert s.as_bytes == b"\xf0"


def test_hex_string(test_seq: BinarySequence) -> None:
    assert test_seq.hex_string == "06"


def test_signed(test_seq: BinarySequence) -> None:
    assert test_seq.signed == (1, 1, -1)


def test_ones(test_seq: BinarySequence) -> None:
    assert test_seq.ones == 2


def test_zeros(test_seq: BinarySequence) -> None:
    assert test_seq.zeros == 1


def test_balance(test_seq: BinarySequence) -> None:
    assert test_seq.balance == 0.667


def test_entropy(test_seq: BinarySequence) -> None:
    assert test_seq.entropy == 0.9183


def test_run_lengths() -> None:
    seq = BinarySequence("11110001110010101100")
    assert seq.run_lengths == [
        (1, 4),
        (0, 3),
        (1, 3),
        (0, 2),
        (1, 1),
        (0, 1),
        (1, 1),
        (0, 1),
        (1, 2),
        (0, 2),
    ]


def test_copy_bits(test_seq: BinarySequence) -> None:
    copy_bits = test_seq.copy_bits()

    assert copy_bits.bits == test_seq.bits
    assert copy_bits is not test_seq


def test_to_length_truncate() -> None:
    bits = [1] * 100
    seq = BinarySequence(bits)
    assert seq.length == 100

    assert seq.to_length(55).length == 55
    assert seq.to_length(300).length == 300
    assert seq.to_length(1).hex_string == "01"


def test_shift_left(test_seq: BinarySequence) -> None:
    assert test_seq.shift(1, "left").bits == (1, 0, 1)
    assert test_seq.shift(2).bits == (0, 1, 1)
    assert test_seq.shift(-1).bits == (0, 1, 1)
    assert test_seq.shift(1, Direction.LEFT).bits == (1, 0, 1)


def test_shift_right(test_seq: BinarySequence) -> None:
    assert test_seq.shift(1, "right").bits == (0, 1, 1)
    assert test_seq.shift(-1, "right").bits == (1, 0, 1)


def test_shift_reject_direction(test_seq: BinarySequence) -> None:
    with pytest.raises(ValueError):
        test_seq.shift(1, "bloop")  # type: ignore[arg-type]


def test_autocorr(test_seq: BinarySequence) -> None:
    pass


def test_crosscor(test_seq: BinarySequence) -> None:
    pass


def test_to_numpy_default(test_seq: BinarySequence) -> None:
    np = pytest.importorskip("numpy")
    arr = test_seq.to_numpy()
    assert arr.ndim == 1
    assert arr.tolist() == [1, 1, 0]
    assert arr.dtype == np.uint8


def test_to_numpy_dtype_int8(test_seq: BinarySequence) -> None:
    np = pytest.importorskip("numpy")
    arr = test_seq.to_numpy(dtype=np.int8)
    assert arr.dtype == np.int8


def test_to_numpy_rejects_non_integer_dtype(test_seq: BinarySequence) -> None:
    np = pytest.importorskip("numpy")
    with pytest.raises(TypeError):
        test_seq.to_numpy(dtype=np.float32)  # type: ignore[arg-type]


def test_from_numpy_int_array() -> None:
    np = pytest.importorskip("numpy")
    arr = np.array([1, 0, 1], dtype=np.uint8)
    seq = BinarySequence.from_numpy(arr)
    assert seq.bits == (1, 0, 1)


def test_from_numpy_bool_array() -> None:
    np = pytest.importorskip("numpy")
    arr = np.array([True, False, True], dtype=np.bool_)
    seq = BinarySequence.from_numpy(arr)
    assert seq.bits == (1, 0, 1)


def test_from_numpy_rejects_non_1d() -> None:
    np = pytest.importorskip("numpy")
    arr = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    with pytest.raises(ValueError):
        BinarySequence.from_numpy(arr)  # type: ignore[arg-type]


def test_from_numpy_rejects_float_dtype() -> None:
    np = pytest.importorskip("numpy")
    arr = np.array([1.0, 0.0], dtype=np.float32)
    with pytest.raises(TypeError):
        BinarySequence.from_numpy(arr)  # type: ignore[arg-type]


def test_from_numpy_rejects_non_binary_values() -> None:
    np = pytest.importorskip("numpy")
    arr = np.array([0, 2, 1], dtype=np.int8)
    with pytest.raises(ValueError):
        BinarySequence.from_numpy(arr)


def test_invert(test_seq: BinarySequence) -> None:
    assert test_seq.inverted().bits == (0, 0, 1)


def test_xor_success(test_seq: BinarySequence) -> None:
    other_seq = BinarySequence("111")
    assert test_seq.xor(other=other_seq).bits == (0, 0, 1)


def test_xor_type_error(test_seq: BinarySequence) -> None:
    with pytest.raises(TypeError):
        test_seq.xor(other="110")  # type: ignore[arg-type]


def test_bitwise_and(test_seq: BinarySequence) -> None:
    other = BinarySequence("101")
    assert test_seq.bitwise_and(other).bits == (1, 0, 0)


def test_bitwise_or(test_seq: BinarySequence) -> None:
    other = BinarySequence("101")
    assert test_seq.bitwise_or(other).bits == (1, 1, 1)


def test_hamming_distance(test_seq: BinarySequence) -> None:
    pass
