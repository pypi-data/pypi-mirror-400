# Change Log

## [0.1.3] - 03/01/2026

- Changed `pyproject.toml` to use python `>= 3.11` instead of `3.14`.

## [0.1.2] - 03/01/2026

- `run_lengths` implemented to count run lengths in BinarySequence.
- `inverted`; changed name of method from `invert` to `inverted` and implemented.
- `xor` implemented.
- Dunder methods for `xor`, `and`, `or` added to enable operators (e.g. ~seq, seq & otherseq) etc. Including adding implementations for `and`, `or` bitwise operations.
- First implementations of `to_numpy()` and `from_numpy()`, which only import `numpy` if using those particular methods.
- Very basic tests added for above methods/properties.

## [0.1.1] - 23/12/2025

### Fixed

- Tests for random_sequence.
- Documentation updates.
- Versioning noob errors!

## [0.1.0b1] - 23/12/2025

### Added

- Core `BinarySequence` class
- Input validation for binary sequences
- Circular shift operations
- Bit counts, balance, Shannon entropy
- Byte/Hex/String representations
- Len, iteration, slicing, eq etc.
- Tests for BinarySequence.
- `random_sequence` using `Random` to generate a binary sequence.
