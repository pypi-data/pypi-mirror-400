from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Union
from warnings import warn

import biocutils as ut
from biocframe import BiocFrame
import numpy as np

from .partition import Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def is_pandas(x: Any) -> bool:
    """Check if ``x`` is a :py:class:`~pandas.DataFrame`.

    Args:
        x:
            Any object.

    Returns:
        True if ``x`` is a :py:class:`~pandas.DataFrame`.
    """
    if hasattr(x, "dtypes"):
        return True

    return False


def _sanitize_frame(frame, num_rows: int):
    frame = frame if frame is not None else BiocFrame({}, number_of_rows=num_rows)

    if is_pandas(frame):
        frame = BiocFrame.from_pandas(frame)

    return frame


def _validate_data_and_partitions(unlist_data, partition):
    if len(unlist_data) != partition.nobj():
        raise ValueError(
            f"Length of 'unlist_data' ({len(unlist_data)}) "
            f"doesn't match 'partitioning' total length ({partition.nobj()})."
        )


class CompressedList(ut.BiocObject):
    """Base class for compressed list objects.

    `CompressedList` stores list elements concatenated in a single vector-like object
    with partitioning information that defines where each list element starts and ends.
    """

    def __init__(
        self,
        unlist_data: Any,
        partitioning: Partitioning,
        element_type: Any = None,
        element_metadata: Optional[BiocFrame] = None,
        metadata: Optional[Union[Dict[str, Any], ut.NamedList]] = None,
        _validate: bool = True,
    ):
        """Initialize a CompressedList.

        Args:
            unlist_data:
                Vector-like object containing concatenated elements.

            partitioning:
                Partitioning object defining element boundaries (exclusive).

            element_type:
                class for the type of elements.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            _validate:
                Internal use only.
        """

        super().__init__(metadata=metadata, _validate=_validate)

        self._unlist_data = unlist_data
        self._partitioning = partitioning
        self._element_type = element_type
        self._element_metadata = _sanitize_frame(element_metadata, len(partitioning))

        if _validate:
            _validate_data_and_partitions(self._unlist_data, self._partitioning)

    #########################
    ######>> Copying <<######
    #########################

    def __deepcopy__(self, memo=None, _nil=[]):
        """
        Returns:
            A deep copy of the current ``Partitioning``.
        """
        from copy import deepcopy

        _unlistdata_copy = deepcopy(self._unlist_data)
        _part_copy = deepcopy(self._partitioning)
        _elem_type_copy = deepcopy(self._element_type)
        _elem_metadata_copy = deepcopy(self._element_metadata)
        _metadata_copy = deepcopy(self._metadata)

        current_class_const = type(self)
        return current_class_const(
            unlist_data=_unlistdata_copy,
            partitioning=_part_copy,
            element_type=_elem_type_copy,
            element_metadata=_elem_metadata_copy,
            metadata=_metadata_copy,
            _validate=False,
        )

    def __copy__(self):
        """
        Returns:
            A shallow copy of the current ``Partitioning``.
        """
        current_class_const = type(self)
        return current_class_const(
            unlist_data=self._unlist_data,
            partitioning=self._partitioning,
            element_type=self._element_type,
            element_metadata=self._element_metadata,
            metadata=self._metadata,
            _validate=False,
        )

    def copy(self):
        """Alias for :py:meth:`~__copy__`."""
        return self.__copy__()

    ######################################
    ######>> length and iterators <<######
    ######################################

    def __len__(self) -> int:
        """Return the number of list elements."""
        return len(self._partitioning)

    def get_element_lengths(self) -> np.ndarray:
        """Get the lengths of each list element."""
        return self._partitioning.get_element_lengths()

    def __iter__(self) -> Iterator[Any]:
        """Iterate over list elements."""
        for i in range(len(self)):
            yield self[i]

    ##########################
    ######>> Printing <<######
    ##########################

    def __repr__(self) -> str:
        """
        Returns:
            A string representation.
        """
        output = f"{type(self).__name__}(number_of_elements={len(self)}"
        output += ", unlist_data=" + ut.print_truncated_list(self._unlist_data)
        output += ", partitioning=" + self._partitioning.__repr__()

        _etype_name = "__unknown_class__"
        if isinstance(self._element_type, str):
            _etype_name = self._element_type
        elif hasattr(self._element_type, "__name__"):
            _etype_name = self._element_type.__name__
        output += ", element_type=" + _etype_name

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

        _etype_name = "__unknown_class__"
        if isinstance(self._element_type, str):
            _etype_name = self._element_type
        elif hasattr(self._element_type, "__name__"):
            _etype_name = self._element_type.__name__

        output += f"number of elements: ({len(self)}) of type: {_etype_name}\n"

        output += f"unlist_data: {ut.print_truncated_list(self._unlist_data)}\n"

        output += f"partitioning: {ut.print_truncated_list(self._partitioning)}\n"

        output += f"element_metadata({str(len(self._element_metadata))} rows): {ut.print_truncated_list(list(self._element_metadata.get_column_names()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"
        output += f"metadata({str(len(self._metadata))}): {ut.print_truncated_list(list(self._metadata.keys()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"

        return output

    #############################
    ######>> element_type <<#####
    #############################

    def get_element_type(self) -> str:
        """Return the element_type."""
        return self._element_type

    @property
    def element_type(self) -> str:
        """Alias for :py:attr:`~get_element_type`, provided for back-compatibility."""
        return self.get_element_type()

    ###########################
    ######>> partitions <<#####
    ###########################

    def get_partitioning(self) -> Partitioning:
        """Return the paritioning info."""
        return self._partitioning

    @property
    def paritioning(self) -> Partitioning:
        """Alias for :py:attr:`~get_paritioning`, provided for back-compatibility."""
        return self.get_partitioning()

    #######################
    ######>> names <<######
    #######################

    def get_names(self) -> Optional[ut.Names]:
        """Get the names of list elements."""
        return self._partitioning.get_names()

    def set_names(self, names: Sequence[str], in_place: bool = False) -> CompressedList:
        """Set the names of list elements.

        names:
            New names, same as the number of rows.

            May be `None` to remove names.

        in_place:
            Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        output._partitioning = self._partitioning.set_names(names, in_place=False)
        return output

    @property
    def names(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_names`."""
        return self._partitioning.get_names()

    @names.setter
    def names(self, names: Sequence[str]):
        """Alias for :py:attr:`~set_names` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'names' is an in-place operation, use 'set_names' instead",
            UserWarning,
        )
        self.set_names(names=names, in_place=True)

    #############################
    ######>> unlist_data <<######
    #############################

    def get_unlist_data(self) -> Any:
        """Get all elements."""
        return self._unlist_data

    def set_unlist_data(self, unlist_data: Any, in_place: bool = False) -> CompressedList:
        """Set new list elements.

        Args:
            unlist_data:
                New vector-like object containing concatenated elements.

            in_place:
                Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)

        _validate_data_and_partitions(unlist_data=unlist_data, partition=self._partitioning)

        output._unlist_data = unlist_data
        return output

    @property
    def unlist_data(self) -> Any:
        """Alias for :py:attr:`~get_unlist_data`."""
        return self.get_unlist_data()

    @unlist_data.setter
    def unlist_data(self, unlist_data: Any):
        """Alias for :py:attr:`~set_unlist_data` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'unlist_data' is an in-place operation, use 'set_unlist_data' instead",
            UserWarning,
        )
        self.set_unlist_data(unlist_data, in_place=True)

    ###################################
    ######>> element metadata <<#######
    ###################################

    def get_element_metadata(self) -> BiocFrame:
        """
        Returns:
            Dictionary of metadata for each element in this object.
        """
        return self._element_metadata

    def set_element_metadata(self, element_metadata: BiocFrame, in_place: bool = False) -> CompressedList:
        """Set new element metadata.

        Args:
            element_metadata:
                New element metadata for this object.

            in_place:
                Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if not isinstance(element_metadata, BiocFrame):
            raise TypeError(f"`element_metadata` must be a BiocFrame, provided {type(element_metadata)}.")

        output = self._define_output(in_place)
        output._element_metadata = _sanitize_frame(element_metadata, len(self._partitioning))
        return output

    @property
    def element_metadata(self) -> BiocFrame:
        """Alias for :py:attr:`~get_element_metadata`."""
        return self.get_element_metadata()

    @element_metadata.setter
    def element_metadata(self, element_metadata: BiocFrame):
        """Alias for :py:attr:`~set_element_metadata` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'element_metadata' is an in-place operation, use 'set_element_metadata' instead",
            UserWarning,
        )
        self.set_element_metadata(element_metadata, in_place=True)

    ##########################
    ######>> accessors <<#####
    ##########################

    def __getitem__(self, key: Union[int, str, slice]) -> Any:
        """Get an element or slice of elements from the list.

        Args:
            key:
                Integer index, string name, or slice.

        Returns:
            List element(s).
        """
        # string keys (names)
        if isinstance(key, str):
            if key not in list(self.get_names()):
                raise KeyError(f"No element named '{key}'.")
            key = list(self.names).index(key)

        # integer indices
        if isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError(f"List index '{key}' out of range.")

            start, end = self._partitioning.get_partition_range(key)
            return self.extract_range(start, end)

        # slices
        elif isinstance(key, (range, slice)):
            if isinstance(key, range):
                key = slice(key.start, key.stop, key.step)

            indices = range(*key.indices(len(self)))
            result = []
            for i in indices:
                start, end = self._partitioning.get_partition_range(i)
                result.append(self.extract_range(start, end))

            current_class_const = type(self)
            return current_class_const.from_list(
                result, names=[self.names[i] for i in indices] if self.names is not None else None
            )

        else:
            try:
                return self.extract_subset(indices=key)
            except Exception as e:
                raise TypeError("'key' must be int, str, slice or list of indices.") from e

    ##################################
    ######>> abstract methods <<######
    ##################################

    def extract_range(self, start: int, end: int) -> Any:
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
            return self._unlist_data[start:end]
        except Exception as e:
            raise NotImplementedError(
                "Custom classes should implement their own `extract_range` method for slice operations"
            ) from e

    @classmethod
    def from_list(
        cls,
        lst: Any,
        names: Optional[Union[ut.Names, Sequence[str]]] = None,
        metadata: Optional[Union[Dict[str, Any], ut.NamedList]] = None,
    ) -> CompressedList:
        """Create a CompressedList from a regular list.

        This method must be implemented by subclasses to handle
        type-specific conversion from list to unlist_data.

        Args:
            lst:
                List to convert.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedList`.
        """
        # Flatten the list
        flat_data = []
        for sublist in lst:
            flat_data.extend(sublist)

        # Create partitioning
        partitioning = Partitioning.from_list(lst, names)

        # Create unlist_data
        # unlist_data = cls._element_type(data=flat_data)

        return cls(flat_data, partitioning, metadata=metadata)

    ###########################
    ######>> coercions <<######
    ###########################

    def to_list(self) -> List[List[Any]]:
        """Convert to a regular Python list.

        Returns:
            A regular Python list with all elements.
        """
        result = []
        for i in range(len(self)):
            _subset = list(self[i])
            if len(_subset) == 0:
                _subset = [None]
            result.append(_subset)

        return result

    def as_list(self) -> List[List[Any]]:
        """Alias to :py:meth:`~to_list`"""
        return self.to_list()

    def unlist(self, use_names: bool = False) -> Any:
        """Get the underlying unlisted data.

        Args:
            use_names:
                Whether to include names in the result if applicable.

        Returns:
            The unlisted data.
        """
        return (
            self._unlist_data
            if use_names is False
            else self._unlist_data.set_names(self.get_partitioning().get_names(), in_place=False)
        )

    def relist(self, unlist_data: Any) -> CompressedList:
        """Create a new `CompressedList` with the same partitioning but different data.

        Args:
            unlist_data:
                New unlisted data.

        Returns:
            A new CompressedList.
        """
        _validate_data_and_partitions(unlist_data, self._partitioning)

        current_class_const = type(self)
        return current_class_const(
            unlist_data,
            self._partitioning.copy(),
            element_type=self._element_type,
            element_metadata=self._element_metadata.copy(),
            metadata=self._metadata.copy(),
        )

    def extract_subset(self, indices: Sequence[int]) -> CompressedList:
        """Extract a subset of elements by indices.

        Args:
            indices:
                Sequence of indices to extract.

        Returns:
            A new CompressedList with only the selected elements.
        """
        print("here", indices, type(indices))
        if isinstance(indices, np.ndarray):
            indices = indices.tolist()

        # Validate indices
        for i in indices:
            if i < 0 or i >= len(self):
                raise IndexError(f"Index {i} out of range")

        # Extract element lengths and names
        new_lengths = ut.subset_sequence(self.get_element_lengths(), indices)
        new_names = ut.subset_sequence(self.names, indices) if self.names is not None else None

        # Create new partitioning
        new_partitioning = Partitioning.from_lengths(new_lengths, new_names)

        # Extract data
        _new_data = []
        for i in indices:
            start, end = self._partitioning.get_partition_range(i)
            _subset = ut.subset_sequence(self._unlist_data, [j for j in range(start, end)])
            _new_data.append(_subset)
        #     if isinstance(self._unlist_data, np.ndarray):
        #         new_data.append(self._unlist_data[start:end])
        #     else:
        #         new_data.extend(self._unlist_data[start:end])

        # if isinstance(self._unlist_data, np.ndarray):
        #     new_data = np.concatenate(new_data)

        if len(_new_data) == 1:
            new_data = _new_data[0]
        elif len(_new_data) > 0:
            new_data = ut.combine_sequences(*_new_data)
        else:
            new_data = []

        current_class_const = type(self)
        return current_class_const(
            new_data,
            new_partitioning,
            element_type=self._element_type,
            element_metadata=self._element_metadata[indices,],
            metadata=self._metadata.copy(),
        )

    def lapply(self, func: Callable) -> CompressedList:
        """Apply a function to each element.

        Args:
            func:
                Function to apply to each element.

        Returns:
            A new CompressedList with the results.
        """
        result = [func(elem) for elem in self]

        current_class_const = type(self)
        return current_class_const.from_list(result, self.names, self._metadata)

    @classmethod
    def empty(cls, n: int):
        """Create an zero-length `CompressedGenomicRangesList` object.

        Args:
            n:
                Number of elements.

        Returns:
            same type as caller, in this case a `CompressedGenomicRangesList`.
        """

        _range_lengths = [0] * n

        return CompressedList(unlist_data=[], partitioning=Partitioning(ends=_range_lengths))

    #######################
    ######>> extend <<#####
    #######################

    def extend(self, other: CompressedList, in_place: bool = False) -> CompressedList:
        """
        Args:
            other:
                Some CompressedList object.

            in_place:
                Whether to perform the modification in place.

        Returns:
            A ``CompressedList`` where items in ``other`` are added to the end. If
            ``in_place = False``, this is a new object, otherwise a reference
            to the current object is returned.
        """
        output = self._define_output(in_place)

        output._unlist_data = ut.combine_sequences(output._unlist_data, other._unlist_data)
        output._partitioning = ut.combine_sequences(output._partitioning, other._partitioning)

        return output


@ut.combine_sequences.register(CompressedList)
def _register_combine_patitioning(*x: CompressedList) -> CompressedList:
    if not x:
        raise ValueError("Cannot combine an empty object")

    output = x[0].copy()
    for i in range(1, len(x)):
        output.extend(x[i], in_place=True)

    return output
