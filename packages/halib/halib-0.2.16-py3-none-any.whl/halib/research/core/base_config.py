import os
from rich.pretty import pprint
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


class NamedConfig(ABC):
    """
    Base class for named configurations.
    All configurations should have a name.
    """

    @abstractmethod
    def get_name(self):
        """
        Get the name of the configuration.
        This method should be implemented in subclasses.
        """
        pass


@dataclass
class AutoNamedConfig(YAMLWizard, NamedConfig):
    """
    Mixin that automatically implements get_name() by returning self.name.
    Classes using this MUST have a 'name' field.
    """

    name: Optional[str] = None

    def get_name(self):
        return self.name

    def __post_init__(self):
        # Enforce the "MUST" rule here
        if self.name is None:
            # We allow None during initial load, but it must be set before usage
            # or handled by the loader.
            pass

T = TypeVar("T", bound=AutoNamedConfig)

class BaseSelectorConfig(Generic[T]):
    """
    Base class to handle the logic of selecting an item from a list by name.
    """

    def _resolve_selection(self, items: List[T], selected_name: str, context: str) -> T:
        if selected_name is None:
            raise ValueError(f"No {context} selected in the configuration.")

        # Create a lookup dict for O(1) access, or just iterate if list is short
        for item in items:
            if item.name == selected_name:
                return item

        raise ValueError(
            f"{context.capitalize()} '{selected_name}' not found in the configuration list."
        )


class ExpBaseConfig(ABC, YAMLWizard):
    """
    Base class for configuration objects.
    What a cfg class must have:
    1 - a dataset cfg
    2 - a metric cfg
    3 - a method cfg
    """

    # Save to yaml fil
    def save_to_outdir(
        self, filename: str = "__config.yaml", outdir=None, override: bool = False
    ) -> None:
        """
        Save the configuration to the output directory.
        """
        if outdir is not None:
            output_dir = outdir
        else:
            output_dir = self.get_outdir()
        os.makedirs(output_dir, exist_ok=True)
        assert (output_dir is not None) and (
            os.path.isdir(output_dir)
        ), f"Output directory '{output_dir}' does not exist or is not a directory."
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path) and not override:
            pprint(
                f"File '{file_path}' already exists. Use 'override=True' to overwrite."
            )
        else:
            # method of YAMLWizard to_yaml_file
            self.to_yaml_file(file_path)

    @classmethod
    @abstractmethod
    # load from a custom YAML file
    def from_custom_yaml_file(cls, yaml_file: str):
        """Load a configuration from a custom YAML file."""
        pass

    @abstractmethod
    def get_cfg_name(self):
        """
        Get the name of the configuration.
        This method should be implemented in subclasses.
        """
        pass

    @abstractmethod
    def get_outdir(self):
        """
        Get the output directory for the configuration.
        This method should be implemented in subclasses.
        """
        return None

    @abstractmethod
    def get_general_cfg(self):
        """
        Get the general configuration like output directory, log settings, SEED, etc.
        This method should be implemented in subclasses.
        """
        pass

    @abstractmethod
    def get_dataset_cfg(self) -> NamedConfig:
        """
        Get the dataset configuration.
        This method should be implemented in subclasses.
        """
        pass

    @abstractmethod
    def get_metric_cfg(self) -> NamedConfig:
        """
        Get the metric configuration.
        This method should be implemented in subclasses.
        """
        pass
