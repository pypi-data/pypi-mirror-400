"""Dataset-related transformations.

This module contains the base class and concrete classes for dataset transformations,
those that potentially act over the entire dataset.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Union

import attr

from bitfount.transformations.base_transformation import Transformation
from bitfount.transformations.exceptions import TransformationApplicationError
from bitfount.utils import delegates


@delegates()
@attr.dataclass(kw_only=True)
class DatasetTransformation(Transformation):
    """Base transformation for all dataset transformation classes.

    User can specify "all" to have it act on every relevant column as defined
    in the schema.

    Args:
        output: Whether or not this transformation should be included in the final
            output. This must be True for all dataset transformations. Defaults to True.
        cols: The columns to act on as a list of strings. Defaults to "all" which acts
            on all columns in the dataset.

    Raises:
        ValueError: If `output` is False.
    """

    output: bool = True
    cols: Union[str, list[str]] = "all"

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not self.output:
            raise ValueError("`output` cannot be False for a DatasetTransformation")


@delegates()
@attr.dataclass(kw_only=True)
class CleanDataTransformation(DatasetTransformation):
    """Dataset transformation that will "clean" the specified columns.

    For continuous columns this will replace all infinities and NaNs with 0.
    For categorical columns this will replace all NaN's with "nan" explicitly.
    """

    _registry_name = "cleandata"


@delegates()
@attr.dataclass(kw_only=True)
class NormalizeDataTransformation(DatasetTransformation):
    """Dataset transformation that will normalise the specified continuous columns.

    Args:
        cols: The columns to act on as a list of strings. By default, this
            transformation will only apply to columns of type float.

    If this transformation should be applied to all continuous columns,
    the cols attribute should be set to 'all'.
    """

    cols: Union[str, list[str]] = "float"
    _registry_name = "normalizedata"


@delegates()
@attr.dataclass(kw_only=True)
class ScalarMultiplicationDataTransformation(DatasetTransformation):
    """Dataset transformation that multiplies the specified columns by a scalar.

    Transformation applied to the dataset in place. Only applies to continuous columns.

    Args:
        scalar: the scalar to be used for multiplication. It can be provided
            as a number, in which case all numerical columns will be multiplied
            by the respective scalar or as a dictionary mapping column names
            to scalars for multiplication. Defaults to 1.

    Raises:
        TransformationApplicationError: if the scalar variable is not correctly
                instantiated.
    """

    scalar: Union[int, float, Mapping[str, Union[int, float]]] = 1
    _registry_name = "scalarmultiply"

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not isinstance(self.scalar, (int, float, dict)):
            raise TransformationApplicationError(
                f"The scalar definition ({self.scalar}) for this transformation is"
                " incorrect. Please make sure you pass an integer, a float, or a"
                " dictionary with column names mapped to the value of the scalar"
                " that the respective column should be mapped to."
            )


@delegates()
@attr.dataclass(kw_only=True)
class ScalarAdditionDataTransformation(DatasetTransformation):
    """Dataset transformation that adds a scalar to the specified columns.

    Transformation applied to the dataset in place. Only applies to continuous columns.

    Args:
        scalar: the scalar to be used for multiplication. It can be provided
            as a number, in which case all numerical columns will be multiplied
            by the respective scalar or as a dictionary mapping column names
            to scalars for multiplication. Defaults to 0.

    Raises:
        TransformationApplicationError: if the scalar variable is not correctly
                instantiated.
    """

    scalar: Union[int, float, Mapping[str, Union[int, float]]] = 0
    _registry_name = "scalaradd"

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if not isinstance(self.scalar, (int, float, dict)):
            raise TransformationApplicationError(
                f"The scalar definition ({self.scalar}) for this transformation is"
                " incorrect. Please make sure you pass an integer, a float, or a"
                " dictionary with column names mapped to the value of the scalar"
                " that the respective column should be mapped to."
            )


@delegates()
@attr.dataclass(kw_only=True)
class AverageColumnsTransformation(Transformation):
    """Transformation that averages multiple columns into a single new column.

    This transformation computes the mean of the specified source columns and
    creates a new column with the result. Optionally, the result can be rounded
    to the nearest integer and the source columns can be dropped.

    Args:
        cols: List of column names to average. Can use column references
            (e.g., "c:column_name").
        round_to_int: Whether to round the result to the nearest integer.
            Defaults to False.
        drop_source_cols: Whether to drop the source columns after computing
            the average. Defaults to True.
        output: Whether this transformation should be included in the final
            output. Defaults to True.

    Raises:
        ValueError: If fewer than 2 columns are specified.
    """

    _registry_name = "average"

    cols: list[str]
    round_to_int: bool = False
    drop_source_cols: bool = True
    output: bool = True

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if len(self.cols) < 2:
            raise ValueError(
                "AverageColumnsTransformation requires at least 2 columns to average."
            )


@delegates()
@attr.dataclass(kw_only=True)
class DropColumnsTransformation(Transformation):
    """Transformation that drops specified columns from the dataframe.

    This transformation removes the specified columns from the dataframe.

    Args:
        cols: List of column names to drop. Can use column references
            (e.g., "c:column_name").
        output: Whether this transformation should be included in the final
            output. This is always True for DropColumnsTransformation as it
            modifies the dataframe in place.

    Raises:
        ValueError: If no columns are specified.
    """

    _registry_name = "drop"

    cols: list[str]
    output: bool = True

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if len(self.cols) < 1:
            raise ValueError(
                "DropColumnsTransformation requires at least 1 column to drop."
            )
