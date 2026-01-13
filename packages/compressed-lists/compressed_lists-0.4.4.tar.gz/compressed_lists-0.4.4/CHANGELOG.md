# Changelog

## Version 0.4.0 - 0.4.4

- Classes extend `BiocObject` from biocutils. `metadata` is a named list.
- Update actions to run from 3.10-3.14
- Support empty compressed list objects of size `n`.
- Implement combine generic for compressed lists.
- element metadata slot is a `BiocFrame`.

## Version 0.3.0

- Renamed `CompressedBiocFrameList` to `CompressedSplitBiocFrameList` since the current implementation can only handle dataframes with the same number and names of columns.
- Correctly link some of the annoying typehint errors.
- `to_list` and `unlist` now perform same operation as the R implementation.
- `splitAsCompressedList` has a more abstract implementation if no generic is implemented. If it fails, returns an error.

## Version 0.2.0

- Major changes to the package; Switch to typed lists from the biocutils package.

## Version 0.1.0 - 0.1.1

- Initial implementation of various classes - Partitioning and CompressedLists.
- Udpate documentation, tutorial and tests.
