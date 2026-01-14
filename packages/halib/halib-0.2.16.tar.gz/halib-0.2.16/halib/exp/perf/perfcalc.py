import os
import glob
from typing import Optional, Tuple
import pandas as pd

from abc import ABC, abstractmethod
from collections import OrderedDict


from ...common.common import now_str
from ...system import filesys as fs

from .perftb import PerfTB
from .perfmetrics import *


REQUIRED_COLS = ["experiment", "dataset"]
CSV_FILE_POSTFIX = "__perf"
METRIC_PREFIX = "metric_"


class PerfCalc(ABC):  # Abstract base class for performance calculation
    @abstractmethod
    def get_experiment_name(self) -> str:
        """
        Return the name of the experiment.
        This function should be overridden by the subclass if needed.
        """
        pass

    @abstractmethod
    def get_dataset_name(self) -> str:
        """
        Return the name of the dataset.
        This function should be overridden by the subclass if needed.
        """
        pass

    @abstractmethod
    def get_metric_backend(self) -> MetricsBackend:
        """
        Return a list of metric names to be used for performance calculation OR a dictionaray with keys as metric names and values as metric instances of torchmetrics.Metric. For example: {"accuracy": Accuracy(), "precision": Precision()}

        """
        pass

    def valid_proc_extra_data(self, proc_extra_data):
        # make sure that all items in proc_extra_data are dictionaries, with same keys
        if proc_extra_data is None or len(proc_extra_data) == 0:
            return
        if not all(isinstance(item, dict) for item in proc_extra_data):
            raise TypeError("All items in proc_extra_data must be dictionaries")

        if not all(
            item.keys() == proc_extra_data[0].keys() for item in proc_extra_data
        ):
            raise ValueError(
                "All dictionaries in proc_extra_data must have the same keys"
            )

    def valid_proc_metric_raw_data(self, metric_names, proc_metric_raw_data):
        # make sure that all items in proc_metric_raw_data are dictionaries, with same keys as metric_names
        assert (
            isinstance(proc_metric_raw_data, list) and len(proc_metric_raw_data) > 0
        ), "raw_data_for_metrics must be a non-empty list of dictionaries"

        # make sure that all items in proc_metric_raw_data are dictionaries with keys as metric_names
        if not all(isinstance(item, dict) for item in proc_metric_raw_data):
            raise TypeError("All items in raw_data_for_metrics must be dictionaries")
        if not all(
            set(item.keys()) == set(metric_names) for item in proc_metric_raw_data
        ):
            raise ValueError(
                "All dictionaries in raw_data_for_metrics must have the same keys as metric_names"
            )

    # =========================================================================
    # 1. Formatting Logic (Decoupled)
    # =========================================================================
    def package_metrics(
        self,
        metric_results_list: List[dict],
        extra_data_list: Optional[List[dict]] = None,
    ) -> List[OrderedDict]:
        """
        Pure formatting function.
        Takes ALREADY CALCULATED metrics and formats them
        (adds metadata, prefixes keys, ensures column order).
        """
        # Normalize extra_data to a list if provided
        if extra_data_list is None:
            extra_data_list = [{} for _ in range(len(metric_results_list))]
        elif isinstance(extra_data_list, dict):
            extra_data_list = [extra_data_list]

        assert len(extra_data_list) == len(
            metric_results_list
        ), "Length mismatch: metrics vs extra_data"

        proc_outdict_list = []

        for metric_res, extra_item in zip(metric_results_list, extra_data_list):
            # A. Base Metadata
            out_dict = {
                "dataset": self.get_dataset_name(),
                "experiment": self.get_experiment_name(),
            }

            # B. Attach Extra Data
            out_dict.update(extra_item)
            custom_fields = list(extra_item.keys())

            # C. Prefix Metric Keys (e.g., 'acc' -> 'metric_acc')
            metric_results_prefixed = {f"metric_{k}": v for k, v in metric_res.items()}
            out_dict.update(metric_results_prefixed)

            # D. Order Columns
            all_cols = (
                REQUIRED_COLS + custom_fields + list(metric_results_prefixed.keys())
            )
            ordered_out = OrderedDict(
                (col, out_dict[col]) for col in all_cols if col in out_dict
            )
            proc_outdict_list.append(ordered_out)

        return proc_outdict_list

    # =========================================================================
    # 2. Calculation Logic (The Coordinator)
    # =========================================================================
    def calc_exp_perf_metrics(
        self,
        metric_names: List[str],
        raw_metrics_data: Union[List[dict], dict],
        extra_data: Optional[Union[List[dict], dict]] = None,
        *args,
        **kwargs,
    ) -> List[OrderedDict]:
        """
        Full workflow: Validates raw data -> Calculates via Backend -> Packages results.
        """
        # Prepare Raw Data
        raw_data_ls = (
            raw_metrics_data
            if isinstance(raw_metrics_data, list)
            else [raw_metrics_data]
        )
        self.valid_proc_metric_raw_data(metric_names, raw_data_ls)

        # Prepare Extra Data (Validation only)
        extra_data_ls = None
        if extra_data:
            extra_data_ls = extra_data if isinstance(extra_data, list) else [extra_data]
            self.valid_proc_extra_data(extra_data_ls)

        # Calculate Metrics via Backend
        metrics_backend = self.get_metric_backend()
        calculated_results = []

        for data_item in raw_data_ls:
            res = metrics_backend.calc_metrics(
                metrics_data_dict=data_item, *args, **kwargs
            )
            calculated_results.append(res)

        # Delegate to Formatting
        return self.package_metrics(calculated_results, extra_data_ls)

    # =========================================================================
    # 3. File Saving Logic (Decoupled)
    # =========================================================================
    def save_results_to_csv(
        self, out_dict_list: List[OrderedDict], **kwargs
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Helper function to convert results to DataFrame and save to CSV.
        """
        csv_outfile = kwargs.get("outfile", None)

        # Determine Output Path
        if csv_outfile is not None:
            filePathNoExt, _ = os.path.splitext(csv_outfile)
            csv_outfile = f"{filePathNoExt}{CSV_FILE_POSTFIX}.csv"
        elif "outdir" in kwargs:
            csvoutdir = kwargs["outdir"]
            csvfilename = f"{now_str()}_{self.get_dataset_name()}_{self.get_experiment_name()}_{CSV_FILE_POSTFIX}.csv"
            csv_outfile = os.path.join(csvoutdir, csvfilename)

        # Convert to DataFrame
        df = pd.DataFrame(out_dict_list)
        if out_dict_list:
            ordered_cols = list(out_dict_list[0].keys())
            df = df[ordered_cols]

        # Save to File
        if csv_outfile:
            df.to_csv(csv_outfile, index=False, sep=";", encoding="utf-8")

        return df, csv_outfile

    # =========================================================================
    # 4. Public API: Standard Calculation
    # raw_metrics_data: example: [{"preds": ..., "target": ...}, ...]
    # =========================================================================
    def calc_perfs(
        self,
        raw_metrics_data: Union[List[dict], dict],
        extra_data: Optional[Union[List[dict], dict]] = None,
        *args,
        **kwargs,
    ) -> Tuple[Union[List[OrderedDict], pd.DataFrame], Optional[str]]:
        """
        Standard use case: Calculate metrics AND save to CSV.
        """
        metric_names = self.get_metric_backend().metric_names

        # 1. Calculate & Package
        out_dict_list = self.calc_exp_perf_metrics(
            metric_names=metric_names,
            raw_metrics_data=raw_metrics_data,
            extra_data=extra_data,
            *args,
            **kwargs,
        )

        # 2. Save
        df, csv_outfile = self.save_results_to_csv(out_dict_list, **kwargs)

        return (
            (df, csv_outfile)
            if kwargs.get("return_df", False)
            else (out_dict_list, csv_outfile)
        )

    # =========================================================================
    # 5. Public API: Manual / External Metrics (The Shortcut)
    # =========================================================================
    def save_computed_perfs(
        self,
        metrics_data: Union[List[dict], dict],
        extra_data: Optional[Union[List[dict], dict]] = None,
        **kwargs,
    ) -> Tuple[Union[List[OrderedDict], pd.DataFrame], Optional[str]]:

        # Ensure list format
        if isinstance(metrics_data, dict):
            metrics_data = [metrics_data]
        if isinstance(extra_data, dict):
            extra_data = [extra_data]

        # 1. Package (Format)
        formatted_list = self.package_metrics(metrics_data, extra_data)

        # 2. Save
        df, csv_outfile = self.save_results_to_csv(formatted_list, **kwargs)

        return (
            (df, csv_outfile)
            if kwargs.get("return_df", False)
            else (formatted_list, csv_outfile)
        )

    @staticmethod
    def default_exp_csv_filter_fn(exp_file_name: str) -> bool:
        """
        Default filter function for experiments.
        Returns True if the experiment name does not start with "test_" or "debug_".
        """
        return "__perf.csv" in exp_file_name

    @classmethod
    def get_perftb_for_multi_exps(
        cls,
        indir: str,
        exp_csv_filter_fn=default_exp_csv_filter_fn,
        include_file_name=False,
        csv_sep=";",
    ) -> PerfTB:
        """
        Generate a performance report by scanning experiment subdirectories.
        Must return a dictionary with keys as metric names and values as performance tables.
        """

        def get_df_for_all_exp_perf(csv_perf_files, csv_sep=";"):
            """
            Create a single DataFrame from all CSV files.
            Assumes all CSV files MAY have different metrics
            """
            cols = []
            FILE_NAME_COL = "file_name" if include_file_name else None

            for csv_file in csv_perf_files:
                temp_df = pd.read_csv(csv_file, sep=csv_sep)
                if FILE_NAME_COL:
                    temp_df[FILE_NAME_COL] = fs.get_file_name(
                        csv_file, split_file_ext=False
                    )
                    # csvfile.fn_display_df(temp_df)
                temp_df_cols = temp_df.columns.tolist()
                for col in temp_df_cols:
                    if col not in cols:
                        cols.append(col)

            df = pd.DataFrame(columns=cols)
            for csv_file in csv_perf_files:
                temp_df = pd.read_csv(csv_file, sep=csv_sep)
                if FILE_NAME_COL:
                    temp_df[FILE_NAME_COL] = fs.get_file_name(
                        csv_file, split_file_ext=False
                    )
                # Drop all-NA columns to avoid dtype inconsistency
                temp_df = temp_df.dropna(axis=1, how="all")
                # ensure all columns are present in the final DataFrame
                for col in cols:
                    if col not in temp_df.columns:
                        temp_df[col] = None  # fill missing columns with None
                df = pd.concat([df, temp_df], ignore_index=True)
            # assert that REQUIRED_COLS are present in the DataFrame
            # pprint(df.columns.tolist())
            sticky_cols = REQUIRED_COLS + (
                [FILE_NAME_COL] if include_file_name else []
            )  # columns that must always be present
            for col in sticky_cols:
                if col not in df.columns:
                    raise ValueError(
                        f"Required column '{col}' is missing from the DataFrame. REQUIRED_COLS = {sticky_cols}"
                    )
            metric_cols = [col for col in df.columns if col.startswith(METRIC_PREFIX)]
            assert (
                len(metric_cols) > 0
            ), "No metric columns found in the DataFrame. Ensure that the CSV files contain metric columns starting with 'metric_'."
            final_cols = sticky_cols + metric_cols
            df = df[final_cols]
            # # !hahv debug
            # pprint("------ Final DataFrame Columns ------")
            # csvfile.fn_display_df(df)
            # ! validate all rows in df before returning
            # make sure all rows will have at least values for REQUIRED_COLS and at least one metric column
            for index, row in df.iterrows():
                if not all(col in row and pd.notna(row[col]) for col in sticky_cols):
                    raise ValueError(
                        f"Row {index} is missing required columns or has NaN values in required columns: {row}"
                    )
                if not any(pd.notna(row[col]) for col in metric_cols):
                    raise ValueError(f"Row {index} has no metric values: {row}")
            # make sure these is no (experiment, dataset) pair that is duplicated
            duplicates = df.duplicated(subset=sticky_cols, keep=False)
            if duplicates.any():
                raise ValueError(
                    "Duplicate (experiment, dataset) pairs found in the DataFrame. Please ensure that each experiment-dataset combination is unique."
                )
            return df

        def mk_perftb_report(df):
            """
            Create a performance report table from the DataFrame.
            This function should be customized based on the specific requirements of the report.
            """
            perftb = PerfTB()
            # find all "dataset" values (unique)
            dataset_names = list(df["dataset"].unique())
            # find all columns that start with METRIC_PREFIX
            metric_cols = [col for col in df.columns if col.startswith(METRIC_PREFIX)]

            # Determine which metrics are associated with each dataset.
            # Since a dataset may appear in multiple rows and may not include all metrics in each, identify the row with the same dataset that contains the most non-NaN metric values. The set of metrics for that dataset is defined by the non-NaN metrics in that row.

            dataset_metrics = {}
            for dataset_name in dataset_names:
                dataset_rows = df[df["dataset"] == dataset_name]
                # Find the row with the most non-NaN metric values
                max_non_nan_row = dataset_rows[metric_cols].count(axis=1).idxmax()
                metrics_for_dataset = (
                    dataset_rows.loc[max_non_nan_row, metric_cols]
                    .dropna()
                    .index.tolist()
                )
                dataset_metrics[dataset_name] = metrics_for_dataset

            for dataset_name, metrics in dataset_metrics.items():
                # Create a new row for the performance table
                perftb.add_dataset(dataset_name, metrics)

            for _, row in df.iterrows():
                dataset_name = row["dataset"]
                ds_metrics = dataset_metrics.get(dataset_name)
                if dataset_name in dataset_metrics:
                    # Add the metrics for this row to the performance table
                    exp_name = row.get("experiment")
                    exp_metric_values = {}
                    for metric in ds_metrics:
                        if metric in row and pd.notna(row[metric]):
                            exp_metric_values[metric] = row[metric]
                    perftb.add_experiment(
                        experiment_name=exp_name,
                        dataset_name=dataset_name,
                        metrics=exp_metric_values,
                    )

            return perftb

        assert os.path.exists(indir), f"Input directory {indir} does not exist."

        csv_perf_files = []
        # Find experiment subdirectories
        exp_dirs = [
            os.path.join(indir, d)
            for d in os.listdir(indir)
            if os.path.isdir(os.path.join(indir, d))
        ]
        if len(exp_dirs) == 0:
            csv_perf_files = glob.glob(os.path.join(indir, f"*.csv"))
            csv_perf_files = [
                file_item
                for file_item in csv_perf_files
                if exp_csv_filter_fn(file_item)
            ]
        else:
            # multiple experiment directories found
            # Collect all matching CSV files in those subdirs
            for exp_dir in exp_dirs:
                # pprint(f"Searching in experiment directory: {exp_dir}")
                matched = glob.glob(os.path.join(exp_dir, f"*.csv"))
                matched = [
                    file_item for file_item in matched if exp_csv_filter_fn(file_item)
                ]
                csv_perf_files.extend(matched)

        assert (
            len(csv_perf_files) > 0
        ), f"No CSV files matching pattern '{exp_csv_filter_fn}' found in the experiment directories."

        assert (
            len(csv_perf_files) > 0
        ), f"No CSV files matching pattern '{exp_csv_filter_fn}' found in the experiment directories."

        all_exp_perf_df = get_df_for_all_exp_perf(csv_perf_files, csv_sep=csv_sep)
        # csvfile.fn_display_df(all_exp_perf_df)
        perf_tb = mk_perftb_report(all_exp_perf_df)
        return perf_tb
