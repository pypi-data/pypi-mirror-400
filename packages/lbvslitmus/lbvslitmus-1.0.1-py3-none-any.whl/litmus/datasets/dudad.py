"""DUD-AD dataset implementation.

This module provides functionality for downloading and managing the DUD-AD dataset,
which contains 55 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in CSV format and splits
are provided as NumPy arrays.
"""

import pathlib
from typing import Optional, Union

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class DUDADDownloader(DatasetDownloader):
    """Downloader for the DUD-AD dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the DUD-AD dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the DUD-AD dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "abl1",
            "aces",
            "adrb1",
            "adrb2",
            "akt1",
            "akt2",
            "aldr",
            "ampc",
            "andr",
            "aofb",
            "braf",
            "cdk2",
            "cp2c9",
            "cp3a4",
            "csf1r",
            "cxcr4",
            "egfr",
            "esr1",
            "esr2",
            "fa7",
            "fabp4",
            "fak1",
            "fgfr1",
            "gcr",
            "gria2",
            "hdac8",
            "hivrt",
            "igf1r",
            "jak2",
            "kit",
            "kpcb",
            "lck",
            "mapk2",
            "mcr",
            "met",
            "mk01",
            "mk10",
            "mk14",
            "mp2k1",
            "pa2ga",
            "pgh1",
            "pgh2",
            "plk1",
            "ppard",
            "pparg",
            "prgr",
            "ptn1",
            "pur2",
            "pyrd",
            "rock1",
            "src",
            "try1",
            "tysy",
            "urok",
            "vgfr2",
        ]
        return DatasetMetadata(
            name="DUD-AD",
            description="DUD-E dataset enhanced with active decoys",
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                "Chen L, Cruz A, Ramsey S, Dickson CJ, Duca JS, Hornak V, Koes DR, Kurtzman T. Hidden bias in the DUD-E dataset leads to misleading "
                "performance of deep learning in structure-based virtual screening. PLoS One. 2019"
            ),
            file_format="csv",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="dudad",
            hf_split_prefix="DUDAD",
        )
