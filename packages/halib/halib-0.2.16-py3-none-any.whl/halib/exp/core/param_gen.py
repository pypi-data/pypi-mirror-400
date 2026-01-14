import os
import yaml
import numpy as np
from typing import Dict, Any, List

from ...common.common import *
from ...filetype import yamlfile
from itertools import product
import copy


"""
Parameter Generation Pipeline

1. Expand Values (_build):
   Parses the YAML file and expands value generators (like ranges) into lists.

   Example:
     Input:  {"p1": {"type": "range", "values": [1, 4, 1]}, "p2": {"values": ["a", "b"]}}
     Output: {"p1": [1, 2, 3], "p2": ["a", "b"]}

2. Generate Combinations (_build_combinations):
   Creates a Cartesian product (grid) of all parameter lists.

   Example:
     Input:  {"p1": [1, 2], "p2": ["a", "b"]}
     Output: [{"p1": 1, "p2": "a"}, {"p1": 1, "p2": "b"}, ...]
3. Expand Configs (expand):
   Merges each parameter combination into a base configuration using a user-defined function.
   Example:
        Input:  base_cfg, [{"p1": 1, "p2": "a"}, {"p1": 1, "p2": "b"}, ...], update_fn
        Output: [cfg1, cfg2, ...] where each cfg has parameters from the combinations applied.
"""

class ParamGen:
    @staticmethod
    def from_file(params_file):
        builder = ParamGen(params_file)
        return builder

    @staticmethod
    def expand(
        base_cfg: Dict[str, Any],
        combination_list: List[Dict[str, Any]],
        update_base_cfg_fn: callable,
    ):
        cfg_ls = []
        for combination in combination_list:
            cfg = copy.deepcopy(base_cfg)
            update_base_cfg_fn(cfg, combination)
            cfg_ls.append(cfg)
        return cfg_ls

    @staticmethod
    def expand_from_file(
        base_cfg: Dict[str, Any],
        params_file: str,
        update_base_cfg_fn: callable):
        param_gen = ParamGen.from_file(params_file)
        return ParamGen.expand(
            base_cfg, param_gen.combinations, update_base_cfg_fn
        )

    def __init__(self, params_file=None):
        self.params = {}
        assert os.path.isfile(params_file), f"params_file not found: {params_file}"
        self.params = self._build_param_dict(params_file)
        self.combinations = self._build_combinations(self.params)

    def _expand_param(self, param_name: str, config: Dict[str, Any]) -> List[Any]:
        """
        Validates and expands the values for a single parameter configuration.

        Args:
            param_name: The name of the parameter being processed.
            config: The configuration dictionary for this parameter.

        Returns:
            A list of the expanded values for the parameter.

        Raises:
            TypeError: If the configuration or its values have an incorrect type.
            ValueError: If the configuration is missing keys or has an invalid structure.
        """
        # 1. Validate the configuration structure
        if not isinstance(config, dict):
            raise TypeError(f"Config for '{param_name}' must be a dictionary.")

        if "type" not in config or "values" not in config:
            raise ValueError(
                f"Config for '{param_name}' must contain 'type' and 'values' keys."
            )

        gen_type = config["type"]
        values = config["values"]

        # 2. Handle the generation based on type
        if gen_type == "list":
            # Ensure values are returned as a list, even if a single item was provided
            return values if isinstance(values, list) else [values]

        elif gen_type == "range":
            if not isinstance(values, list) or len(values) != 3:
                raise ValueError(
                    f"For 'range' type on '{param_name}', 'values' must be a list of 3 numbers "
                    f"[start, end, step], but got: {values}"
                )

            start, end, step = values
            if all(isinstance(v, int) for v in values):
                return list(range(start, end, step))
            elif all(isinstance(v, (int, float)) for v in values):
                # Use numpy for floating point ranges
                temp_list = list(np.arange(start, end, step))
                # convert to float (not np.float)
                return [float(v) for v in temp_list]
            else:
                raise TypeError(
                    f"All 'values' for 'range' on '{param_name}' must be numbers."
                )

        else:
            raise ValueError(
                f"Invalid 'type' for '{param_name}': '{gen_type}'. Must be 'list' or 'range'."
            )

    def _build_param_dict(self, params_file):
        """
        Builds a full optimization configuration by expanding parameter values based on their type.

        This function processes a dictionary where each key is a parameter name and each value
        is a config dict specifying the 'type' ('list' or 'range') and 'values' for generation.

        Args:
            opt_cfg: The input configuration dictionary.
                    Example:
                    {
                        "learning_rate": {"type": "range", "values": [0.01, 0.1, 0.01]},
                        "optimizer": {"type": "list", "values": ["adam", "sgd"]},
                        "epochs": {"type": "list", "values": 100}
                    }

        Returns:
            A dictionary with parameter names mapped to their fully expanded list of values.
        """
        cfg_raw_dict = yamlfile.load_yaml(params_file, to_dict=True)
        if not isinstance(cfg_raw_dict, dict):
            raise TypeError("The entire opt_cfg must be a dictionary.")

        # Use a dictionary comprehension for a clean and efficient build
        return {
            param_name: self._expand_param(param_name, config)
            for param_name, config in cfg_raw_dict.items()
        }
    def _build_combinations(self, params_dict: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generates all combinations of parameters from the provided parameter dictionary.

        Args:
            params_dict: A dictionary where each key is a parameter name and each value is a list of possible values.
        Returns:
            A list of dictionaries, each representing a unique combination of parameters.
        """

        # Extract parameter names and their corresponding lists of values
        param_names = list(params_dict.keys())
        param_values = [params_dict[name] for name in param_names]

        # Generate all combinations using Cartesian product
        all_combinations = product(*param_values)

        # Convert each combination tuple into a dictionary
        combinations_list = [
            dict(zip(param_names, combination)) for combination in all_combinations
        ]

        return combinations_list

    def save(self, outfile):
        with open(outfile, "w") as f:
            yaml.dump(self.params, f)
