"""Split the data into train and test sets using the max-min method."""

from collections.abc import Sequence
from typing import List

from rdkit.Chem import MolFromSmiles
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from rdkit.SimDivFilters.rdSimDivPickers import MaxMinPicker
from tqdm import tqdm


def maxmin_train_test_split(
    data: Sequence[str],
    train_size: float = 0.75,
    random_state: int = 0,
    batch_size: int = 10000,
    show_progress: bool = False,
) -> tuple[List[int], List[int]]:
    """
    Split the data into train and test sets using the max-min method with progress reporting.

    Parameters
    ----------
    data : Sequence[str]
        The data to be split in SMILES format.
    train_size : float, default=0.75
        The proportion of the data to include in the train split.
    random_state : int, default=0
        Controls the randomness of the training and testing indices.
    batch_size : int, default=10000
        Size of batches to process for large datasets.
    show_progress : bool, default=False
        Whether to show progress bar for fingerprint generation.

    Returns
    -------
    tuple[List[int], List[int]]
        A tuple containing the train idx and test idx.
    """
    data_size = len(data)

    if train_size > 1 or train_size < 0:
        raise ValueError("train_size should be between 0 and 1")
    train_size, test_size = (
        int(data_size * train_size),
        int(data_size * (1 - train_size)),
    )

    if train_size == 0 or test_size == 0:
        raise ValueError("train_size and test_size should be greater than 0")

    # Process data in batches for large datasets
    all_fps = []
    batch_count = (data_size + batch_size - 1) // batch_size

    # Only show progress bar if explicitly requested
    batch_iterator = range(batch_count)
    if show_progress:
        batch_iterator = tqdm(
            batch_iterator,
            desc="Generating fingerprints",
            unit="batch",
            leave=False,
            position=0,
        )

    for batch_idx in batch_iterator:
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, data_size)
        batch_smiles = data[start_idx:end_idx]

        # Convert batch to RDKit mols
        batch_mols = [MolFromSmiles(smi) for smi in batch_smiles]
        # Generate fingerprints for batch
        batch_fps = GetMorganGenerator(radius=2, fpSize=2048).GetFingerprints(
            batch_mols
        )
        all_fps.extend(batch_fps)

    picker = MaxMinPicker()
    test_indices = picker.LazyBitVectorPick(
        all_fps,
        poolSize=data_size,
        pickSize=test_size,
        seed=random_state,
    )

    test_indices = list(test_indices)
    train_indices = list(set(range(data_size)) - set(test_indices))

    return train_indices, test_indices
