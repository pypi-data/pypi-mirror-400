from abc import ABC, abstractmethod
from typing import Tuple, Any, Optional
from base_config import ExpBaseConfig
from ..perf.perfcalc import PerfCalc
from ..perf.perfmetrics import MetricsBackend

# ! SEE https://github.com/hahv/base_exp for sample usage
class BaseExperiment(PerfCalc, ABC):
    """
    Base class for experiments.
    Orchestrates the experiment pipeline using a pluggable metrics backend.
    """

    def __init__(self, config: ExpBaseConfig):
        self.config = config
        self.metric_backend = None
        # Flag to track if init_general/prepare_dataset has run
        self._is_env_ready = False

    # -----------------------
    # PerfCalc Required Methods
    # -----------------------
    def get_dataset_name(self):
        return self.config.get_dataset_cfg().get_name()

    def get_experiment_name(self):
        return self.config.get_cfg_name()

    def get_metric_backend(self):
        if not self.metric_backend:
            self.metric_backend = self.prepare_metrics(self.config.get_metric_cfg())
        return self.metric_backend

    # -----------------------
    # Abstract Experiment Steps
    # -----------------------
    @abstractmethod
    def init_general(self, general_cfg):
        """Setup general settings like SEED, logging, env variables."""
        pass

    @abstractmethod
    def prepare_dataset(self, dataset_cfg):
        """Load/prepare dataset."""
        pass

    @abstractmethod
    def prepare_metrics(self, metric_cfg) -> MetricsBackend:
        """
        Prepare the metrics for the experiment.
        This method should be implemented in subclasses.
        """
        pass

    @abstractmethod
    def before_exec_exp_once(self, *args, **kwargs):
        """Optional: any setup before exec_exp. Note this is called once per run_exp."""
        pass

    @abstractmethod
    def exec_exp(self, *args, **kwargs) -> Optional[Tuple[Any, Any]]:
        """Run experiment process, e.g.: training/evaluation loop.
        Return: either `None` or a tuple of (raw_metrics_data, extra_data) for calc_and_save_exp_perfs
        """
        pass

    @abstractmethod
    def exec_eval(self, *args, **kwargs) -> Optional[Tuple[Any, Any]]:
        """Run evaluation process.
        Return: either `None` or a tuple of (raw_metrics_data, extra_data) for calc_and_save_exp_perfs
        """
        pass

    # -----------------------
    # Internal Helpers
    # -----------------------
    def _validate_and_unpack(self, results):
        if results is None:
            return None
        if not isinstance(results, (tuple, list)) or len(results) != 2:
            raise ValueError("exec must return (metrics_data, extra_data)")
        return results[0], results[1]

    def _prepare_environment(self, force_reload: bool = False):
        """
        Common setup. Skips if already initialized, unless force_reload is True.
        """
        if self._is_env_ready and not force_reload:
            # Environment is already prepared, skipping setup.
            return

        # 1. Run Setup
        self.init_general(self.config.get_general_cfg())
        self.prepare_dataset(self.config.get_dataset_cfg())

        # 2. Update metric backend (refresh if needed)
        self.metric_backend = self.prepare_metrics(self.config.get_metric_cfg())

        # 3. Mark as ready
        self._is_env_ready = True

    # -----------------------
    # Main Experiment Runner
    # -----------------------
    def run_exp(self, should_calc_metrics=True, reload_env=False, *args, **kwargs):
        """
        Run the whole experiment pipeline.
        :param reload_env: If True, forces dataset/general init to run again.
        :param should_calc_metrics: Whether to calculate and save metrics after execution.
        :kwargs Params:
            + 'outfile' to save csv file results,
            + 'outdir' to set output directory for experiment results.
            + 'return_df' to return a DataFrame of results instead of a dictionary.

        Full pipeline:
            1. Init
            2. Prepare Environment (General + Dataset + Metrics)
            3. Save Config
            4. Execute
            5. Calculate & Save Metrics
        """
        self._prepare_environment(force_reload=reload_env)

        # Any pre-exec setup (loading models, etc)
        self.before_exec_exp_once(*args, **kwargs)
        # Save config before running
        self.config.save_to_outdir()

        # Execute experiment
        results = self.exec_exp(*args, **kwargs)

        if should_calc_metrics and results is not None:
            metrics_data, extra_data = self._validate_and_unpack(results)
            # Calculate & Save metrics
            perf_results = self.calc_perfs(
                raw_metrics_data=metrics_data, extra_data=extra_data, *args, **kwargs
            )
            return perf_results
        else:
            return results

    # -----------------------
    # Main Experiment Evaluator
    # -----------------------
    def eval_exp(self, reload_env=False, *args, **kwargs):
        """
        Run evaluation only.
        :param reload_env: If True, forces dataset/general init to run again.
        """
        self._prepare_environment(force_reload=reload_env)
        results = self.exec_eval(*args, **kwargs)
        if results is not None:
            metrics_data, extra_data = self._validate_and_unpack(results)
            return self.calc_perfs(
                raw_metrics_data=metrics_data, extra_data=extra_data, *args, **kwargs
            )
        return None
