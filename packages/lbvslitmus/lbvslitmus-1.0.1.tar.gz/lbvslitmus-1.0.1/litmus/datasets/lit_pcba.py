"""LIT-PCBA dataset implementation.

This module provides functionality for downloading and managing the LIT-PCBA dataset,
which contains 15 targets. The dataset is downloaded from HuggingFace Hub
(https://huggingface.co/datasets/scikit-fingerprints/litmus) where it is
preprocessed and ready to use. All data files are in Parquet format and splits
are provided as NumPy arrays.
"""

import pathlib
from typing import Optional, Union

from litmus.datasets.downloader import DatasetDownloader, DatasetMetadata


class LITPCBADownloader(DatasetDownloader):
    """Downloader for the LIT-PCBA dataset."""

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the LIT-PCBA dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        super().__init__(cache_dir)

    @property
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the LIT-PCBA dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """
        available_targets = [
            "ADRB2",
            "ALDH1",
            "ESR1_ago",
            "ESR1_ant",
            "FEN1",
            "GBA",
            "IDH1",
            "KAT2A",
            "MAPK1",
            "MTORC1",
            "OPRK1",
            "PKM2",
            "PPARG",
            "TP53",
            "VDR",
        ]
        return DatasetMetadata(
            name="LIT-PCBA",
            description=(
                "LIT-PCBA: A dataset for virtual screening and machine learning 15 target sets, 7761 actives and 382674 unique inactives selected from high-confidence PubChem Bioassay data"
            ),
            source_url="https://huggingface.co/datasets/scikit-fingerprints/litmus",
            citation=(
                """
                LIT-PCBA: An Unbiased Data Set for Machine Learning and Virtual Screening
                Viet-Khoa Tran-Nguyen, Célien Jacquemard, and Didier Rognan
                Journal of Chemical Information and Modeling 2020 60 (9), 4263-4273
                DOI: 10.1021/acs.jcim.0c00155
                """
            ),
            file_format="parquet",
            available_targets=available_targets,
            hf_repo="scikit-fingerprints/litmus",
            hf_subdir="litpcba",
            hf_split_prefix="LIT-PCBA",
        )

