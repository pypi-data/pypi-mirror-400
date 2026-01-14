"""Dataset registry implementation for Litmus.

This module provides a registry for managing available datasets
and their downloaders.
"""

from typing import Dict, Type

from litmus.datasets.downloader import DatasetDownloader
from litmus.datasets.dudad import DUDADDownloader
from litmus.datasets.lit_pcba import LITPCBADownloader
from litmus.datasets.muv import MUVDownloader
from litmus.datasets.welqrate import WelQrateDownloader


class DatasetRegistry:
    """Registry for managing available datasets."""

    def __init__(self):
        """Initialize the dataset registry."""
        self._downloaders: Dict[str, Type[DatasetDownloader]] = {}

    def register(self, downloader_class: Type[DatasetDownloader]) -> None:
        """Register a dataset downloader.

        Parameters
        ----------
        downloader_class : Type[DatasetDownloader]
            The downloader class to register.
        """
        downloader = downloader_class()
        self._downloaders[downloader.metadata.name] = downloader_class

    def get_downloader(self, name: str) -> DatasetDownloader:
        """Get a downloader instance for a dataset.

        Parameters
        ----------
        name : str
            Name of the dataset.

        Returns
        -------
        DatasetDownloader
            DatasetDownloader instance for the requested dataset.
        """
        if name not in self._downloaders:
            raise KeyError(
                f"Dataset '{name}' not found. Available datasets: {list(self._downloaders.keys())}"
            )
        return self._downloaders[name]()

    def list_datasets(self) -> list[str]:
        """List all available datasets.

        Returns
        -------
        list[str]
            List of available dataset names.
        """
        return list(self._downloaders.keys())


# Global registry instance
registry = DatasetRegistry()
registry.register(MUVDownloader)
registry.register(LITPCBADownloader)
registry.register(WelQrateDownloader)
registry.register(DUDADDownloader)
