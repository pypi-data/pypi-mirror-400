"""MUV (Maximum Unbiased Validation) dataset implementation.

This module provides functionality for downloading and managing the MUV dataset,
which contains 17 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in Parquet format and splits
are provided as NumPy arrays.
"""

import pathlib
from typing import Optional, Union

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class MUVDownloader(DatasetDownloader):
    """Downloader for the MUV dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the MUV dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the MUV dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "MUV-466",
            "MUV-548",
            "MUV-600",
            "MUV-644",
            "MUV-652",
            "MUV-689",
            "MUV-692",
            "MUV-712",
            "MUV-713",
            "MUV-733",
            "MUV-737",
            "MUV-810",
            "MUV-832",
            "MUV-846",
            "MUV-852",
            "MUV-858",
            "MUV-859",
        ]
        return DatasetMetadata(
            name="MUV",
            description="Maximum Unbiased Validation (MUV) dataset for virtual screening",
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                "Ramsundar, Bharath, et al. Massively multitask networks for drug discovery arXiv:1502.02072 (2015) https://arxiv.org/abs/1502.02072"
            ),
            file_format="parquet",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="muv",
        )

