from bseqgen import random_sequence
from bseqgen.base import BinarySequence
import pytest


@pytest.fixture
def test_seq() -> BinarySequence:
    return random_sequence(n=10)


def test_random_sequence_returns_binarysequence(test_seq) -> None:
    assert isinstance(test_seq, BinarySequence)


def test_random_sequence_length(test_seq) -> None:
    assert test_seq.length == 10


def test_random_sequence_bits_binary(test_seq) -> None:
    assert all(bit in (0, 1) for bit in test_seq)


def test_random_sequence_reproducible_seed() -> None:
    seq1 = random_sequence(20, seed=42)
    seq2 = random_sequence(20, seed=42)

    assert seq1.bits == seq2.bits


def test_random_sequence_diff_seeds() -> None:
    seq1 = random_sequence(20, seed=4)
    seq2 = random_sequence(20, seed=2)

    assert seq1.bits != seq2.bits


def test_random_sequence_balance() -> None:
    seq = random_sequence(1000)
    assert 0.4 < seq.balance < 0.6


def test_random_sequence_invalid_length() -> None:
    with pytest.raises(ValueError):
        random_sequence(-1)

    with pytest.raises(ValueError):
        random_sequence(0)
