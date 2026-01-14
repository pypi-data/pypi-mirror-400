import os
from pathlib import Path

import numpy as np
import pandas as pd

from litmus.model_selection.splitters.maxmin_split import maxmin_train_test_split


def migrate_dataset_to_v2_structure(
    input_path, output_path, split_output_path, dataset_name
):
    """
    Change dataset file structure from target directories with `dataset.csv` and `split_indices.csv`
    to flat structure with separate direcories for data and splits.
    """
    Path(output_path).mkdir(parents=True, exist_ok=True)
    Path(split_output_path).mkdir(parents=True, exist_ok=True)
    targets = os.listdir(input_path)

    for target in targets:
        target_input_path = Path(input_path) / target

        df_data = pd.read_csv(target_input_path / "dataset.csv")

        df_data["label"] = df_data["label"].map({"active": 1, "decoy": 0})
        df_data = df_data.rename(columns={"label": target})
        df_data = df_data.rename(columns={"smiles": "SMILES"})

        df_data.to_parquet(
            Path(output_path) / f"{dataset_name}_{target}.parquet", engine="pyarrow"
        )

        smiles = df_data["SMILES"].tolist()

        train_idx, test_idx = maxmin_train_test_split(data=smiles, show_progress=True)

        train_split_path = (
            Path(split_output_path) / f"{dataset_name}_{target}.train_idx.npy"
        )
        test_split_path = (
            Path(split_output_path) / f"{dataset_name}_{target}.test_idx.npy"
        )

        np.save(train_split_path, np.array(train_idx))
        np.save(test_split_path, np.array(test_idx))


if __name__ == "__main__":
    output_path = "litmus/data/filtered_dekois_v2"
    input_path = "litmus/data/filtered_dekois"
    split_output_path = "litmus/data/filtered_dekois_splits_v2"

    migrate_dataset_to_v2_structure(
        input_path, output_path, split_output_path, "DEKOIS"
    )

    output_path = "litmus/data/filtered_dude_v2"
    input_path = "litmus/data/filtered_dude"
    split_output_path = "litmus/data/filtered_dude_splits_v2"

    migrate_dataset_to_v2_structure(input_path, output_path, split_output_path, "DUDE")
