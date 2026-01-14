"""Dekois dataset implementation.

This module provides functionality for downloading and managing the Dekois dataset,
which contains 55 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in parquet format and splits
are provided as NumPy arrays.
"""

import pathlib
from typing import Optional, Union

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class DekoisDownloader(DatasetDownloader):
    """Downloader for the Dekois dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the Dekois dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the Dekois dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "17betaHSD1",
            "A2A",
            "ADRB2",
            "AKT1",
            "ALR2",
            "AR",
            "AURKA",
            "AURKB",
            "BCL2",
            "CATL",
            "CDK2",
            "COX1",
            "COX2",
            "CYP2A6",
            "DHFR",
            "EGFR",
            "EPHB4",
            "FGFR1",
            "FXA",
            "GBA",
            "GR",
            "GSK3B",
            "HDAC2",
            "HIV1PR",
            "HIV1RT",
            "HSP90",
            "IGF1R",
            "ITK",
            "JAK3",
            "JNK1",
            "JNK2",
            "JNK3",
            "KIF11",
            "LCK",
            "MK2",
            "MMP2",
            "PARP-1",
            "PDE5",
            "PDK1",
            "PI3Kg",
            "PIM-1",
            "PIM-2",
            "PPARA",
            "PPARG",
            "PR",
            "ROCK-1",
            "SARS-HCoV",
            "SIRT2",
            "SRC",
            "Thrombin",
            "TIE2",
            "TK",
            "TPA",
            "VEGFR1",
            "VEGFR2",
        ]

        return DatasetMetadata(
            name="Dekois",
            description="Dekois dataset",
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                "DEKOIS: Demanding Evaluation Kits for Objective in Silico Screening — A Versatile Tool for Benchmarking Docking Programs and Scoring Functions"
                "Vogel, Simon M. and Bauer, Matthias R. and Boeckler, Frank M."
                "DOI: 10.1021/ci2001549"
            ),
            file_format="parquet",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="dekois",
            hf_split_prefix="DEKOIS",
        )
