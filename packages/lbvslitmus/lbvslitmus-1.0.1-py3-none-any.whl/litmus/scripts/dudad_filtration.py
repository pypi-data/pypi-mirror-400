import os
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import RDLogger
from rdkit.Chem import Mol
from skfp.preprocessing import MolFromSDFTransformer

from litmus.datasets.data_filtration import (
    filter_data_set_knn_with_auroc,
)
from litmus.model_selection.splitters.maxmin_split import maxmin_train_test_split

# Disable warning about molecules being tagged as 2D but have at least on Z coordinate
RDLogger.DisableLog("rdApp.*")

DUDAD_PATH = Path(__file__).parent.parent / "data" / "102_AD_dataset"
OUTPUT_PATH_DUDAD = Path(__file__).parent.parent / "data" / "filtered_dudad"
OUTPUT_PATH_DUDAD_SPLIT = Path(__file__).parent.parent / "data" / "dudad_splits"

os.makedirs(OUTPUT_PATH_DUDAD, exist_ok=True)


def parse_sdf_file(filepath: str) -> list[Mol]:
    """
    Parse a single .sdf file and return RDKit Mol objects.
    """
    with open(filepath, encoding="utf-8") as file:
        sdf_content = file.read()

    mols = MolFromSDFTransformer().transform(sdf_content)
    return mols


def load_dudad_target(
    filepath_active: str,
    filepath_decoy: str,
) -> tuple[list[Mol], list[str]]:
    """
    Load molecular data from .sdf files and return parsed components.

    :param filepath_active: Path to the target file .sdf with active molecules.
    :param filepath_decoy: Path to the target file .sdf with AD molecules.
    :return: A tuple containing:
        - list of RDKit Mol objects,
        - list of labels of 2 types active and decoy.
    """
    source_path = DUDAD_PATH

    if not os.path.isdir(source_path):
        raise FileNotFoundError(f"Directory with path {source_path} does not exist")

    all_mols: list[Mol] = []
    labels: list[str] = []

    mols = parse_sdf_file(filepath_active)
    all_mols.extend(mols)
    labels.extend([1] * len(mols))

    mols = parse_sdf_file(filepath_decoy)
    all_mols.extend(mols)
    labels.extend([0] * len(mols))

    return all_mols, labels


def filter_dudad() -> None:
    """
    Filter out targets from DUD-AD dataset that achieve AUROC > 0.9 for a kNN with k=1 classifier.
    Saves the filtered dataset as CSV file in the output directory.
    """
    source_path = DUDAD_PATH

    # Find all targets
    sdf_files = [file for file in os.listdir(source_path) if file.endswith(".sdf")]
    targets = {file.split("_")[0] for file in sdf_files}

    filtered_out_targets = 0

    target_files = {target: {"actives": None, "AD": None} for target in targets}
    for filename in sdf_files:
        path = source_path / filename

        filename_parts = filename.split("_")
        target = filename_parts[0]
        file_type = filename_parts[1][:-4]
        target_files[target][file_type] = path

    for target in targets:
        target_mols, y = load_dudad_target(*target_files[target].values())
        labels = ["active" if label == 1 else "decoy" for label in y]
        result = filter_data_set_knn_with_auroc(target_mols, labels, target)
        if result is not None:
            _, smiles_train, smiles_test, y_train, y_test = result

            df = pd.DataFrame(
                {
                    "SMILES": smiles_train + smiles_test,
                    target: y_train.tolist() + y_test.tolist(),
                }
            )
            df.to_csv(OUTPUT_PATH_DUDAD / f"DUDAD_{target}.csv", index=False)
            _generate_and_save_splits(target=target)
        else:
            filtered_out_targets += 1

    print(f"Filtered out {filtered_out_targets} targets")


def _generate_and_save_splits(target, output_dir=None) -> None:
    if output_dir is None:
        output_dir = OUTPUT_PATH_DUDAD_SPLIT

    os.makedirs(output_dir, exist_ok=True)

    train_split_path = output_dir / f"DUDAD_{target}.train_idx.npy"
    test_split_path = output_dir / f"DUDAD_{target}.test_idx.npy"

    dataset_path = OUTPUT_PATH_DUDAD / f"DUDAD_{target}.csv"

    df = pd.read_csv(dataset_path)
    smiles = df["SMILES"].tolist()

    train_idx, test_idx = maxmin_train_test_split(data=smiles, show_progress=True)

    np.save(train_split_path, np.array(train_idx))
    np.save(test_split_path, np.array(test_idx))


if __name__ == "__main__":
    filter_dudad()
