import biocutils as ut
import pytest

from compressed_lists import (
    CompressedBooleanList,
    CompressedFloatList,
    CompressedIntegerList,
    CompressedStringList,
    Partitioning,
)

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.mark.parametrize(
    "Cls, data, unlist_type",
    [
        (CompressedIntegerList, [1, 2, 3], ut.IntegerList),
        (CompressedFloatList, [1.1, 2.2], ut.FloatList),
        (CompressedBooleanList, [True, False, True], ut.BooleanList),
        (CompressedStringList, ["a", "b", "c"], ut.StringList),
    ],
)
def test_coercion_warning(Cls, data, unlist_type):
    part = Partitioning.from_lengths([len(data)])
    with pytest.warns(UserWarning, match="trying to coerce"):
        clist = Cls(data, part)

    assert isinstance(clist.unlist_data, unlist_type)
    assert list(clist.unlist_data) == data
