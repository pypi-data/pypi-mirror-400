import pytest

from compressed_lists import (
    Partitioning,
)

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def test_init_with_ends():
    ends = [3, 5, 10]
    names = ["A", "B", "C"]
    part = Partitioning(ends, names)

    assert list(part.get_ends()) == ends
    assert list(part.starts) == [0, 3, 5]
    assert list(part.get_names()) == names
    assert len(part) == 3


def test_init_with_invalid_names():
    ends = [3, 5, 10]
    names = ["A", "B"]

    with pytest.raises(ValueError):
        Partitioning(ends, names)


def test_from_lengths():
    lengths = [2, 3, 5]
    part = Partitioning.from_lengths(lengths)

    assert list(part.ends) == [2, 5, 10]
    assert list(part.get_starts()) == [0, 2, 5]
    assert len(part) == 3


def test_from_list():
    lst = [[1, 2], [3, 4, 5], ["a", "b", "c", "d", "e"]]
    part = Partitioning.from_list(lst)

    assert list(part.ends) == [2, 5, 10]
    assert list(part.get_element_lengths()) == [2, 3, 5]


def test_nobj():
    ends = [3, 5, 10]
    part = Partitioning(ends)

    assert part.nobj() == 10

    empty_part = Partitioning([])
    assert empty_part.nobj() == 0


def test_get_partition_range():
    ends = [3, 5, 10]
    part = Partitioning(ends)

    assert part.get_partition_range(0) == (0, 3)
    assert part.get_partition_range(1) == (3, 5)
    assert part.get_partition_range(2) == (5, 10)

    with pytest.raises(IndexError):
        part.get_partition_range(3)


def test_getitem():
    ends = [3, 5, 10]
    part = Partitioning(ends)

    assert part[0] == (0, 3)
    assert part[1] == (3, 5)

    assert part[0:2] == [(0, 3), (3, 5)]

    with pytest.raises(TypeError):
        part["invalid"]


def test_partitioning_empty():
    part = Partitioning([])
    assert len(part) == 0
    assert part.nobj() == 0
    assert list(part.get_element_lengths()) == []
    assert part.get_names() is None


def test_partitioning_from_list_non_sequence():
    # The implementation checks for __len__ or assumes 1
    lst = [1, [2, 3], "foo", (4, 5, 6)]
    part = Partitioning.from_list(lst)
    assert list(part.get_element_lengths()) == [1, 2, 3, 3]
    assert list(part.ends) == [1, 3, 6, 9]


def test_partitioning_getitem_slices():
    part = Partitioning.from_lengths([2, 3, 5, 1])

    assert part[:] == [(0, 2), (2, 5), (5, 10), (10, 11)]
    assert part[-2:] == [(5, 10), (10, 11)]
    assert part[::2] == [(0, 2), (5, 10)]


def test_partitioning_set_names_inplace():
    part = Partitioning.from_lengths([2, 3], names=["A", "B"])

    part_new = part.set_names(["X", "Y"], in_place=False)
    assert list(part.names) == ["A", "B"]
    assert list(part_new.names) == ["X", "Y"]

    part.set_names(["X", "Y"], in_place=True)
    assert list(part.names) == ["X", "Y"]

    with pytest.raises(ValueError, match="Length of names must match"):
        part.set_names(["X"], in_place=True)
