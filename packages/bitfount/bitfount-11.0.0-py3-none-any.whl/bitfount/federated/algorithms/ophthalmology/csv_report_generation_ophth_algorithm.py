"""Deprecated: Algorithm for outputting results to CSV on the pod-side.

This module is deprecated. Please use
`bitfount.federated.algorithms.csv_report_algorithm` instead.
The `CSVReportGeneratorOphthalmologyAlgorithm` class is now an alias for
`CSVReportAlgorithm` with ophthalmology-specific features available via the
`ophthalmology_args` parameter.
"""

from __future__ import annotations

from typing import Any
import warnings

from bitfount.federated.algorithms.csv_report_algorithm import (
    ColumnFilter,
    CSVReportAlgorithm,
    DFMergeType,
    DFSortType,
    MatchPatientVisit,
    OphthalmologyArgs,
    _WorkerSide,
)
from bitfount.utils.logging_utils import deprecated_class_name

# Re-export for backward compatibility
__all__ = [
    "CSVReportGeneratorOphthalmologyAlgorithm",
    "CSVReportGeneratorAlgorithm",
    "ColumnFilter",
    "DFMergeType",
    "DFSortType",
    "MatchPatientVisit",
    "OphthalmologyArgs",
    "_WorkerSide",
]


class CSVReportGeneratorOphthalmologyAlgorithm(CSVReportAlgorithm):
    """Deprecated: Algorithm for generating the CSV results reports.

    This class is deprecated. Please use `CSVReportAlgorithm` instead.
    All ophthalmology-specific features are now available via the
    `ophthalmology_args` parameter.

    Example migration:
        Before:
            CSVReportGeneratorOphthalmologyAlgorithm(
                datastructure=ds,
                trial_name="MyTrial",
                produce_matched_only=False,
            )

        After:
            CSVReportAlgorithm(
                datastructure=ds,
                ophthalmology_args=OphthalmologyArgs(
                    trial_name="MyTrial",
                    produce_matched_only=False,
                ),
            )
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "CSVReportGeneratorOphthalmologyAlgorithm is deprecated. "
            "Please use CSVReportAlgorithm instead. Ophthalmology-specific "
            "features are available via the `ophthalmology_args` parameter.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# Keep old name for backwards compatibility
@deprecated_class_name
class CSVReportGeneratorAlgorithm(CSVReportGeneratorOphthalmologyAlgorithm):
    """Deprecated: Algorithm for generating the CSV results reports.

    This class is deprecated. Please use `CSVReportAlgorithm` instead.
    """

    pass
