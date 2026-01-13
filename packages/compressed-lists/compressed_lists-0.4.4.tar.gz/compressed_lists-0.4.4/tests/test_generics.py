import biocutils as ut
import numpy as np
import pytest

from compressed_lists import (
    CompressedFloatList,
    CompressedIntegerList,
    CompressedNumpyList,
    Partitioning,
    splitAsCompressedList,
)
from compressed_lists.split_generic import _generic_register_helper, groups_to_partition

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def test_groups():
    float_vec = ut.FloatList([1.1, 1.2, 2.1, 2.2, 2.3, 3.0])
    groups = [1, 2, 3, 1, 2, 3]

    clist = splitAsCompressedList(float_vec, groups_or_partitions=groups)

    assert isinstance(clist, CompressedFloatList)


def test_partitions():
    int_list = splitAsCompressedList(
        ut.IntegerList([1, 2, 3, 4, 5, 6, 7, 8, 9]), groups_or_partitions=Partitioning(ends=[3, 5, 9])
    )

    assert isinstance(int_list, CompressedIntegerList)


def test_groups_to_partition_value_error():
    with pytest.raises(ValueError, match="must match length of groups"):
        groups_to_partition([1, 2, 3], [1, 2], None)


def test_groups_to_partition_empty():
    data = []
    groups = []
    part_data, part = groups_to_partition(data, groups)
    assert part_data == []
    assert len(part) == 0


def test_splitAsCompressedList_unsupported_type():
    class UnregisteredType:
        def __init__(self):
            self.data = [1, 2]

        def __len__(self):
            return len(self.data)

        def __getitem__(self, i):
            return self.data[i]

    data = UnregisteredType()
    with pytest.raises(NotImplementedError, match="No `splitAsCompressedList` dispatcher found"):
        splitAsCompressedList(data, groups_or_partitions=[0, 0])


def test_splitAsCompressedList_empty():
    data_int = ut.IntegerList([])
    groups_int = []
    clist_int = splitAsCompressedList(data_int, groups_int)
    assert isinstance(clist_int, CompressedIntegerList)
    assert len(clist_int) == 0
    assert len(clist_int.unlist_data) == 0

    data_np = np.array([])
    groups_np = []
    clist_np = splitAsCompressedList(data_np, groups_np)
    assert isinstance(clist_np, CompressedNumpyList)
    assert len(clist_np) == 0
    assert len(clist_np.unlist_data) == 0


def test_generic_register_helper_errors():
    with pytest.raises(ValueError, match="'groups_or_paritions' cannot be 'None'"):
        _generic_register_helper([1, 2, 3], None)

    with pytest.raises(ValueError, match="'groups_or_paritions' must be a group vector or a Partition object"):
        _generic_register_helper([1, 2, 3], {"a": 1})


def test_paritioning_combine():
    p1 = Partitioning(ends=[3, 5, 9], names=["1", "2", "3"])
    p2 = Partitioning(ends=[3, 5, 9])

    combi = ut.combine_sequences(p1, p2)

    assert isinstance(combi, Partitioning)
    assert len(combi) == 6
    assert np.allclose(combi.get_ends(), [3, 5, 9, 12, 14, 18])
    assert list(combi.get_names()) == ["1", "2", "3", "", "", ""]


def test_compressed_list_combine():
    f1 = CompressedFloatList.from_list([[1.1, 1.2], [2.1, 2.2, 2.3], [3]], ["fruits1", "fruits2", "fruits3"])
    f2 = CompressedFloatList.from_list([[1.1, 1.2], [2.1, 2.2, 2.3], [3]])

    combi = ut.combine_sequences(f1, f2)

    assert isinstance(combi, CompressedFloatList)
    assert len(combi) == 6
    assert np.allclose(combi.get_partitioning().get_ends(), [2, 5, 6, 8, 11, 12])
    assert list(combi.get_names()) == ["fruits1", "fruits2", "fruits3", "", "", ""]
