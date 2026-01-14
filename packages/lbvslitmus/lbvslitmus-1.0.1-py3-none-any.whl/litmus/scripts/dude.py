import os
from pathlib import Path

import pandas as pd
from rdkit import Chem
from skfp.preprocessing import (
    MolFromSmilesTransformer,
)

from litmus.datasets.data_filtration import (
    filter_data_set_knn_with_auroc,
    save_filtered_dataset,
)

DUDE_PATH = Path(__file__).parent.parent / "dude"
OUTPUT_PATH_DUDE = Path(__file__).parent.parent / "filtered_dude"
os.makedirs(OUTPUT_PATH_DUDE, exist_ok=True)


def load_dude_target(
    source_path: str,
) -> tuple[list[Chem.Mol], list[str]]:
    """
    Load molecular data from an .ism file and return parsed components.

    :param source_path: Path to the target directory containing the .ism file.
    :return: A tuple containing:
        - list of RDKit Mol objects,
        - list of labels of 2 types active and decoy.
    """
    if not os.path.isdir(source_path):
        raise FileNotFoundError(f"directory with path {source_path} does not exist")

    all_mols: list[Chem.Mol] = []
    labels: list[str] = []

    mol_from_smiles = MolFromSmilesTransformer(valid_only=True, n_jobs=-1)
    for label in ["actives", "decoys"]:
        filename = f"{label}_final.ism"
        filepath = os.path.join(source_path, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"directory with path {filepath} does not exist")

        df = pd.read_csv(filepath, sep=r"\s+", header=None, engine="python")
        # Skip lines that don't have at least SMILES and ID
        df = df[df.notna().sum(axis=1) >= 2]
        lines = df.to_numpy().tolist()

        smiles_raw = [parts[0] for parts in lines]

        mols = mol_from_smiles.transform(smiles_raw)
        all_mols.extend(mols)
        labels.extend([label[:-1]] * len(mols))

    return all_mols, labels


def filter_dude() -> None:
    """
    Iterate over all directories in the DUDe dataset folder and filter each target dataset.
    """
    for target in os.listdir(DUDE_PATH):
        if target == ".DS_Store":
            continue
        target_path = os.path.join(DUDE_PATH, target)
        if not os.path.isdir(target_path):
            continue
        all_mols, labels = load_dude_target(target_path)
        print("entering: ", target)
        result = filter_data_set_knn_with_auroc(all_mols, labels, target)
        if result is not None:
            source, smiles_train, smiles_test, y_train, y_test = result
            save_filtered_dataset(
                source, smiles_train, smiles_test, y_train, y_test, OUTPUT_PATH_DUDE
            )


if __name__ == "__main__":
    filter_dude()
