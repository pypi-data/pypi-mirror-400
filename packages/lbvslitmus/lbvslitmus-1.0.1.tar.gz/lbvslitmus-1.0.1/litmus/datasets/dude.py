"""DUD-E dataset implementation.

This module provides functionality for downloading and managing the DUD-E dataset,
which contains 21 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in parquet format and splits
are provided as NumPy arrays.
"""

import pathlib
from typing import Optional, Union

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class DUDEDownloader(DatasetDownloader):
    """Downloader for the DUD-E dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the DUD-E dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the DUD-E dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "abl1",
            "ampc",
            "aofb",
            "cp3a4",
            "csf1r",
            "fabp4",
            "fak1",
            "gria2",
            "hivint",
            "jak2",
            "kit",
            "kpcb",
            "lck",
            "mk01",
            "mk10",
            "mp2k1",
            "pa2ga",
            "plk1",
            "ptn1",
            "pygm",
            "src",
        ]
        return DatasetMetadata(
            name="DUD-E",
            description="DUD-E",
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                "Directory of Useful Decoys, Enhanced (DUD-E): Better Ligands and Decoys for Better Benchmarking"
                "Mysinger, Michael M. and Carchia, Michael and Irwin, John. J. and Shoichet, Brian K."
                "DOI: 10.1021/jm300687e"
            ),
            file_format="parquet",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="dude",
            hf_split_prefix="DUDE",
        )
