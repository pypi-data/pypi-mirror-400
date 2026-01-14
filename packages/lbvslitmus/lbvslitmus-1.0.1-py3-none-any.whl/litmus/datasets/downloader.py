"""Dataset downloader implementation for Litmus.

This module provides functionality for downloading and managing datasets
used in virtual screening experiments. All datasets are downloaded from
HuggingFace Hub (https://huggingface.co/datasets/scikit-fingerprints/litmus)
where they are preprocessed and ready to use. The datasets are organized in
folders with subfolders 'data' (containing dataset files) and 'splits' (containing
train/test split indices as NumPy arrays).
"""

import pathlib
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from sklearn.datasets import get_data_home
from tqdm import tqdm


@dataclass
class DatasetMetadata:
    """Metadata for a dataset."""

    name: str
    description: str
    source_url: str
    available_targets: List[str]  # List of available targets in the dataset
    citation: Optional[str] = None
    file_format: str = "parquet"  # Supported formats: "csv", "parquet"
    hf_repo: str = "scikit-fingerprints/litmus"  # HuggingFace repository name
    hf_subdir: Optional[str] = None  # Custom HuggingFace subdirectory name
    hf_split_prefix: Optional[str] = None  # Custom prefix for split filenames
    hf_repo_path_template: Optional[
        str
    ] = None  # Template used to compose paths on HuggingFace


