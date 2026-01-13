import biocutils as ut
import pytest
from biocframe import BiocFrame

from compressed_lists import CompressedSplitBiocFrameList, CompressedStringList, Partitioning, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def frame_data():
    return BiocFrame(
        {
            "ensembl": ["ENS00001", "ENS00002", "ENS00003"],
            "symbol": ["MAP1A", "BIN1", "ESR1"],
        }
    )


def test_creation(frame_data):
    frame_list = CompressedSplitBiocFrameList(frame_data, partitioning=Partitioning.from_lengths([1, 2]))

    assert isinstance(frame_list, CompressedSplitBiocFrameList)
    assert len(frame_list) == 2
    assert isinstance(frame_list.unlist_data, BiocFrame)
    assert len(frame_list.get_unlist_data()) == 3
    assert list(frame_list.get_element_lengths()) == [1, 2]
    assert frame_list[0].get_column("symbol") == ["MAP1A"]


def test_bframe_typed_list_column():
    bframe = BiocFrame(
        {
            "ensembl": ut.StringList(["ENS00001", "ENS00002", "ENS00003"]),
            "symbol": ["MAP1A", "BIN1", "ESR1"],
        }
    )
    frame_list = CompressedSplitBiocFrameList(bframe, partitioning=Partitioning.from_lengths([1, 2]))

    ens_col = frame_list["ensembl"]
    assert isinstance(ens_col, CompressedStringList)
    assert len(ens_col) == 2


def test_split_biocframe(frame_data):
    frame_data.set_column("groups", [0, 0, 1], in_place=True)
    clist = splitAsCompressedList(frame_data, groups_or_partitions=frame_data.get_column("groups"))

    assert isinstance(clist, CompressedSplitBiocFrameList)

    val = clist.__repr__()
    assert isinstance(val, str)

    val = clist.__str__()
    assert isinstance(val, str)
