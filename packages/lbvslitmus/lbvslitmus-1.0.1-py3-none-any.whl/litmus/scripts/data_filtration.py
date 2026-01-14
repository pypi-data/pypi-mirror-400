from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from skfp.fingerprints import ECFPFingerprint
from skfp.model_selection import maxmin_train_test_split
from skfp.preprocessing import (
    MolToSmilesTransformer,
)
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import KNeighborsClassifier


def save_filtered_dataset(
    source: str,
    smiles_train: list[str],
    smiles_test: list[str],
    y_train: np.ndarray,
    y_test: np.ndarray,
    output_path: Path,
):
    """
    Save filtered dataset.

    :param source: source of file.
    :param smiles_train: smiles used for training.
    :param smiles_test: smiles used for tests.
    :param y_train: information about labels inside train.
    :param y_test: information about labels inside test.
    :param output_path: path for the output.
    :return: None
    """
    target_dir = output_path / source
    target_dir.mkdir(parents=True, exist_ok=True)

    full_smiles = smiles_train + smiles_test
    full_labels = list(y_train.astype(int)) + list(y_test.astype(int))
    full_split = (["train"] * len(y_train)) + (["test"] * len(y_test))
    labels = ["active" if y == 1 else "decoy" for y in full_labels]

    df = pd.DataFrame(
        {
            "smiles": full_smiles,
            "label": labels,
        }
    )
    df.to_csv(target_dir / "dataset.csv", index=False)

    df_split = pd.DataFrame(
        {"index": list(range(len(full_split))), "split": full_split}
    )
    df_split.to_csv(target_dir / "split_indices.csv", index=False)


def filter_data_set_knn_with_auroc(
    all_mols: list[Chem.Mol],
    labels: list[str],
    source: str,
):
    """
     Filter a single target dataset using knn.

    :param all_mols: list of RDKit Mol objects.
    :param labels: labels of 2 types active and decoy.
    :param source: name of surce file.
    :return: Optional[str]: Data for saving if AUROC < 0.90, otherwise None.
    """
    y = [1 if label.lower() == "active" else 0 for label in labels]
    smiles_list = MolToSmilesTransformer(n_jobs=-1).transform(all_mols)

    smiles_active = [s for s, label in zip(smiles_list, y) if label == 1]
    y_active = np.ones(len(smiles_active))

    smiles_decoy = [s for s, label in zip(smiles_list, y) if label == 0]
    y_decoy = np.zeros(len(smiles_decoy))

    (
        smiles_train_active,
        smiles_test_active,
        y_train_active,
        y_test_active,
    ) = maxmin_train_test_split(smiles_active, y_active, test_size=0.25, random_state=0)
    (
        smiles_train_decoy,
        smiles_test_decoy,
        y_train_decoy,
        y_test_decoy,
    ) = maxmin_train_test_split(smiles_decoy, y_decoy, test_size=0.25, random_state=0)

    smiles_train = smiles_train_active + smiles_train_decoy
    smiles_test = smiles_test_active + smiles_test_decoy
    y_train = np.concatenate([y_train_active, y_train_decoy])
    y_test = np.concatenate([y_test_active, y_test_decoy])

    fp = ECFPFingerprint()
    X_train = fp.transform(smiles_train)
    X_test = fp.transform(smiles_test)

    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(X_train, y_train)
    y_pred = knn.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred)

    print(f"[{source}] AUROC MaxMin split: {auc:.2%}")

    if auc < 0.90:
        return source, smiles_train, smiles_test, y_train, y_test
    else:
        return None