class DatasetDownloader(ABC):
    """Base class for dataset downloaders.

    All datasets are downloaded from HuggingFace Hub where they are
    preprocessed and ready to use. The datasets are organized in folders
    with subfolders 'data' (containing dataset files) and 'splits' (containing
    train/test split indices as NumPy arrays).
    """

    def __init__(self, cache_dir: Optional[Union[str, pathlib.Path]] = None):
        """Initialize the dataset downloader.

        Parameters
        ----------
        cache_dir : Optional[Union[str, pathlib.Path]], default=None
            Directory to store downloaded datasets. If None, uses
            get_data_home() from sklearn.datasets.
        """
        if cache_dir is None:
            cache_dir = pathlib.Path(get_data_home()) / "litmus" / "datasets"
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir = self.cache_dir / "splits"
        self.splits_dir.mkdir(exist_ok=True)

    @property
    @abstractmethod
    def metadata(self) -> DatasetMetadata:
        """Get metadata for the dataset.

        Returns
        -------
        DatasetMetadata
            DatasetMetadata object containing dataset information.
        """

    def get_dataset_path(self, target: str) -> pathlib.Path:
        """Get the path where the dataset should be stored.

        Parameters
        ----------
        target : str
            Target name to get the dataset path for.

        Returns
        -------
        pathlib.Path
            Path to the dataset file.
        """
        return (
            self.cache_dir
            / f"{self.metadata.name}_{target}.{self.metadata.file_format}"
        )

    def is_downloaded(self, target: str) -> bool:
        """Check if the dataset is already downloaded.

        Parameters
        ----------
        target : str
            Target name to check for.

        Returns
        -------
        bool
            True if the dataset exists in the cache directory.
        """
        return self.get_dataset_path(target).exists()

    def _download_file_from_hf(
        self, filename: str, subfolder: str, force: bool = False
    ) -> pathlib.Path:
        """Download a file from HuggingFace Hub.

        Parameters
        ----------
        filename : str
            Name of the file to download
        subfolder : str
            Subfolder in the repository (e.g., 'data', 'splits')
        force : bool, default=False
            If True, force download even if file exists

        Returns
        -------
        pathlib.Path
            Path to the downloaded file
        """
        dataset_folder = (
            self.metadata.hf_subdir
            if self.metadata.hf_subdir is not None
            else self.metadata.name.lower().replace("-", "_")
        )
        if self.metadata.hf_repo_path_template:
            repo_path = self.metadata.hf_repo_path_template.format(
                dataset_folder=dataset_folder,
                subfolder=subfolder,
                filename=filename,
            )
        else:
            repo_path = f"{dataset_folder}/{subfolder}/{filename}"

        local_path = hf_hub_download(
            repo_id=self.metadata.hf_repo,
            filename=repo_path,
            repo_type="dataset",
            force_download=force,
            local_dir=self.cache_dir / "huggingface_cache",
        )
        return pathlib.Path(local_path)

    def get_available_seeds(self) -> List[Optional[int]]:
        """Return seeds that should be downloaded for this dataset."""
        return [None]

    def _get_data_file_extension(self) -> str:
        """Return the file extension used for remote dataset files."""
        return self.metadata.file_format

    def _get_data_prefix(self) -> str:
        """Return the prefix used for remote dataset files."""
        return self._get_split_prefix()

    def _get_data_filename(self, target: str) -> str:
        """Compose the remote filename for a dataset target."""
        return f"{self._get_data_prefix()}_{target}.{self._get_data_file_extension()}"

    def _format_split_filename(
        self,
        target: str,
        split: str,
        seed: Optional[int],
        dataset_prefix: Optional[str] = None,
    ) -> str:
        """Compose the filename for split files."""
        prefix = self._get_split_prefix(dataset_prefix)
        if seed is not None:
            return f"seed{seed}_{prefix}_{target}.{split}_idx.npy"
        return f"{prefix}_{target}.{split}_idx.npy"

    def _split_file_exists(
        self,
        target: str,
        split: str,
        seed: Optional[int],
        dataset_prefix: Optional[str],
    ) -> bool:
        """Check whether the split file is already cached locally."""
        filename = self._format_split_filename(target, split, seed, dataset_prefix)
        return (self.splits_dir / filename).exists()

    def _get_split_prefix(self, dataset_prefix: Optional[str] = None) -> str:
        """Resolve the prefix used for split filenames."""
        if dataset_prefix is not None:
            return dataset_prefix

        if self.metadata.hf_split_prefix is not None:
            return self.metadata.hf_split_prefix

        return self.metadata.name.replace("-", "_")

    def _download_splits(
        self,
        target: str,
        dataset_prefix: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, np.ndarray]:
        """Download train and test splits for a target from HuggingFace Hub.

        Parameters
        ----------
        target : str
            Target name (e.g., 'MUV-466', 'ALDH1')
        dataset_prefix : str
            Prefix for the split filename (e.g., 'muv', 'LIT-PCBA')
        seed : Optional[int], default=None
            Seed number for datasets with multiple seeds (e.g., WelQrate).
            If None, uses default split without seed prefix.

        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary containing 'train' and 'test' splits as numpy arrays
        """
        splits = {}
        split_types = ["train", "test"]

        for split in split_types:
            filename = self._format_split_filename(target, split, seed, dataset_prefix)
            split_path = self.splits_dir / filename

            if not split_path.exists():
                downloaded_path = self._download_file_from_hf(filename, "splits")
                # Copy to splits_dir for easier access
                shutil.copy2(downloaded_path, split_path)

            splits[split] = np.load(split_path)

        return splits

    def download(self, force: bool = False) -> None:
        """Download dataset files and splits from HuggingFace Hub."""
        targets = self.metadata.available_targets
        seeds = self.get_available_seeds()
        split_prefix = self.metadata.hf_split_prefix

        all_targets_exist = all(self.is_downloaded(target) for target in targets)
        splits_exist = all(
            self._split_file_exists(target, split, seed, split_prefix)
            for target in targets
            for seed in seeds
            for split in ["train", "test"]
        )

        if not force and all_targets_exist and splits_exist:
            return

        if not all_targets_exist or force:
            for target in tqdm(targets, desc=f"Downloading {self.metadata.name} data"):
                target_path = self.get_dataset_path(target)
                if force or not target_path.exists():
                    filename = self._get_data_filename(target)
                    downloaded_path = self._download_file_from_hf(
                        filename, "data", force
                    )
                    shutil.copy2(downloaded_path, target_path)

        if force or not splits_exist:
            for target in tqdm(
                targets, desc=f"Downloading {self.metadata.name} splits"
            ):
                for seed in seeds:
                    self._download_splits(
                        target, dataset_prefix=split_prefix, seed=seed
                    )

    def get_splits(
        self, target: str, seed: Optional[int] = None, force_download: bool = False
    ) -> Dict[str, np.ndarray]:
        """Get the train and test splits for a given target.

        Parameters
        ----------
        target : str
            Target name to get the split for.
        seed : Optional[int], default=None
            Seed number for datasets with multiple seeds (e.g., WelQrate).
            If None, uses default split without seed prefix.
        force_download : bool, default=False
            If True, download even if the dataset already exists.

        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary containing 'train' and 'test' splits as numpy arrays
        """
        if target not in self.metadata.available_targets:
            raise ValueError(
                f"Target '{target}' not found in dataset. "
                f"Available targets: {self.metadata.available_targets}"
            )

        if not self.is_downloaded(target):
            if force_download:
                self.download(force=True)
            else:
                raise ValueError(
                    f"Dataset for target '{target}' is not downloaded. "
                    "Please call download() first."
                )

        # Determine dataset prefix from metadata name
        return self._download_splits(
            target, dataset_prefix=self.metadata.hf_split_prefix, seed=seed
        )

    def load(self, target: str, force_download: bool = False) -> pd.DataFrame:
        """Load the dataset, downloading it if necessary.

        Parameters
        ----------
        target : str
            Target name to load the dataset for.
        force_download : bool, default=False
            If True, download even if the dataset already exists.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the dataset.
        """
        if target not in self.metadata.available_targets:
            raise ValueError(
                f"Target '{target}' not found in dataset. Available targets: {self.metadata.available_targets}"
            )

        if not self.is_downloaded(target) or force_download:
            self.download(force=force_download)

        dataset_path = self.get_dataset_path(target)

        if self.metadata.file_format == "csv":
            df = pd.read_csv(dataset_path)
        elif self.metadata.file_format == "parquet":
            df = pd.read_parquet(dataset_path, engine="pyarrow")
        else:
            raise ValueError(f"Unsupported format: {self.metadata.file_format}")

        required_columns = {"SMILES", target}
        missing_cols = required_columns - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset is missing required columns: {missing_cols}")

        return df
