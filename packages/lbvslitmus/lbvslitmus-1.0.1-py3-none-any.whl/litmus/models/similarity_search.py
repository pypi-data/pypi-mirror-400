# ruff: noqa: F405 F403
import numpy as np
from skfp.distances import *
from sklearn.base import BaseEstimator, ClassifierMixin, check_is_fitted
from sklearn.utils._param_validation import StrOptions
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import validate_data

SIMILARITY_FUNCTIONS = {
    "braun_blanquet_binary": bulk_braun_blanquet_binary_similarity,
    "ct4_binary": bulk_ct4_binary_similarity,
    "ct4_count": bulk_ct4_count_similarity,
    "dice_binary": bulk_dice_binary_similarity,
    "dice_count": bulk_dice_count_similarity,
    "fraggle": bulk_fraggle_similarity,
    "harris_lahey_binary": bulk_harris_lahey_binary_similarity,
    "kulczynski_binary": bulk_kulczynski_binary_similarity,
    "mcconnaughey_binary": bulk_mcconnaughey_binary_similarity,
    "rand_binary": bulk_rand_binary_similarity,
    "rogot_goldberg_binary": bulk_rogot_goldberg_binary_similarity,
    "russell_binary": bulk_russell_binary_similarity,
    "simpson_binary": bulk_simpson_binary_similarity,
    "sokal_sneath_2_binary": bulk_sokal_sneath_2_binary_similarity,
    "tanimoto_binary": bulk_tanimoto_binary_similarity,
    "tanimoto_count": bulk_tanimoto_count_similarity,
}


class SimilaritySearch(ClassifierMixin, BaseEstimator):
    """
    Similarity-based retrieval model using similarity aggregation.

    Parameters
    ----------
    similarity_function : str, default="tanimoto_binary"
        Function used to calculate similarity of the points. Must be one of:

        {"braun_blanquet_binary", "ct4_binary", "ct4_count", "dice_binary",
        "dice_count", "fraggle", "harris_lahey_binary", "kulczynski_binary",
        "mcconnaughey_binary", "rand_binary", "rogot_goldberg_binary",
        "russell_binary", "simpson_binary", "sokal_sneath_2_binary",
        "tanimoto_binary", "tanimoto_count"}

        The string selects similarity function from `scikit-fingerprints` (e.g. `bulk_tanimoto_binary_similarity`).

    aggregation : {"max", "mean"}, default="max"
        Metod used to aggregate similarity scores to positive molecules.

    threshold : float, default=0.5
        Similarity threshold for assigning a positive label. New samples with higher or equal
        similarity to training positives (actives) will be classified as positive.
    """

    _parameter_constraints: dict = {
        "aggregation": [StrOptions({"max", "mean"})],
        "similarity_function": [StrOptions(set(SIMILARITY_FUNCTIONS.keys()))],
        "threshold": [float],
    }

    def __init__(
        self,
        similarity_function: str = "tanimoto_binary",
        aggregation: str = "max",
        threshold: float = 0.5,
    ) -> None:
        self.similarity_function = similarity_function
        self.aggregation = aggregation
        self.threshold = threshold

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> "SimilaritySearch":
        """
        Fit model by calculating positive samples from X.

        Parameters
        ----------
        X : ndarray of shape (n_samples, any)
            Feature matrix.

        y : ndarray of shape (n_samples,)
            Class labels.

        Returns
        -------
        self
        """
        self._validate_params()
        validate_data(self, X=X, y=y)
        classes = unique_labels(y)
        if set(classes) != {0, 1}:
            raise ValueError(
                f"Expected binary class labels [0, 1], but found: {classes.tolist()}"
            )

        self.positives_ = X[y == 1]
        return self

    def predict_proba(self, X: np.ndarray) -> None:
        """
        Raise error as probability predictions are not supported.
        """
        raise NotImplementedError(
            "SimilaritySearch do not support predict_proba(). Try to use top_positive_matches()"
        )

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate similarities between active molecules and X.
        Similarities to all actives are aggregated using the aggregation parameter.

        Parameters
        ----------
        X : ndarray of shape (n_samples, any)
            Feature matrix.

        Returns
        -------
        similarities : ndarray of shape (n_samples,)
            Array of similarities.
        """
        check_is_fitted(self)

        similarity_matrix = SIMILARITY_FUNCTIONS[self.similarity_function](
            X, self.positives_
        )

        if self.aggregation == "mean":
            similarities = similarity_matrix.mean(axis=1)
        else:  # aggregation = "max"
            similarities = similarity_matrix.max(axis=1)

        return similarities

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict binary labels based on similarity to positive points.

        Parameters
        ----------
        X : ndarray of shape (n_samples, any)
            Feature matrix.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Predicted binary labels (1 for active, 0 otherwise).
        """
        return (self.score_samples(X) >= self.threshold).astype(int)

    def get_top_positive_matches(
        self, X: np.ndarray, n_matches: int = 1
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Return top-n closest positive matches (aggregations closest to positive points).

        Parameters
        ----------
        X : ndarray of shape (n_samples, any)
            Feature matrix.

        n_matches : int, default=1
            The number of top matches to return.

        Returns
        -------
        positive_matches : ndarray of shape (n_matches, any)
            Top-n points with highest similarity to positive points.

        similarities : ndarray of shape (n_samples,)
            Array of similarities.
        """
        similarities = self.score_samples(X)
        top_sorted_idx = np.argsort(-similarities)[:n_matches]
        return X[top_sorted_idx], similarities[top_sorted_idx]
