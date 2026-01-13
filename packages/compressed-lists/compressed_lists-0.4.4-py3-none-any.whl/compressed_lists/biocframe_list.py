from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import biocutils as ut
from biocframe import BiocFrame

from .base import CompressedList
from .partition import Partitioning
from .split_generic import _generic_register_helper, splitAsCompressedList

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedSplitBiocFrameList(CompressedList):
    """CompressedList for BiocFrames.

    All BiocFrames are expected to have the same number and names of columns."""

    def __init__(
        self,
        unlist_data: BiocFrame,
        partitioning: Partitioning,
        element_metadata: Optional[dict] = None,
        metadata: Optional[Union[Dict[str, Any], ut.NamedList]] = None,
        **kwargs,
    ):
        """Initialize a CompressedSplitBiocFrameList.

        Args:
            unlist_data:
                BiocFrame object.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """
        if not isinstance(unlist_data, BiocFrame):
            raise TypeError("'unlist_data' is not a `BiocFrame` object.")

        super().__init__(
            unlist_data, partitioning, element_type="BiocFrame", element_metadata=element_metadata, metadata=metadata
        )

    @classmethod
    def from_list(
        cls,
        lst: List[BiocFrame],
        names: Optional[Union[ut.Names, Sequence[str]]] = None,
        metadata: Optional[dict] = None,
    ) -> CompressedSplitBiocFrameList:
        """Create a `CompressedSplitBiocFrameList` from a regular list.

        This concatenates the list of `BiocFrame` objects.

        Args:
            lst:
                List of `BiocFrame` objects.

                Must have the same number and names of columns.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedList`.
        """
        unlist_data = ut.relaxed_combine_rows(*lst)
        partitioning = Partitioning.from_list(lst, names)
        return cls(unlist_data, partitioning, metadata=metadata)

    def __getitem__(self, key: Union[int, str, slice]):
        """Override to handle column extraction using `splitAsCompressedList`."""
        if isinstance(key, str):
            column_data = self._unlist_data.get_column(key)
            return splitAsCompressedList(
                column_data, groups_or_partitions=self._partitioning, names=self.names, metadata=self.metadata
            )
        else:
            return super().__getitem__(key)

    def extract_range(self, start: int, end: int) -> BiocFrame:
        """Extract a range from `unlist_data`.

        This method must be implemented by subclasses to handle
        type-specific extraction from `unlist_data`.

        Args:
            start:
                Start index (inclusive).

            end:
                End index (exclusive).

        Returns:
            Extracted element.
        """
        try:
            return self._unlist_data[start:end, :]
        except Exception as e:
            raise NotImplementedError(
                "Custom classes should implement their own `extract_range` method for slice operations"
            ) from e

    ##########################
    ######>> Printing <<######
    ##########################

    def __repr__(self) -> str:
        """
        Returns:
            A string representation.
        """
        output = f"{type(self).__name__}(number_of_elements={len(self)}"
        output += ", unlist_data=" + self._unlist_data.__repr__()
        output += ", partitioning=" + self._partitioning.__repr__()
        output += (
            ", element_type=" + self._element_type.__name__
            if not isinstance(self._element_type, str)
            else self._element_type
        )

        output += ", element_metadata=" + self._element_metadata.__repr__()

        if len(self._metadata) > 0:
            output += ", metadata=" + ut.print_truncated_dict(self._metadata)

        output += ")"
        return output

    def __str__(self) -> str:
        """
        Returns:
            A pretty-printed string containing the contents of this object.
        """
        output = f"class: {type(self).__name__}\n"

        output += f"number of elements: ({len(self)}) of type: {self._element_type.__name__ if not isinstance(self._element_type, str) else self._element_type}\n"

        output += f"unlist_data: {ut.print_truncated_list(self._unlist_data.get_column_names())}\n"

        output += f"partitioning: {ut.print_truncated_list(self._partitioning)}\n"

        output += f"element_metadata({str(len(self._element_metadata))} rows): {ut.print_truncated_list(list(self._element_metadata.get_column_names()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"
        output += f"metadata({str(len(self._metadata))}): {ut.print_truncated_list(list(self._metadata.keys()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"

        return output


@splitAsCompressedList.register
def _(
    data: BiocFrame,
    groups_or_partitions: Union[list, Partitioning],
    names: Optional[Union[ut.Names, Sequence[str]]] = None,
    metadata: Optional[dict] = None,
) -> CompressedSplitBiocFrameList:
    """Handle lists of BiocFrame objects."""

    partitioned_data, groups_or_partitions = _generic_register_helper(
        data=data, groups_or_partitions=groups_or_partitions, names=names
    )

    if not isinstance(partitioned_data, BiocFrame) and len(partitioned_data) != 0:
        partitioned_data = ut.relaxed_combine_rows(*partitioned_data)

    return CompressedSplitBiocFrameList(
        unlist_data=partitioned_data, partitioning=groups_or_partitions, metadata=metadata
    )
