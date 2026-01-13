"""Algorithm for outputting results to CSV on the pod-side."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
import operator
import os
from pathlib import Path
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    Optional,
    Sequence,
    Union,
    cast,
)
import warnings

import desert
from marshmallow import fields, validate
import pandas as pd

from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import (
    ORIGINAL_FILENAME_METADATA_COLUMN,
)
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    FinalStepAlgorithm,
    NoResultsModellerAlgorithm,
)
from bitfount.federated.algorithms.ophthalmology.dataframe_generation_extensions import (  # noqa: E501
    extensions as extensions_registry,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_types import (
    _BITFOUNT_PATIENT_ID_KEY,
    _BITFOUNT_PATIENT_ID_RENAMED,
    ELIGIBILE_VALUE,
    FILTER_FAILED_REASON_COLUMN,
    FILTER_MATCHING_COLUMN,
    NON_ELIGIBILE_VALUE,
    ORIGINAL_DICOM_COLUMNS,
    ORIGINAL_HEIDELBERG_COLUMNS,
    ORIGINAL_TOPCON_COLUMNS,
    TRIAL_NAME_COL,
    TrialNotesCSVArgs,
)
from bitfount.federated.algorithms.ophthalmology.ophth_algo_utils import (
    get_data_for_files,
    get_dataframe_iterator_from_datasource,
    is_file_iterable_source,
)
from bitfount.federated.algorithms.ophthalmology.trial_inclusion_filters import (
    ColumnFilter,
    MethodFilter,
)
from bitfount.federated.exceptions import AlgorithmError, DataProcessingError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.types import ProtocolContext, get_task_results_directory
from bitfount.types import DEPRECATED_STRING, UsedForConfigSchemas
from bitfount.utils.pandas_utils import (
    append_dataframe_to_csv,
    append_encrypted_dataframe_to_csv,
    dataframe_iterable_join,
    read_encrypted_csv,
    to_encrypted_csv,
)

if TYPE_CHECKING:
    from bitfount.types import T_FIELDS_DICT

logger = _get_federated_logger(__name__)


# Type definitions
DFMergeType = Literal["inner", "outer", "left", "right"]
DFSortType = Literal["asc", "desc"]
DFSortMapping = {"asc": True, "desc": False}

_FilterOperatorTypes = Literal[
    "equal",
    "==",
    "equals",
    "not equal",
    "!=",
    "less than",
    "<",
    "less than or equal",
    "<=",
    "greater than",
    ">",
    "greater than or equal",
    ">=",
]

_OperatorMapping = {
    "less than": operator.lt,
    "<": operator.lt,
    "less than or equal": operator.le,
    "<=": operator.le,
    "greater than": operator.gt,
    ">": operator.gt,
    "greater than or equal": operator.ge,
    ">=": operator.ge,
    "equal": operator.eq,
    "==": operator.eq,
    "equals": operator.eq,
    "not equal": operator.ne,
    "!=": operator.ne,
}

# List of ophthalmology-specific argument names for deprecation checking
_OPHTH_ARG_NAMES = [
    "trial_name",
    "aux_cols",
    "match_patient_visit",
    "produce_matched_only",
    "produce_trial_notes_csv",
    "csv_extensions",
]


@dataclass
class MatchPatientVisit(UsedForConfigSchemas):
    """Dataclass for matching patient visits.

    Allows matching of different scans and results for the same patient visit.
    Only two records can be matched for the same patient visit.

    Args:
        cols_to_match: List of columns on which to match.
        divergent_col: Column containing the divergent strings for
            the same patient. E.g. the column indicating whether the
            scan was performed on the left or right eye.
        date_time_col: The column indicating the date of the patient visit.
    """

    # TODO: [BIT-3641] Add support for datasource-agnostic matching criteria
    cols_to_match: list[str]
    divergent_col: str
    date_time_col: str
    how: DFMergeType = desert.field(
        fields.String(validate=validate.OneOf(typing.get_args(DFMergeType))),
        default="outer",
    )


@dataclass
class OphthalmologyArgs(UsedForConfigSchemas):
    """Container for ophthalmology-specific arguments.

    This groups ophthalmology-related options that were previously part of
    CSVReportGeneratorOphthalmologyAlgorithm.

    Args:
        trial_name: The name of the trial for the csv report. If provided,
            the CSV will be saved as "trial_name"-prescreening-patients-"date".csv.
        aux_cols: The auxiliary columns from other datasources to include
            in the report. If not specified, will use defaults.
        match_patient_visit: Used for matching the same patient visit.
        produce_matched_only: If True, only the matched CSV will be generated at the
            end of the run. If False, both the non-matched and matched CSV will be
            generated.
        produce_trial_notes_csv: If True, a CSV file containing the trial notes will
            be generated at the end of the run.
        csv_extensions: List of named CSV extension functions that will be applied
            to the output CSV just before saving to file.
    """

    trial_name: Optional[str] = desert.field(
        fields.String(allow_none=True), default=None
    )
    aux_cols: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True),
        default=None,
    )
    match_patient_visit: Optional[MatchPatientVisit] = desert.field(
        fields.Nested(desert.schema_class(MatchPatientVisit), allow_none=True),
        default=None,
    )
    produce_matched_only: bool = desert.field(fields.Bool(), default=True)
    produce_trial_notes_csv: bool = desert.field(fields.Bool(), default=False)
    csv_extensions: Optional[list[str]] = desert.field(
        fields.List(fields.String(), allow_none=True),
        default=None,
    )


class _WorkerSide(BaseWorkerAlgorithm, FinalStepAlgorithm):
    """Worker side of the algorithm."""

    def __init__(
        self,
        path: Union[str, os.PathLike],
        original_cols: Optional[list[str]] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        columns_to_drop: Optional[list[str]] = None,
        columns_to_drop_prefix: Optional[list[str]] = None,
        columns_to_include: Optional[list[str]] = None,
        filter: Optional[list[Union[ColumnFilter, MethodFilter]]] = None,
        sorting_columns: Optional[dict[str, DFSortType]] = None,
        decimal_places: int = 2,
        # Ophthalmology-specific arguments
        trial_name: Optional[str] = None,
        aux_cols: Optional[list[str]] = None,
        matcher: Optional[MatchPatientVisit] = None,
        matched_csv_path: Optional[Union[str, os.PathLike]] = None,
        produce_matched_only: bool = True,
        csv_extensions: Optional[list[str]] = None,
        produce_trial_notes_csv: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.path = Path(path)
        self.original_cols = original_cols
        self.rename_columns = rename_columns
        self.columns_to_drop = columns_to_drop
        self.columns_to_drop_prefix = columns_to_drop_prefix
        self.columns_to_include = columns_to_include
        self.filter: Optional[list[Union[ColumnFilter, MethodFilter]]] = filter
        self.sorting_columns = sorting_columns
        self.decimal_places = decimal_places

        # Ophthalmology-specific attributes
        self.trial_name = trial_name
        self.task_start_date = datetime.today().strftime("%Y-%m-%d")
        self.filename_mid_segment: str = "prescreening-patients"
        self.aux_cols: Optional[list[str]] = aux_cols if aux_cols is not None else []
        self.matcher = matcher
        self.produce_matched_only = produce_matched_only
        self.produce_trial_notes_csv = produce_trial_notes_csv
        self.matched_filter: Optional[list[ColumnFilter]] = None
        self.trial_notes_csv_args: Optional[TrialNotesCSVArgs] = None

        # Set the path for the matched CSV file output
        self.matched_csv_path: Path
        if matched_csv_path is not None:
            self.matched_csv_path = Path(matched_csv_path)
        else:
            if self.matcher is not None:
                logger.debug("No matched_csv_path defined, using `path`")
            self.matched_csv_path = self.path

        # Warn if both matched and unmatched CSVs point to same file
        if (
            self.matcher is not None
            and not self.produce_matched_only
            and self.matched_csv_path == self.path
            and self.path.suffix
        ):
            logger.warning(
                f"Both matched and unmatched CSVs have been requested but"
                f" they are to be saved to the same file path"
                f" ({self.path}); the matched CSV will overwrite the"
                f" unmatched CSV."
            )

        # CSV extensions
        self.csv_extensions: list[str] = []
        if csv_extensions is not None:
            for ext in csv_extensions:
                if ext not in extensions_registry:
                    logger.warning(
                        f'CSV extension "{ext}" was requested but was not found'
                        f" in the extensions registry. Will not be applied."
                    )
                else:
                    logger.info(
                        f'CSV extension "{ext}" was requested and will be applied.'
                    )
                    self.csv_extensions.append(ext)

        self.encryption_key: Optional[str] = None
        self._run_csv_path: Optional[Path] = None

    def _append_to_csv(self, csv_path: Path, df: pd.DataFrame) -> Path:
        """Append DataFrame to CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            df: DataFrame to append.

        Returns:
            The actual path where the CSV was written.
        """
        if self.encryption_key is not None:
            return append_encrypted_dataframe_to_csv(csv_path, df, self.encryption_key)
        else:
            return append_dataframe_to_csv(csv_path, df)

    def _write_to_csv(self, csv_path: Path, df: pd.DataFrame, **kwargs: Any) -> Path:
        """Write DataFrame to CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            df: DataFrame to write.
            **kwargs: Additional arguments for to_csv/to_encrypted_csv.

        Returns:
            The actual path where the CSV was written.
        """
        if self.encryption_key is not None:
            return to_encrypted_csv(df, csv_path, self.encryption_key, **kwargs)
        else:
            df.to_csv(csv_path, **kwargs)
            return csv_path

    def _read_from_csv(self, csv_path: Path, **kwargs: Any) -> pd.DataFrame:
        """Read DataFrame from CSV file with optional encryption.

        Args:
            csv_path: Path to the CSV file.
            **kwargs: Additional arguments for read_csv/read_encrypted_csv.

        Returns:
            The DataFrame read from the CSV file.
        """
        if self.encryption_key is not None:
            return read_encrypted_csv(csv_path, self.encryption_key, **kwargs)
        else:
            return cast(pd.DataFrame, pd.read_csv(csv_path, **kwargs))

    @property
    def file_name(self) -> str:
        """Returns the file name for the CSV report."""
        if self.trial_name is not None:
            file_name = (
                f"{self.trial_name}-{self.filename_mid_segment}-{self.task_start_date}"
            )
        else:
            file_name = "results"
        return file_name

    def set_column_filters(
        self, filters: Sequence[Union[ColumnFilter, MethodFilter]]
    ) -> None:
        """Sets the column filters for the worker.

        If filters already exist, the new filters will be appended to
        the existing ones.

        Args:
            filters: List of column filters or method filters to set.
        """
        if self.filter is None:
            self.filter = list(filters)
        else:
            self.filter.extend(filters)

    def set_filter(self, filters: Sequence[Union[ColumnFilter, MethodFilter]]) -> None:
        """Sets the filter attribute with proper type handling.

        This method handles the list invariance issue by creating a new list,
        allowing assignment of narrower filter types to the broader filter
        attribute type.

        Args:
            filters: List of column filters or method filters to set.
        """
        self.filter = list(filters)

    def set_aux_cols(self, aux_cols: Optional[list[str]]) -> None:
        """Sets the aux_cols attribute.

        Args:
            aux_cols: The auxiliary columns to set, or None to clear.
        """
        self.aux_cols = aux_cols

    def use_default_columns(self) -> None:
        """Sets the default columns to include based on the datasource."""
        if self.original_cols is None:
            if type(self.datasource).__name__ == "HeidelbergSource":
                self.original_cols = ORIGINAL_HEIDELBERG_COLUMNS
            elif type(self.datasource).__name__ == "DICOMOphthalmologySource":
                self.original_cols = ORIGINAL_DICOM_COLUMNS
            elif type(self.datasource).__name__ == "TopconSource":
                self.original_cols = ORIGINAL_TOPCON_COLUMNS

    def _update_matcher_columns(self) -> None:
        """Updates the matcher columns to the renamed columns."""
        self.matcher = cast(MatchPatientVisit, self.matcher)
        if self.rename_columns:
            self.matcher.cols_to_match = [
                self.rename_columns.get(col, col) for col in self.matcher.cols_to_match
            ]
            self.matcher.divergent_col = self.rename_columns.get(
                self.matcher.divergent_col, self.matcher.divergent_col
            )
            self.matcher.date_time_col = self.rename_columns.get(
                self.matcher.date_time_col, self.matcher.date_time_col
            )

    def _match_same_patient_visit(self, df: pd.DataFrame) -> pd.DataFrame:
        """Matches two patient records to the same visit within 24 hours.

        Args:
            df: The dataframe on which the filter is applied.
        """
        if self.matcher is None:
            return df
        else:
            self._update_matcher_columns()
        try:
            if len(unique_vals := df[self.matcher.divergent_col].unique()) != 2:
                if len(unique_vals) > 2:
                    logger.warning(
                        f"Divergent column `{self.matcher.divergent_col}` has more "
                        "than 2 unique values. We can only match two patient visits. "
                        "Saving CSV report without matching individual visits."
                    )
                    return df
                elif len(unique_vals) == 1:
                    if self.matcher.how == "outer":
                        logger.warning(
                            f"Divergent column `{self.matcher.divergent_col}` "
                            f"has only 1 unique value. Saving CSV report "
                            f"without matching individual visits."
                        )
                        return df
                    else:
                        # Return empty df if only one unique value
                        # and `how` is not outer
                        return pd.DataFrame(columns=df.columns)
            elif not df[self.matcher.cols_to_match].duplicated().any():
                # TODO: [BIT-2621] This doesn't take into account the `date_time_col`
                #       when checking for duplicates. This means that even if there
                #       are two records with the same values in the `cols_to_match`
                #       columns, but datetimes that are more than 24 hours apart, they
                #       won't be matched but the dataframe will still be split anyway.
                #       It also doesn't take into account the `divergent_col` column
                #       which means that even if there are two records with the same
                #       values in the `cols_to_match` columns, they may still have
                #       the same values in the `divergent_col` column and therefore
                #       won't be matched either. Therefore, this check is not sufficient
                #       to determine whether or not the dataframe definitely will have
                #       matches but it should account for the vast majority of cases
                #       where there are definitely no matches.
                logger.info(
                    "No duplicate records found across the specified columns. "
                    "Saving CSV report without matching individual visits."
                )
                return df

            df[self.matcher.date_time_col] = pd.to_datetime(
                df[self.matcher.date_time_col],
                format="mixed",
            )
            df_list = []
            if any(
                df[self.matcher.cols_to_match]
                .apply(pd.to_numeric, errors="ignore")
                .applymap(lambda x: isinstance(x, float), na_action="ignore")
                .any()
            ):
                # merge_asof does not allow matching on float values,
                # so we log a warning
                logger.warning(
                    "Matching records is not supported on float columns."
                    "Saving CSV report without matching individual visits."
                )
                return df
            for item in unique_vals:
                df_list.append(
                    df.where(df[self.matcher.divergent_col] == item)
                    .dropna(how="all")
                    .copy()
                )
            # sort values and convert dtypes
            df1 = df_list[0].sort_values(self.matcher.date_time_col).convert_dtypes()
            df2 = df_list[1].sort_values(self.matcher.date_time_col).convert_dtypes()

            # merge on datetime within 24hours by specific column
            # merge_asof does not implement outer merge, so we have to merge
            # separately left and right and then combine them.
            df_left_to_right_merge = pd.merge_asof(
                df1,
                df2,
                on=self.matcher.date_time_col,
                by=self.matcher.cols_to_match,
                tolerance=pd.Timedelta("24h"),
                suffixes=[
                    "_" + str(unique_vals[0]),
                    "_" + str(unique_vals[1]),
                ],
                direction="nearest",
            )
            df_right_to_left_merge = pd.merge_asof(
                df2,
                df1,
                on=self.matcher.date_time_col,
                by=self.matcher.cols_to_match,
                tolerance=pd.Timedelta("24h"),
                suffixes=[
                    "_" + str(unique_vals[1]),
                    "_" + str(unique_vals[0]),
                ],
                direction="nearest",
            )
            # get common cols and remove the date-time
            common_cols = df_left_to_right_merge.columns.to_list()
            common_cols.remove(self.matcher.date_time_col)
            # final merge to ensure date-time for both patient visits are there
            matched_df = pd.merge(
                df_left_to_right_merge,
                df_right_to_left_merge,
                on=common_cols,
                suffixes=[
                    "_" + str(unique_vals[0]),
                    "_" + str(unique_vals[1]),
                ],
                how=self.matcher.how,
            )
            return matched_df
        except KeyError as e:
            logger.warning(
                f"KeyError: {str(e)}. Saving CSV report without matching "
                "individual visits."
            )
            return df

    def initialise(
        self,
        *,
        datasource: BaseSource,
        task_id: str,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        encryption_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource, datasplitter and encryption key.

        Args:
            datasource: The datasource to initialise the data from.
            task_id: The task id to initialise the data from.
            data_splitter: The data splitter to use for splitting the data.
            pod_dp: The pod dp to use for the data.
            pod_identifier: The pod identifier to use for the data.
            encryption_key: The encryption key to use for the data.
            **kwargs: Additional keyword arguments that may be passed to the algorithm.
        """
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)
        if encryption_key is not None:
            logger.debug("Setting encryption key.")
            self.encryption_key = encryption_key

    def _add_filtering_to_csv_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds filtering to the CSV dataframe (supports all filter types)."""
        df[FILTER_MATCHING_COLUMN] = True
        df[FILTER_FAILED_REASON_COLUMN] = ""
        if self.filter is not None:
            logger.debug("Filtering data.")
            # Ensure filter columns will be included in output
            if self.original_cols is not None:
                if FILTER_MATCHING_COLUMN not in self.original_cols:
                    self.original_cols.append(FILTER_MATCHING_COLUMN)
            for i, col_filter in enumerate(self.filter):
                logger.debug(f"Running filter {i + 1}")
                try:
                    if isinstance(col_filter, ColumnFilter):
                        # Get columns before applying filter to identify new column
                        cols_before = set(df.columns)
                        df = col_filter.apply_filter(
                            df, rename_columns=self.rename_columns
                        )
                        # Update original_cols with filter column names
                        if self.original_cols is not None:
                            # Find the filter column that was just added
                            cols_after = set(df.columns)
                            new_cols = cols_after - cols_before
                            for filter_col_name in new_cols:
                                if filter_col_name not in self.original_cols:
                                    self.original_cols.append(filter_col_name)
                    elif isinstance(col_filter, MethodFilter):
                        df = col_filter.apply_filter(
                            df, rename_columns=self.rename_columns
                        )
                    else:
                        raise TypeError(f"Unknown filter type: {type(col_filter)}")
                except (KeyError, TypeError) as e:
                    if isinstance(e, KeyError):
                        logger.warning(
                            f"Missing column, filtering only on remaining"
                            f" given columns: {e}"
                        )
                    else:
                        logger.warning(f"Filter raised TypeError: {str(e)}")
                    logger.info("Filtering will skip this filter")
        return df

    def _add_filtering_to_matched_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds filtering to the matched dataframe."""
        logger.debug("Filtering data.")
        df[FILTER_MATCHING_COLUMN] = True
        df[FILTER_FAILED_REASON_COLUMN] = ""
        if self.matched_filter is not None:
            for i, col_filter in enumerate(self.matched_filter):
                logger.debug(f"Running filter {i + 1}")
                try:
                    df = col_filter._add_partial_filtering_to_df(
                        df,
                        drop_filtered_cols=True,
                        add_new_col_for_filter=False,
                        rename_columns=self.rename_columns,
                    )
                except (KeyError, TypeError) as e:
                    if isinstance(e, KeyError):
                        logger.warning(
                            f"No column `{col_filter.column}` found in the data. "
                            "Filtering only on remaining given columns"
                        )
                    else:
                        logger.warning(
                            f"Filter column {col_filter.identifier} "
                            f"raised TypeError: {str(e)}"
                        )
                    logger.info(f"Filtering will skip `{col_filter.identifier}`")
        return df

    def _extract_source_data(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        filenames: Optional[list[str]],
    ) -> Iterable[pd.DataFrame]:
        """Extract data from datasource based on filenames or iterate all files.

        Args:
            results_df: The results dataframe(s) from inference.
            filenames: Optional list of filenames to retrieve data for.

        Returns:
            An iterable of dataframes from the datasource.
        """
        if filenames is not None and is_file_iterable_source(self.datasource):
            logger.debug(f"Retrieving data for: {filenames}")
            df: pd.DataFrame = get_data_for_files(
                cast(FileSystemIterableSource, self.datasource), filenames
            )
            test_data_dfs: Iterable[pd.DataFrame] = [df]

            if len(filenames) != len(df):
                raise DataProcessingError(
                    f"Length of results ({len(df)})"
                    f" does not match the number of files ({len(filenames)})"
                    f" while processing CSV report."
                )
            return test_data_dfs

        # Fallback: iterate through all files
        logger.debug(f"{len(results_df)=}, {len(self.datasource)=}")
        if isinstance(results_df, pd.DataFrame) and len(results_df) == len(
            self.datasource
        ):
            if self.original_cols and not all(
                res_col in self.original_cols for res_col in results_df.columns.tolist()
            ):
                self.original_cols += [
                    res_col
                    for res_col in results_df.columns.tolist()
                    if res_col not in self.original_cols
                ]
            logger.debug("Joining datasource dataframe to results dataframe")
            results_df = results_df.reset_index(drop=True)

            if isinstance(self.datasource, FileSystemIterableSource):
                return self._extract_from_file_system_source(results_df)
            else:
                return self._extract_from_generic_source(results_df)
        else:
            return get_dataframe_iterator_from_datasource(
                self.datasource, self.data_splitter
            )

    def _extract_from_file_system_source(
        self, results_df: pd.DataFrame
    ) -> Iterable[pd.DataFrame]:
        """Extract data from FileSystemIterableSource.

        Args:
            results_df: The results dataframe from inference.

        Returns:
            An iterable of dataframes.
        """
        if ORIGINAL_FILENAME_METADATA_COLUMN in results_df:
            file_names: list[str] = results_df[
                ORIGINAL_FILENAME_METADATA_COLUMN
            ].tolist()
            logger.debug(f"Getting data for: {file_names}")
            file_df = cast(FileSystemIterableSource, self.datasource).get_data(
                file_names
            )
            if file_df is not None:
                merged = file_df.merge(results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN)
                return [merged]
            else:
                return [pd.DataFrame(columns=[ORIGINAL_FILENAME_METADATA_COLUMN])]
        else:
            return dataframe_iterable_join(
                cast(FileSystemIterableSource, self.datasource).yield_data(
                    data_keys=cast(
                        FileSystemIterableSource, self.datasource
                    ).selected_file_names
                ),
                results_df,
                reset_joiners_index=True,
            )

    def _extract_from_generic_source(
        self, results_df: pd.DataFrame
    ) -> Iterable[pd.DataFrame]:
        """Extract data from a generic datasource.

        Args:
            results_df: The results dataframe from inference.

        Returns:
            An iterable of dataframes.
        """
        if ORIGINAL_FILENAME_METADATA_COLUMN in results_df.columns:
            # Collect all data and merge on filename
            all_source_data = pd.concat(
                list(self.datasource.yield_data()), ignore_index=True
            )
            if ORIGINAL_FILENAME_METADATA_COLUMN in all_source_data.columns:
                logger.debug(
                    f"Merging on {ORIGINAL_FILENAME_METADATA_COLUMN}: "
                    f"source has {len(all_source_data)} rows, "
                    f"results has {len(results_df)} rows"
                )
                merged = all_source_data.merge(
                    results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                )
                logger.debug(f"Merged result has {len(merged)} rows")
                return [merged]
            else:
                # Fallback to index-based join
                joinee_df = results_df.drop(columns=[ORIGINAL_FILENAME_METADATA_COLUMN])
                return dataframe_iterable_join(
                    self.datasource.yield_data(),
                    joinee_df,
                    reset_joiners_index=True,
                )
        else:
            return dataframe_iterable_join(
                self.datasource.yield_data(),
                results_df,
                reset_joiners_index=True,
            )

    def _combine_results_dataframes(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        filenames: Optional[list[str]],
    ) -> pd.DataFrame:
        """Combine multiple results dataframes into one.

        Args:
            results_df: Single dataframe or list of dataframes.
            filenames: Optional list of filenames (determines merge strategy).

        Returns:
            Combined dataframe.
        """
        if isinstance(results_df, list):
            if filenames is not None:
                for i, df in enumerate(results_df):
                    if ORIGINAL_FILENAME_METADATA_COLUMN not in df.columns:
                        raise ValueError(
                            f"Results dataframe at index {i}"
                            f" is missing required key column"
                            f" {ORIGINAL_FILENAME_METADATA_COLUMN}"
                        )
                # Merge all dataframes on filename column
                return reduce(
                    lambda left, right: pd.merge(
                        left, right, on=ORIGINAL_FILENAME_METADATA_COLUMN
                    ),
                    results_df,
                )
            else:
                return pd.concat(results_df, axis="columns")
        else:
            return results_df

    def _update_original_cols_from_results(self, aux_results_df: pd.DataFrame) -> None:
        """Add result columns to original_cols based on aux_cols settings.

        Args:
            aux_results_df: The combined results dataframe.
        """
        if self.original_cols is None:
            return

        if all(
            res_col in self.original_cols for res_col in aux_results_df.columns.tolist()
        ):
            return

        if self.aux_cols is None or len(self.aux_cols) == 0:
            self.original_cols += [
                res_col
                for res_col in aux_results_df.columns.tolist()
                if res_col not in self.original_cols
            ]
        else:
            self.original_cols += [
                res_col
                for res_col in aux_results_df.columns.tolist()
                if ((res_col not in self.original_cols) and (res_col in self.aux_cols))
            ]

    def _merge_source_and_results(
        self,
        test_data_dfs: Iterable[pd.DataFrame],
        aux_results_df: pd.DataFrame,
        filenames: Optional[list[str]],
    ) -> Iterable[pd.DataFrame]:
        """Merge source data with results dataframe.

        Args:
            test_data_dfs: Iterable of source dataframes.
            aux_results_df: The combined results dataframe.
            filenames: Optional list of filenames.

        Returns:
            Iterable of merged dataframes.
        """
        if filenames is not None:
            test_data_dfs = cast(list[pd.DataFrame], test_data_dfs)
            if ORIGINAL_FILENAME_METADATA_COLUMN not in test_data_dfs[0].columns:
                raise ValueError(
                    f"Retrieved file data dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )
            if ORIGINAL_FILENAME_METADATA_COLUMN not in aux_results_df.columns:
                raise ValueError(
                    f"Results dataframe is missing"
                    f" the required key column: {ORIGINAL_FILENAME_METADATA_COLUMN}"
                )
            # Drop overlapping columns from source data (results take precedence)
            source_df = test_data_dfs[0]
            overlapping_cols = set(aux_results_df.columns) - {
                ORIGINAL_FILENAME_METADATA_COLUMN
            }
            source_df_clean = source_df.drop(
                columns=[c for c in source_df.columns if c in overlapping_cols]
            )
            return [
                source_df_clean.merge(
                    aux_results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                )
            ]
        else:
            # if not isinstance(test_data_dfs, list):
            return self._merge_iterable_with_results(test_data_dfs, aux_results_df)
            # return test_data_dfs

    def _merge_iterable_with_results(
        self,
        test_data_dfs: Iterable[pd.DataFrame],
        aux_results_df: pd.DataFrame,
    ) -> Iterable[pd.DataFrame]:
        """Merge an iterable of dataframes with results.

        Args:
            test_data_dfs: Iterable of source dataframes.
            aux_results_df: The combined results dataframe.

        Returns:
            Iterable of merged dataframes.
        """
        if ORIGINAL_FILENAME_METADATA_COLUMN in aux_results_df.columns:
            # Collect all data and merge on filename
            # Convert to list first to avoid exhausting the iterable
            test_data_dfs_list = cast(list[pd.DataFrame], test_data_dfs)
            all_source_data = pd.concat(test_data_dfs_list, ignore_index=True)
            if ORIGINAL_FILENAME_METADATA_COLUMN in all_source_data.columns:
                logger.debug(
                    f"Merging on {ORIGINAL_FILENAME_METADATA_COLUMN}: "
                    f"source has {len(all_source_data)} rows, "
                    f"results has {len(aux_results_df)} rows"
                )
                # Drop overlapping columns from source data (results take precedence)
                overlapping_cols = set(aux_results_df.columns) - {
                    ORIGINAL_FILENAME_METADATA_COLUMN
                }
                all_source_data_clean = all_source_data.drop(
                    columns=[
                        c for c in all_source_data.columns if c in overlapping_cols
                    ]
                )
                merged = all_source_data_clean.merge(
                    aux_results_df, on=ORIGINAL_FILENAME_METADATA_COLUMN
                )
                logger.debug(f"Merged result has {len(merged)} rows")
                return [merged]
            else:
                # Fallback to index-based join
                logger.warning(
                    "Joining results and original data iteratively;"
                    " data must be provided in the same order in both"
                )
                joinee_df = aux_results_df.drop(
                    columns=[ORIGINAL_FILENAME_METADATA_COLUMN]
                )
                # Use the list we already created instead of the exhausted iterable

                return dataframe_iterable_join(iter(test_data_dfs_list), joinee_df)
        else:
            logger.warning(
                "Joining results and original data iteratively;"
                " data must be provided in the same order in both"
            )
            # Drop overlapping columns from source data (results take precedence)
            overlapping_cols = set(aux_results_df.columns)
            return dataframe_iterable_join(
                (
                    df.drop(columns=[c for c in df.columns if c in overlapping_cols])
                    for df in test_data_dfs
                ),
                aux_results_df,
            )

    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process a single dataframe for CSV output.

        Applies filtering, extensions, column operations, and formatting.

        Args:
            df: The dataframe to process.

        Returns:
            Processed dataframe ready for CSV output.
        """
        # Apply filtering
        if self.filter is not None:
            df = self._add_filtering_to_csv_df(df)

        # Handle Eligibility column formatting
        if (
            self.rename_columns is not None
            and (FILTER_MATCHING_COLUMN, "Eligibility") in self.rename_columns.items()
            and FILTER_MATCHING_COLUMN in df.columns
        ):
            df[FILTER_MATCHING_COLUMN] = df[FILTER_MATCHING_COLUMN].replace(
                {True: "Eligible", False: "Not Eligible"}
            )

        # Remove trailing comma from filter failed reason
        if FILTER_FAILED_REASON_COLUMN in df.columns:
            df[FILTER_FAILED_REASON_COLUMN] = df[
                FILTER_FAILED_REASON_COLUMN
            ].str.rstrip(", ")

        # Ensure filename column is included
        if (
            isinstance(self.datasource, FileSystemIterableSource)
            and self.original_cols is not None
            and len(self.original_cols) > 0
            and ORIGINAL_FILENAME_METADATA_COLUMN not in self.original_cols
        ):
            self.original_cols.append(ORIGINAL_FILENAME_METADATA_COLUMN)

        # Handle image columns
        if isinstance(self.datasource, FileSystemIterableSource):
            df = self._process_image_columns(df)

        # Apply CSV extensions
        for ext in self.csv_extensions:
            logger.info(f"Applying {ext} extension to CSV")
            logger.info(f"DataFrame columns before {ext}: {df.columns.tolist()}")
            ext_func = extensions_registry[ext]
            df = ext_func(df)
            logger.info(f"DataFrame columns after {ext}: {df.columns.tolist()}")

        # Add trial name column
        if self.trial_name:
            df["Study name"] = self.trial_name
        if self.trial_name and self.matcher is not None:
            self.matcher.cols_to_match.append("Study name")

        # Add patient ID to matcher if present
        if _BITFOUNT_PATIENT_ID_RENAMED in df.columns and self.matcher is not None:
            if _BITFOUNT_PATIENT_ID_RENAMED not in self.matcher.cols_to_match:
                self.matcher.cols_to_match.append(_BITFOUNT_PATIENT_ID_RENAMED)
        if _BITFOUNT_PATIENT_ID_KEY in df.columns and self.matcher is not None:
            if _BITFOUNT_PATIENT_ID_KEY not in self.matcher.cols_to_match:
                self.matcher.cols_to_match.append(_BITFOUNT_PATIENT_ID_KEY)
        # Drop specified columns
        df = self._drop_columns(df)

        # Filter to original_cols and rename
        csv_df = self._select_and_rename_columns(df)

        return csv_df

    def _process_image_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process image columns in the dataframe.

        Args:
            df: The dataframe to process.

        Returns:
            Dataframe with image columns processed.
        """
        datasource = cast(FileSystemIterableSource, self.datasource)
        img_columns = list(datasource.image_columns)
        existing_img_columns = list(set(img_columns) & set(df.columns))
        missing_img_columns = set(img_columns) - set(df.columns)

        if missing_img_columns:
            logger.warning(
                f"DataFrame has {len(existing_img_columns)} out of"
                f" {len(img_columns)} image columns."
                f"Missing {len(missing_img_columns)} image columns."
            )
            logger.debug(
                "The following image columns are missing from"
                f" the DataFrame: {missing_img_columns}"
            )

        if existing_img_columns and datasource.cache_images is False:
            img_df = df[existing_img_columns]
            img_df = img_df.mask(img_df.notna(), other=True)
            img_df = img_df.mask(img_df.isna(), other=None)
            df[existing_img_columns] = img_df

        return df

    def _drop_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop specified columns from the dataframe.

        Args:
            df: The dataframe to process.

        Returns:
            Dataframe with columns dropped.
        """
        # Drop explicitly specified columns
        if self.columns_to_drop is not None:
            cols_to_drop = [col for col in self.columns_to_drop if col in df.columns]
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)

        # Drop columns by prefix
        if self.columns_to_drop_prefix is not None:
            for prefix in self.columns_to_drop_prefix:
                cols_to_drop = [col for col in df.columns if col.startswith(prefix)]
                if cols_to_drop:
                    df = df.drop(columns=cols_to_drop)

        return df

    def _select_and_rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select columns and apply renaming.

        Selection priority:
        1. If columns_to_include is set, use only those columns (in order)
        2. Otherwise, if original_cols is set, use those columns
        3. Otherwise, use all columns

        Missing columns are silently skipped.

        Args:
            df: The dataframe to process.

        Returns:
            Dataframe with selected and renamed columns.
        """
        # Determine which columns to include
        if self.columns_to_include is not None:
            # Use columns_to_include - strict ordered, missing silently skipped
            report_cols = [col for col in self.columns_to_include if col in df.columns]
            if len(report_cols) != 0:
                csv_df = df[report_cols].copy()
            else:
                csv_df = df.copy()
                logger.warning(
                    "No columns from the columns_to_include list were found "
                    "in the data. Saving the whole dataframe to csv."
                )
        elif self.original_cols is not None:
            # Fall back to original_cols behavior
            report_cols = [col for col in self.original_cols if col in df.columns]
            if len(report_cols) != 0:
                csv_df = df[report_cols].copy()
            else:
                csv_df = df.copy()
                logger.warning(
                    "No columns from the original_cols list were found "
                    "in the data. Saving the whole dataframe to csv."
                )
        else:
            csv_df = df.copy()

        # Rename columns if specified
        if self.rename_columns is not None:
            csv_df.rename(columns=self.rename_columns, inplace=True, errors="ignore")

        return csv_df

    def run(
        self,
        results_df: Union[pd.DataFrame, list[pd.DataFrame]],
        task_id: str,
        final_batch: bool = False,
        filenames: Optional[list[str]] = None,
        encryption_key: Optional[str] = None,
    ) -> Union[str, tuple[Optional[Path], int, bool]]:
        """Generates a CSV file at the user specified path.

        Args:
            results_df: The results of the previous inference task.
            task_id: The ID of the task.
            final_batch: Whether this is the final batch (deprecated).
            filenames: The list of files that the results correspond to.
            encryption_key: The encryption key for encrypted CSV data.

        Returns:
            The path to the CSV file as a string, or a tuple containing
            (matched_csv_path, unique_patient_count, matched_data) for
            ophthalmology workflows.
        """
        # Handle deprecation warning
        if final_batch:
            warnings.warn(
                "final_batch parameter is deprecated and will be removed "
                "in a future release. Matching logic moved to "
                "run_final_step() method.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Setup encryption
        if encryption_key is not None:
            logger.debug("Setting encryption key.")
            self.encryption_key = encryption_key

        # Get the path to the CSV file
        csv_path = self._get_unique_csv_path(self.path, self.file_name, task_id)
        self._run_csv_path = csv_path

        # Step 1: Extract data from datasource
        test_data_dfs = self._extract_source_data(results_df, filenames)

        # Convert to list to check if empty (and allow multiple iterations)
        test_data_dfs = list(test_data_dfs)
        if not test_data_dfs:
            logger.error("Datasource has no test set, cannot produce CSV.")
            raise AlgorithmError("Datasource has no test set, cannot produce CSV.")

        # Step 2: Combine multiple results dataframes into one
        aux_results_df = self._combine_results_dataframes(results_df, filenames)
        # Step 3: Update original_cols with result columns
        self._update_original_cols_from_results(aux_results_df)

        # Validate result count matches filenames
        len_aux_results_df = len(aux_results_df)
        if filenames is not None and len(filenames) != len_aux_results_df:
            raise DataProcessingError(
                f"Length of results ({len_aux_results_df})"
                f" does not match the number of files ({len(filenames)})"
                f" while processing CSV report."
            )

        logger.debug("Appending results to the original data.")

        # Step 4: Merge source data with results
        test_data_dfs = self._merge_source_and_results(
            test_data_dfs, aux_results_df, filenames
        )

        # Step 5: Process each dataframe and write to CSV
        len_test_data_dfs = 0
        for df in test_data_dfs:
            len_test_data_dfs += len(df)
            csv_df = self._process_dataframe(df)

            # Write to CSV
            this_csv_path = self._append_to_csv(
                csv_path, csv_df.round(decimals=self.decimal_places)
            )
            logger.debug(f"CSV output to {this_csv_path}")
            csv_path = this_csv_path
            self._run_csv_path = this_csv_path

        # Step 6: Sort CSV if specified
        if self.sorting_columns is not None:
            logger.info("Sorting the CSV file based on the specified columns.")
            self.sort_csv(csv_path)

        # Validate record counts
        if filenames is not None and isinstance(
            self.datasource, FileSystemIterableSource
        ):
            if len_aux_results_df != len_test_data_dfs:
                raise DataProcessingError(
                    f"Number of predictions ({len_aux_results_df})"
                    f" does not match the number of records ({len_test_data_dfs})"
                    f" while processing CSV report."
                )

        # Return appropriate result based on workflow type
        if (
            self.matcher is not None
            or self.trial_name is not None
            or filenames is not None
        ):
            unique_patient_count = self._get_unique_patients_id_count(csv_path)
            return None, unique_patient_count, False
        else:
            # Handle encrypted CSV files properly
            if self.encryption_key is not None:
                # Read encrypted CSV and convert to string
                df = self._read_from_csv(csv_path, index_col=False)
                return df.to_csv(index=False)
            else:
                return csv_path.read_text(encoding="utf-8")

    def run_final_step(
        self, *, context: ProtocolContext, **kwargs: Any
    ) -> tuple[Optional[Path], int, bool]:
        """Execute CSV matching and sorting post main run."""
        matched_csv_path: Optional[Path] = None
        matched_data: bool = False
        if self.matcher is not None:
            task_id: str = context.task_id
            if self._run_csv_path is None or not self._run_csv_path.exists():
                logger.warning("No CSV file found for final reduce step")
                return None, 0, False
            matched_csv_path, matched_data = self._produce_matched_csv(
                self._run_csv_path, task_id
            )
            if self.sorting_columns is not None and matched_csv_path is not None:
                logger.info(
                    "Sorting the matched CSV file based on the specified columns."
                )
                self.sort_csv(matched_csv_path)

            if matched_csv_path and self.produce_trial_notes_csv:
                self._produce_trial_notes_csv(matched_csv_path, task_id)
            elif self.produce_trial_notes_csv:
                self._produce_trial_notes_csv(self._run_csv_path, task_id)

        if self._run_csv_path is not None and self._run_csv_path.exists():
            unique_patient_count = self._get_unique_patients_id_count(
                self._run_csv_path
            )
        else:
            unique_patient_count = 0

        return matched_csv_path, unique_patient_count, matched_data

    def _produce_matched_csv(
        self, csv_path: Path, task_id: str
    ) -> tuple[Optional[Path], bool]:
        """Produce the matched CSV file."""
        logger.info("Matching patient info across visits.")
        data = self._read_from_csv(csv_path, index_col=False)
        matched_data = False
        if not data.empty:
            try:
                all_data = self._match_same_patient_visit(data)
            except Exception as e:
                logger.error(
                    f"Error while matching patient visits: {str(e)}. "
                    "Skipping patient matching."
                )
                all_data = pd.DataFrame()
            if not all_data.empty:
                matched_csv_path = self._get_matched_csv_path(csv_path, task_id)
                logger.debug(f"Saving matched patients data to {matched_csv_path}")
                if self.filter:
                    all_data = self._add_filtering_to_matched_df(all_data)
                    if FILTER_MATCHING_COLUMN in all_data.columns:
                        all_data[FILTER_MATCHING_COLUMN] = all_data[
                            FILTER_MATCHING_COLUMN
                        ].astype(str)
                        all_data[FILTER_MATCHING_COLUMN] = all_data[
                            FILTER_MATCHING_COLUMN
                        ].replace(
                            {"True": ELIGIBILE_VALUE, "False": NON_ELIGIBILE_VALUE}
                        )
                        col_list = [
                            c for c in all_data.columns if c != FILTER_MATCHING_COLUMN
                        ]
                        if TRIAL_NAME_COL in col_list:
                            col_list.insert(1, FILTER_MATCHING_COLUMN)
                        else:
                            col_list.insert(0, FILTER_MATCHING_COLUMN)
                        all_data = all_data[col_list]
                    if (
                        self.rename_columns
                        and FILTER_MATCHING_COLUMN in self.rename_columns
                    ):
                        all_data.rename(
                            columns={
                                FILTER_MATCHING_COLUMN: self.rename_columns[
                                    FILTER_MATCHING_COLUMN
                                ]
                            },
                            inplace=True,
                            errors="ignore",
                        )

                matched_csv_path = self._append_to_csv(
                    matched_csv_path, all_data.round(decimals=self.decimal_places)
                )
                logger.info(f"Saved matched patients data to {matched_csv_path}")
                matched_data = True
                return matched_csv_path, matched_data
            else:
                logger.warning(
                    "No matches were found, but matching was requested. "
                    "Returning original csv path."
                )
                return csv_path, matched_data
        else:
            return None, matched_data

    def _get_unique_patients_id_count(self, csv_path: Path) -> int:
        """Get the unique patient ids from the csv file."""
        try:
            all_data = self._read_from_csv(
                csv_path, usecols=[_BITFOUNT_PATIENT_ID_RENAMED], index_col=False
            )
            return len(all_data[_BITFOUNT_PATIENT_ID_RENAMED].unique())
        except ValueError:
            try:
                all_data = self._read_from_csv(
                    csv_path, usecols=[_BITFOUNT_PATIENT_ID_KEY], index_col=False
                )
                return len(all_data[_BITFOUNT_PATIENT_ID_KEY].unique())
            except ValueError:
                all_data = self._read_from_csv(csv_path, index_col=False)
                return len(all_data)

    def sort_csv(self, csv_path: Path) -> None:
        """Sort the csv file based on the columns specified in sorting_columns."""
        if self.sorting_columns is not None:
            logger.info("Sorting the CSV file based on the specified columns.")
            all_data = self._read_from_csv(csv_path)
            columns_to_sort_by = []
            how_to_sort = []
            for column, sort_type in self.sorting_columns.items():
                find_matching_cols = [
                    col
                    for col in all_data.columns
                    if col.lower()
                    .replace(" ", "")
                    .startswith(column.lower().replace(" ", ""))
                ]
                if len(find_matching_cols) == 0:
                    if self.rename_columns and column in self.rename_columns.keys():
                        find_matching_cols_renamed = [
                            col
                            for col in all_data.columns
                            if col.lower()
                            .replace(" ", "")
                            .startswith(
                                self.rename_columns[column].lower().replace(" ", "")
                            )
                        ]
                        columns_to_sort_by.extend(find_matching_cols_renamed)
                        how_to_sort.extend(
                            [DFSortMapping[sort_type]] * len(find_matching_cols_renamed)
                        )
                    else:
                        logger.warning(
                            f"Column {column} not found in the data, "
                            "skipping any sorting based on it."
                        )
                else:
                    columns_to_sort_by.extend(find_matching_cols)
                    how_to_sort.extend(
                        [DFSortMapping[sort_type]] * len(find_matching_cols)
                    )
            if not len(columns_to_sort_by) == 0:
                all_data.sort_values(
                    columns_to_sort_by, ascending=how_to_sort, inplace=True
                )
                csv_path = self._write_to_csv(csv_path, all_data, index=False)
                self._run_csv_path = csv_path
            else:
                logger.warning(
                    "None of the columns specified for sorting were found in the data."
                )

    def _trial_notes_csv_path(self, task_id: str, eligible_only: bool = True) -> Path:
        """Get the path to save the trial notes CSV to."""
        if self.trial_name is not None and eligible_only:
            file_name = f"{self.trial_name}-eligible-patients-notes-template"
        elif self.trial_name:
            file_name = f"{self.trial_name}-patients-notes-template"
        else:
            file_name = "bitfount-trial-notes-template"
        return self._get_unique_csv_path(self.path, file_name, task_id)

    def _produce_trial_notes_csv(self, csv_path: Path, task_id: str) -> None:
        """Produce the trial notes CSV file."""
        if self.trial_notes_csv_args is None:
            logger.warning(
                "Trial notes csv was requested, but no arguments "
                "were passed from the protocol. Trial notes "
                "CSV will not be generated "
            )
        else:
            data = self._read_from_csv(csv_path, index_col=False)
            trial_notes_csv_path = self._trial_notes_csv_path(
                task_id, self.trial_notes_csv_args.eligible_only
            )
            df = pd.DataFrame(columns=self.trial_notes_csv_args.columns_for_csv)
            if self.trial_notes_csv_args.eligible_only:
                data = data[data["Eligibility"] == ELIGIBILE_VALUE]

            if self.trial_notes_csv_args.columns_from_data:
                for (
                    new_col,
                    orig_col,
                ) in self.trial_notes_csv_args.columns_from_data.items():
                    df[new_col] = data[orig_col]

            if self.trial_notes_csv_args.columns_to_populate_with_static_values:
                static_vals = (
                    self.trial_notes_csv_args.columns_to_populate_with_static_values
                )
                for col, val in static_vals.items():
                    df[col] = [val] * len(df)

            if len(df) > 0:
                df.drop_duplicates(inplace=True)
                df.fillna("N/A", inplace=True)
                trial_notes_csv_path = self._append_to_csv(
                    trial_notes_csv_path, df.round(decimals=self.decimal_places)
                )
                logger.info(f"Saved trial notes data to {trial_notes_csv_path}")
            else:
                logger.warning(
                    "No eligible patients were found, trial notes CSV "
                    "will not be generated"
                )

    def _get_matched_csv_path(self, csv_path: Path, task_id: str) -> Path:
        """Get the path to save the matched patients CSV to."""
        if self.produce_matched_only:
            return csv_path
        return self._get_unique_csv_path(
            self.matched_csv_path, f"{self.file_name}-matched eyes", task_id
        )

    @staticmethod
    def _get_unique_csv_path(base_path: Path, file_name: str, task_id: str) -> Path:
        """Generate a unique file path for saving a CSV to."""
        if base_path.suffix:
            if base_path.suffix != ".csv":
                logger.warning(
                    f"Supplied save path was not for a CSV file ("
                    f"{base_path}). Saving to this file anyway."
                )
            return base_path
        else:
            base_dir: Path = base_path

        base_dir.mkdir(parents=True, exist_ok=True)

        if base_dir.name != task_id:
            task_id_dir = base_dir / task_id
        else:
            task_id_dir = base_dir
        task_id_dir.mkdir(parents=True, exist_ok=True)
        csv_path = task_id_dir / f"{file_name}.csv"

        return csv_path


def _check_ophth_arg_conflicts(
    ophthalmology_args: Optional[OphthalmologyArgs],
    flat_args: dict[str, Any],
) -> None:
    """Check for conflicts between flat and nested ophthalmology args.

    Raises:
        ValueError: If the same argument is specified both at the top level
            and within ophthalmology_args.
    """
    if ophthalmology_args is None:
        return

    # Create a default instance to get actual default values
    default_instance = OphthalmologyArgs()
    conflicts = []
    for arg_name in _OPHTH_ARG_NAMES:
        flat_value = flat_args.get(arg_name)
        if flat_value is not None:
            nested_value = getattr(ophthalmology_args, arg_name, None)
            default_value = getattr(default_instance, arg_name, None)
            # Check if nested value is non-default
            if nested_value is not None and nested_value != default_value:
                conflicts.append(arg_name)

    if conflicts:
        raise ValueError(
            f"The following arguments were specified both at the top level "
            f"and within ophthalmology_args: {conflicts}. Please specify each "
            f"argument in only one location."
        )


def _emit_flat_ophth_args_deprecation_warning(flat_args: dict[str, Any]) -> None:
    """Emit deprecation warnings for flat ophthalmology arguments."""
    used_flat_args = [
        arg_name for arg_name in _OPHTH_ARG_NAMES if flat_args.get(arg_name) is not None
    ]
    if used_flat_args:
        warnings.warn(
            f"The following ophthalmology-specific arguments are deprecated "
            f"at the top level: {used_flat_args}. Please use the "
            f"`ophthalmology_args` parameter instead.",
            DeprecationWarning,
            stacklevel=3,
        )


class CSVReportAlgorithm(
    BaseNonModelAlgorithmFactory[NoResultsModellerAlgorithm, _WorkerSide]
):
    """Algorithm for generating the CSV results reports.

    This is the unified CSV report algorithm that combines functionality from
    both the original CSVReportAlgorithm and CSVReportGeneratorOphthalmologyAlgorithm.

    Args:
        datastructure: The data structure to use for the algorithm.
        original_cols: The tabular columns from the datasource to include
            in the report. If not specified it will include all tabular columns.
        rename_columns: A dictionary mapping old column names to new names.
        columns_to_drop: A list of column names to exclude from the output.
        columns_to_drop_prefix: A list of prefixes; columns starting with any
            of these prefixes will be dropped from the output.
        columns_to_include: A list of column names to include in the output,
            in the specified order. Columns not in this list are excluded.
            Columns in the list but missing from data are silently skipped.
            Takes precedence over original_cols if both are specified.
        filter: A list of `ColumnFilter` instances for filtering data.
        sorting_columns: A dictionary of columns to sort by (column: 'asc'|'desc').
        decimal_places: Number of decimal places to round to. Defaults to 2.
        ophthalmology_args: Container for ophthalmology-specific options.
        trial_name: (Deprecated) Use ophthalmology_args.trial_name instead.
        aux_cols: (Deprecated) Use ophthalmology_args.aux_cols instead.
        match_patient_visit: (Deprecated) Use ophthalmology_args instead.
        produce_matched_only: (Deprecated) Use ophthalmology_args instead.
        produce_trial_notes_csv: (Deprecated) Use ophthalmology_args instead.
        csv_extensions: (Deprecated) Use ophthalmology_args instead.

    Attributes:
        original_cols: The columns from the datasource to include
            in the report. If not specified it will include all columns.
        rename_columns: A dictionary mapping old column names to new names.
        columns_to_drop: A list of column names to exclude from the output.
        columns_to_drop_prefix: A list of prefixes; columns starting with any
            of these prefixes will be dropped from the output.
        columns_to_include: A list of column names to include in the output,
            in the specified order, including results. Columns not in this list
            are excluded. Columns in the list but missing from data are silently
            skipped. Takes precedence over original_cols if both are specified.
        filter: A list of filters instances for filtering data.
        sorting_columns: A dictionary of columns to sort by (column: 'asc'|'desc').
        decimal_places: Number of decimal places to round to. Defaults to 2.
        ophthalmology_args: Container for ophthalmology-specific options.

    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        # TODO: [BIT-6393] save_path deprecation
        "save_path": fields.Str(),
        "original_cols": fields.List(fields.Str(), allow_none=True),
        "rename_columns": fields.Dict(
            keys=fields.Str(), values=fields.Str(), allow_none=True
        ),
        "columns_to_drop": fields.List(fields.Str(), allow_none=True),
        "columns_to_drop_prefix": fields.List(fields.Str(), allow_none=True),
        "columns_to_include": fields.List(fields.Str(), allow_none=True),
        "filter": fields.Nested(
            desert.schema_class(ColumnFilter), many=True, allow_none=True
        ),
        "sorting_columns": fields.Dict(
            keys=fields.Str(),
            values=fields.Str(validate=validate.OneOf(typing.get_args(DFSortType))),
            allow_none=True,
        ),
        "decimal_places": fields.Int(validate=validate.Range(min=0), load_default=2),
        # Ophthalmology args - both nested and flat (deprecated) formats
        "ophthalmology_args": fields.Nested(
            desert.schema_class(OphthalmologyArgs), allow_none=True
        ),
        # Deprecated flat args for backward compatibility
        "trial_name": fields.Str(allow_none=True),
        "aux_cols": fields.List(fields.Str(), allow_none=True),
        "match_patient_visit": fields.Nested(
            desert.schema_class(MatchPatientVisit), allow_none=True
        ),
        "matched_csv_path": fields.Str(allow_none=True),
        "produce_matched_only": fields.Bool(),
        "produce_trial_notes_csv": fields.Bool(),
        "csv_extensions": fields.List(fields.Str(), allow_none=True),
    }

    def __init__(
        self,
        datastructure: DataStructure,
        # TODO: [BIT-6393] save_path deprecation
        save_path: Optional[Union[str, os.PathLike]] = None,
        original_cols: Optional[list[str]] = None,
        rename_columns: Optional[Mapping[str, str]] = None,
        columns_to_drop: Optional[list[str]] = None,
        columns_to_drop_prefix: Optional[list[str]] = None,
        columns_to_include: Optional[list[str]] = None,
        filter: Optional[list[Union[ColumnFilter, MethodFilter]]] = None,
        sorting_columns: Optional[dict[str, DFSortType]] = None,
        decimal_places: int = 2,
        # Nested ophthalmology args (preferred)
        ophthalmology_args: Optional[OphthalmologyArgs] = None,
        # Flat ophthalmology args (deprecated, for backward compatibility)
        trial_name: Optional[str] = None,
        aux_cols: Optional[list[str]] = None,
        match_patient_visit: Optional[MatchPatientVisit] = None,
        matched_csv_path: Optional[Union[str, os.PathLike]] = None,
        produce_matched_only: bool = True,
        produce_trial_notes_csv: bool = False,
        csv_extensions: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        # Handle save_path deprecation
        if save_path is not None:
            warnings.warn(
                f"The `save_path` argument is deprecated in {type(self).__name__}."
                "Use the BITFOUNT_OUTPUT_DIR,"
                " BITFOUNT_TASK_RESULTS,"
                " or BITFOUNT_PRIMARY_RESULTS_DIR"
                " environment variables instead.",
                DeprecationWarning,
            )
        self.save_path: str = DEPRECATED_STRING

        # Handle matched_csv_path deprecation
        if matched_csv_path is not None:
            warnings.warn(
                f"The `matched_csv_path` argument is deprecated"
                f" in {type(self).__name__}."
                "Use the BITFOUNT_OUTPUT_DIR,"
                " BITFOUNT_TASK_RESULTS,"
                " or BITFOUNT_PRIMARY_RESULTS_DIR"
                " environment variables instead.",
                DeprecationWarning,
            )
        self.matched_csv_path = None

        # Collect flat ophth args for conflict checking
        flat_ophth_args = {
            "trial_name": trial_name,
            "aux_cols": aux_cols,
            "match_patient_visit": match_patient_visit,
            "produce_matched_only": None
            if produce_matched_only
            else produce_matched_only,
            "produce_trial_notes_csv": produce_trial_notes_csv
            if produce_trial_notes_csv
            else None,
            "csv_extensions": csv_extensions,
        }

        # Check for conflicts between flat and nested args
        _check_ophth_arg_conflicts(ophthalmology_args, flat_ophth_args)

        # Emit deprecation warning for flat args
        _emit_flat_ophth_args_deprecation_warning(flat_ophth_args)

        # Merge flat args into ophthalmology_args (flat takes precedence)
        if ophthalmology_args is None:
            ophthalmology_args = OphthalmologyArgs()

        # Apply flat args if specified (backward compatibility)
        if trial_name is not None:
            ophthalmology_args.trial_name = trial_name
        if aux_cols is not None:
            ophthalmology_args.aux_cols = aux_cols
        if match_patient_visit is not None:
            ophthalmology_args.match_patient_visit = match_patient_visit
        if not produce_matched_only:
            ophthalmology_args.produce_matched_only = produce_matched_only
        if produce_trial_notes_csv:
            ophthalmology_args.produce_trial_notes_csv = produce_trial_notes_csv
        if csv_extensions is not None:
            ophthalmology_args.csv_extensions = csv_extensions

        # Store attributes
        self.original_cols = original_cols
        self.rename_columns = dict(rename_columns) if rename_columns else None
        self.columns_to_drop = columns_to_drop
        self.columns_to_drop_prefix = columns_to_drop_prefix
        self.columns_to_include = columns_to_include
        self.filter = filter
        self.sorting_columns = sorting_columns
        self.decimal_places = decimal_places
        self.ophthalmology_args = ophthalmology_args

        super().__init__(datastructure=datastructure, **kwargs)

    def modeller(
        self,
        *,
        context: ProtocolContext,
        **kwargs: Any,
    ) -> NoResultsModellerAlgorithm:
        """Modeller-side of the algorithm."""
        task_results_dir = get_task_results_directory(context)

        return NoResultsModellerAlgorithm(
            log_message="CSV saved to the pod.",
            save_path=task_results_dir,
            **kwargs,
        )

    def worker(
        self,
        *,
        context: ProtocolContext,
        **kwargs: Any,
    ) -> _WorkerSide:
        """Worker-side of the algorithm."""
        task_results_dir = get_task_results_directory(context)

        # Extract ophthalmology args
        ophth = self.ophthalmology_args or OphthalmologyArgs()

        return _WorkerSide(
            path=task_results_dir,
            original_cols=self.original_cols,
            rename_columns=self.rename_columns,
            columns_to_drop=self.columns_to_drop,
            columns_to_drop_prefix=self.columns_to_drop_prefix,
            columns_to_include=self.columns_to_include,
            filter=self.filter,
            sorting_columns=self.sorting_columns,
            decimal_places=self.decimal_places,
            # Ophthalmology args
            trial_name=ophth.trial_name,
            aux_cols=ophth.aux_cols,
            matcher=ophth.match_patient_visit,
            matched_csv_path=task_results_dir,
            produce_matched_only=ophth.produce_matched_only,
            csv_extensions=ophth.csv_extensions,
            produce_trial_notes_csv=ophth.produce_trial_notes_csv,
            **kwargs,
        )
