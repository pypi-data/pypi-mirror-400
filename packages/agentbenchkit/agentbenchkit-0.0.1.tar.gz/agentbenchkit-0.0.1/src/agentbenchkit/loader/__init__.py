import importlib
import logging
from pathlib import Path
from typing import Dict,Type
from .base import BaseDatasetLoader
from agentbenchkit.core.utils import ConfigManager

logger = logging.getLogger(__name__)
_LOADER_REGISTRY: Dict[str, Type[BaseDatasetLoader]] = {}
_config_manager = ConfigManager()

def print_benchmark_metadata(benchmark_name: str):
    meta_data = _config_manager.get_metadata(benchmark_name)
    print(f"Benchmark name: {meta_data['Dataset']}")
    print(f"Benchmark type: {meta_data['Type']}")
    print(f"Default evaluator: {meta_data['evaluator']}")
    print(f"Benchmark link: {meta_data['Url']}")


def register_loader(name: str):
    def inner(cls: Type[BaseDatasetLoader]):
        if name in _LOADER_REGISTRY:
            raise ValueError(f"Dataset loader {name} is already registered.")
        _LOADER_REGISTRY[name] = cls
        return cls
    return inner

def get_dataset_loader(name: str) -> BaseDatasetLoader:
    """
    Factory function to get the specified dataset loader.
    """
    if name not in _LOADER_REGISTRY:
        available = list(_LOADER_REGISTRY.keys())
        raise ValueError(f"Dataset loader {name} is not registered.Available:{available}")
    logger.info(f"Instantiating dataset loader {name}")
    return _LOADER_REGISTRY[name]()

def print_dataset_loaders():
    """Print a sorted list of all registered dataset loader names."""
    print(sorted(_LOADER_REGISTRY.keys()))

def _auto_import_loaders():
    package_dir = Path(__file__).parent
    loaders_dir = package_dir

    if not loaders_dir.exists():
        logger.info(f"No loader directory found at {loaders_dir}.")
        return

    for file_path in loaders_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        module_name = file_path.stem
        full_module_name = f"{__package__}.{module_name}"

        try:
            importlib.import_module(full_module_name)
        except Exception as e:
            logging.warning(f"Failed to import loader module {full_module_name}: {e}")

_auto_import_loaders()

__all__ = ["get_dataset_loader", "BaseDatasetLoader", "register_loader", "print_dataset_loaders", "print_benchmark_metadata"]
