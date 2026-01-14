import gzip
import os
from pathlib import Path

from rdkit import Chem
from skfp.preprocessing import (
    MolFromSDFTransformer,
)

from litmus.datasets.data_filtration import (
    filter_data_set_knn_with_auroc,
    save_filtered_dataset,
)

DEKOIS_PATH = Path(__file__).parent.parent / "dekois"
OUTPUT_PATH_DEKOIS = Path(__file__).parent.parent / "filtered_dekois"

os.makedirs(OUTPUT_PATH_DEKOIS, exist_ok=True)


def parse_sdf_gz_file(filepath: str) -> list[Chem.Mol]:
    """
    Parse a single .sdf.gz file and return RDKit Mol objects.
    """
    with gzip.open(filepath, "rt", encoding="utf-8") as f:
        sdf_content = f.read()

    mols = MolFromSDFTransformer().transform(sdf_content)
    return mols


def download_dekois_target_sdf(
    source_path: str,
) -> tuple[list[Chem.Mol], list[str]]:
    """
    Load dekois molecular data from a single .sdf.gz file. and return parsed components.

    :param source_path: Path to the target directory containing the .ism file.
    :return: A tuple containing:
        - list of RDKit Mol objects,
        - list of labels of 2 types active and decoy.
    """
    if not os.path.isdir(source_path):
        raise FileNotFoundError(f"directory with path {source_path} does not exist")

    all_mols: list[Chem.Mol] = []
    labels: list[str] = []

    sdf_files = sorted(Path(source_path).glob("*.sdf.gz"))

    for filepath in sdf_files:
        mols = parse_sdf_gz_file(str(filepath))
        for mol in mols:
            if mol is None:
                continue
            all_mols.append(mol)
            # Active mols don't have a 'status' property.
            # Decoy mols have a 'status' property with the value 'decoy'.
            label = mol.GetProp("status") if mol.HasProp("status") else "active"
            labels.append(label.strip().lower())

    return all_mols, labels


def filter_dekois_sdf() -> None:
    """
    Iterate over all directories in the Dekois dataset folder and filter each target dataset.
    """
    for target in os.listdir(DEKOIS_PATH):
        if target == ".DS_Store":
            continue
        target_path = os.path.join(DEKOIS_PATH, target)
        if not os.path.isdir(target_path):
            continue
        all_mols, labels = download_dekois_target_sdf(target_path)
        print("entering: ", target)
        result = filter_data_set_knn_with_auroc(all_mols, labels, target)
        if result is not None:
            source, smiles_train, smiles_test, y_train, y_test = result
            save_filtered_dataset(
                source, smiles_train, smiles_test, y_train, y_test, OUTPUT_PATH_DEKOIS
            )


if __name__ == "__main__":
    filter_dekois_sdf()
