"""WELQRATE dataset implementation.

This module provides functionality for downloading and managing the WELQRATE dataset,
which contains 9 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in Parquet format and splits
are provided as NumPy arrays. WELQRATE has 5 different seeds (1-5) for cross-validation,
with split files named as seed{1-5}_WELQRATE_{target}.{train|test}_idx.npy.
"""

import pathlib
from typing import Dict, List, Optional, Union


import numpy as np

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class WelQrateDownloader(DatasetDownloader):
    """Downloader for the Wel Qrate dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the Wel Qrate dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the Wel Qrate dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "AID1798",
            "AID1843",
            "AID2258",
            "AID2689",
            "AID435008",
            "AID435034",
            "AID463087",
            "AID485290",
            "AID488997",
        ]
        return DatasetMetadata(
            name="WELQRATE",
            description="WelQrate: Defining the Gold Standard in Small Molecule Drug Discovery Benchmarking",
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                "WelQrate: Defining the Gold Standard in Small Molecule Drug Discovery Benchmarking Yunchao,"
                " Liu and Dong, Ha and Wang, Xin and Moretti, Rocco and Wang, Yu and Su, Zhaoqian and Gu, Jiawei and Bodenheimer, "
                "Bobby and Weaver, Charles David and Meiler, Jens and Derr, Tyler and others arXiv preprint arXiv:2411.09820"
            ),
            file_format="parquet",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="welqrate",
        )

    def get_available_seeds(self) -> List[int]:
        """Get list of available seeds for cross-validation.

        Returns
        -------
        List[int]
            List of available seed numbers (1-5 for WELQRATE)
        """
        return [1, 2, 3, 4, 5]

    def get_splits(
        self, target: str, seed: Optional[int] = None, force_download: bool = False
    ) -> Dict[str, np.ndarray]:
        """Get the train and test splits for a target.

        Parameters
        ----------
        target : str
            Target name (e.g., 'AID2258')
        seed : Optional[int], default=None
            Seed number (1-5). If None, defaults to seed 1.
        force_download : bool, default=False
            If True, download even if the dataset already exists.

        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary containing 'train' and 'test' splits as numpy arrays

        """
        if seed is None:
            seed = 1
        if seed not in self.get_available_seeds():
            raise ValueError(
                f"Seed {seed} not available. Available seeds: {self.get_available_seeds()}"
            )
        return super().get_splits(target, seed=seed, force_download=force_download)
