from copy import copy, deepcopy

import biocutils as ut
import pytest

from compressed_lists import CompressedList
from biocframe import BiocFrame

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def base_list_data():
    return [[1, 2], [3], [4, 5, 6]]


@pytest.fixture
def base_list(base_list_data):
    names = ["A", "B", "C"]
    return CompressedList.from_list(base_list_data, names)


def test_base_empty_creation():
    cl_empty = CompressedList.from_list([])
    assert len(cl_empty) == 0
    assert len(cl_empty.unlist_data) == 0
    assert list(cl_empty.get_element_lengths()) == []
    assert cl_empty.to_list() == []


def test_base_list_of_empty():
    cl_list_empty = CompressedList.from_list([[], [], []])
    assert len(cl_list_empty) == 3
    assert len(cl_list_empty.unlist_data) == 0
    assert list(cl_list_empty.get_element_lengths()) == [0, 0, 0]
    assert list(cl_list_empty[0]) == []
    assert list(cl_list_empty[1]) == []
    assert list(cl_list_empty[2]) == []


def test_base_list_empty_classmeth():
    cl_list_empty = CompressedList.empty(n=3)
    assert len(cl_list_empty) == 3
    assert len(cl_list_empty.unlist_data) == 0
    assert list(cl_list_empty.get_element_lengths()) == [0, 0, 0]
    assert list(cl_list_empty[0]) == []
    assert list(cl_list_empty[1]) == []
    assert list(cl_list_empty[2]) == []

    subset = cl_list_empty[[0, 2]]
    assert isinstance(subset, CompressedList)
    assert len(subset) == 2


def test_base_set_names(base_list):
    new_names = ["X", "Y", "Z"]

    cl_new_names = base_list.set_names(new_names, in_place=False)
    assert list(base_list.names) == ["A", "B", "C"]  # Original is unchanged
    assert list(cl_new_names.names) == new_names

    with pytest.warns(UserWarning, match="Setting property 'names'"):
        base_list.names = new_names
    assert list(base_list.names) == new_names


def test_base_set_unlist_data(base_list):
    new_data = [10, 20, 30, 40, 50, 60]
    assert len(new_data) == len(base_list.unlist_data)

    cl_new_data = base_list.set_unlist_data(new_data, in_place=False)
    assert base_list.unlist_data == [1, 2, 3, 4, 5, 6]  # Original is unchanged
    assert cl_new_data.unlist_data == new_data
    assert list(cl_new_data[0]) == [10, 20]

    with pytest.warns(UserWarning, match="Setting property 'unlist_data'"):
        base_list.unlist_data = new_data
    assert base_list.unlist_data == new_data
    assert list(base_list[1]) == [30]


def test_base_set_unlist_data_error(base_list):
    with pytest.raises(ValueError, match="Length of 'unlist_data'"):
        base_list.set_unlist_data([1, 2, 3], in_place=False)


def test_base_metadata(base_list):
    meta = {"source": "test"}
    cl_meta = base_list.set_metadata(meta, in_place=False)
    assert base_list.metadata == ut.NamedList()
    assert cl_meta.metadata == ut.NamedList.from_dict({"source": "test"})

    with pytest.warns(UserWarning, match="Setting property 'metadata'"):
        base_list.metadata = meta
    assert base_list.metadata == ut.NamedList.from_dict({"source": "test"})

    el_meta = BiocFrame({"score": [1, 2, 3]})
    cl_el_meta = base_list.set_element_metadata(el_meta, in_place=False)
    assert len(base_list.element_metadata) == 3
    assert cl_el_meta.element_metadata.get_column("score") == el_meta.get_column("score")

    with pytest.raises(Exception):
        base_list.element_metadata = {"info": "details"}


def test_base_copying(base_list):
    cl_copy = copy(base_list)
    assert cl_copy is not base_list
    assert cl_copy.unlist_data is base_list.unlist_data
    assert cl_copy.get_partitioning() is base_list.get_partitioning()

    cl_deepcopy = deepcopy(base_list)
    assert cl_deepcopy is not base_list
    assert cl_deepcopy.unlist_data is not base_list.unlist_data
    assert cl_deepcopy.unlist_data == base_list.unlist_data
    assert cl_deepcopy.get_partitioning() is not base_list.get_partitioning()
    assert list(cl_deepcopy.get_partitioning().get_ends()) == list(base_list.get_partitioning().get_ends())


def test_base_repr_str(base_list):
    assert isinstance(repr(base_list), str)
    assert "CompressedList" in repr(base_list)
    assert "number_of_elements=3" in repr(base_list)

    assert isinstance(str(base_list), str)
    assert "class: CompressedList" in str(base_list)
    assert "number of elements: (3)" in str(base_list)


def test_base_extract_subset_edge_cases(base_list, base_list_data):
    sub_empty = base_list.extract_subset([])
    assert len(sub_empty) == 0
    assert len(sub_empty.unlist_data) == 0

    sub_dup = base_list.extract_subset([0, 1, 0])
    assert len(sub_dup) == 3
    assert list(sub_dup.names) == ["A", "B", "A"]
    assert sub_dup.to_list() == [base_list_data[0], base_list_data[1], base_list_data[0]]
    assert sub_dup.unlist_data == [1, 2, 3, 1, 2]

    sub_order = base_list.extract_subset([2, 0])
    assert len(sub_order) == 2
    assert list(sub_order.names) == ["C", "A"]
    assert sub_order.to_list() == [base_list_data[2], base_list_data[0]]
    assert sub_order.unlist_data == [4, 5, 6, 1, 2]
