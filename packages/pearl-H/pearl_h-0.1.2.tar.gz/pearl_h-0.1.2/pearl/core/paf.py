"""
PAF: Prototype-guided Augmented Features
Enhances embeddings with prototype-based similarity features.
"""
import numpy as np
from sklearn.cluster import KMeans
from typing import Optional


class PrototypeFeatures:
    """
    Generates prototype-based features for embeddings.

    Creates per-class prototypes using K-means and computes
    various similarity-based features including:
    - Maximum prototype similarity per class
    - Mean prototype similarity per class
    - Class centroid similarity
    - Decision margin (difference between top-2 similarities)
    - Prediction entropy
    """

    def __init__(
        self,
        n_classes: int,
        n_prototypes_per_class: int = 3,
        random_state: int = 42
    ):
        """
        Args:
            n_classes: Number of classes
            n_prototypes_per_class: Number of prototypes per class
            random_state: Random seed for reproducibility
        """
        self.n_classes = n_classes
        self.n_proto = n_prototypes_per_class
        self.random_state = random_state

        self.prototypes = None
        self.class_centroids = None

    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> 'PrototypeFeatures':
        """
        Learn prototypes from training data.

        Args:
            embeddings: Training embeddings [N, D]
            labels: Training labels [N]

        Returns:
            self
        """
        proto_list = []
        self.class_centroids = np.zeros((self.n_classes, embeddings.shape[1]))

        for c in range(self.n_classes):
            mask = labels == c
            class_emb = embeddings[mask]

            # Compute class centroid
            self.class_centroids[c] = class_emb.mean(axis=0)

            # Compute prototypes for this class
            if len(class_emb) < self.n_proto:
                # If too few samples, replicate the centroid
                protos = np.tile(class_emb.mean(axis=0), (self.n_proto, 1))
            else:
                # Use K-means to find prototypes
                kmeans = KMeans(
                    n_clusters=self.n_proto,
                    random_state=self.random_state,
                    n_init=3
                )
                kmeans.fit(class_emb)
                protos = kmeans.cluster_centers_

            proto_list.append(protos)

        # Stack all prototypes
        self.prototypes = np.vstack(proto_list)

        # Normalize prototypes and centroids
        self.prototypes = self._normalize(self.prototypes)
        self.class_centroids = self._normalize(self.class_centroids)

        return self

    def transform(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute prototype-based features for embeddings.

        Args:
            embeddings: Input embeddings [N, D]

        Returns:
            Prototype features [N, n_features]
            where n_features = 3 * n_classes + 2
            (max_sims, mean_sims, centroid_sims, margin, entropy)
        """
        if self.prototypes is None:
            raise ValueError("Must call fit() before transform()")

        # Normalize embeddings
        emb_norm = self._normalize(embeddings)
        # Guard against numerical issues
        emb_norm = np.nan_to_num(emb_norm, nan=0.0, posinf=0.0, neginf=0.0)

        # Compute similarities to all prototypes
        proto_sims = emb_norm @ self.prototypes.T  # [N, n_classes * n_proto]

        # Reshape to [N, n_classes, n_proto]
        proto_sims_reshaped = proto_sims.reshape(
            len(embeddings), self.n_classes, self.n_proto
        )

        # Feature 1: Maximum similarity to prototypes per class
        max_sims = proto_sims_reshaped.max(axis=2)  # [N, n_classes]

        # Feature 2: Mean similarity to prototypes per class
        mean_sims = proto_sims_reshaped.mean(axis=2)  # [N, n_classes]

        # Feature 3: Similarity to class centroids
        centroid_sims = emb_norm @ self.class_centroids.T  # [N, n_classes]

        # Feature 4: Decision margin (top-1 vs top-2 max similarity)
        sorted_max = np.sort(max_sims, axis=1)[:, ::-1]
        margin = (sorted_max[:, 0] - sorted_max[:, 1]).reshape(-1, 1)  # [N, 1]

        # Feature 5: Prediction entropy based on centroid similarities
        # Use temperature scaling for better separation
        softmax_sims = np.exp(centroid_sims * 5)
        softmax_sims = softmax_sims / (softmax_sims.sum(axis=1, keepdims=True) + 1e-8)
        entropy = -np.sum(
            softmax_sims * np.log(softmax_sims + 1e-8),
            axis=1,
            keepdims=True
        )  # [N, 1]

        # Concatenate all features
        features = np.hstack([
            max_sims,       # [N, n_classes]
            mean_sims,      # [N, n_classes]
            centroid_sims,  # [N, n_classes]
            margin,         # [N, 1]
            entropy         # [N, 1]
        ])

        return features

    def fit_transform(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray
    ) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(embeddings, labels).transform(embeddings)

    def get_augmented(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Get embeddings augmented with prototype features.

        Args:
            embeddings: Input embeddings [N, D]

        Returns:
            Augmented embeddings [N, D + n_features]
        """
        features = self.transform(embeddings)
        return np.hstack([embeddings, features])

    @staticmethod
    def _normalize(x: np.ndarray) -> np.ndarray:
        """L2 normalize vectors."""
        norms = np.linalg.norm(x, axis=1, keepdims=True)
        return x / (norms + 1e-8)

    def get_feature_names(self) -> list:
        """Get names of all generated features."""
        feature_names = []

        # Max similarities
        for c in range(self.n_classes):
            feature_names.append(f'max_sim_class_{c}')

        # Mean similarities
        for c in range(self.n_classes):
            feature_names.append(f'mean_sim_class_{c}')

        # Centroid similarities
        for c in range(self.n_classes):
            feature_names.append(f'centroid_sim_class_{c}')

        # Margin and entropy
        feature_names.extend(['margin', 'entropy'])

        return feature_names

    def get_n_features(self) -> int:
        """Get total number of features generated."""
        return 3 * self.n_classes + 2


class PAFAugmentor:
    """
    Convenience wrapper for augmenting embeddings with PAF features.

    Usage:
        augmentor = PAFAugmentor(n_classes=10)
        X_train_aug = augmentor.fit_transform(X_train, y_train)
        X_test_aug = augmentor.transform(X_test)
    """

    def __init__(
        self,
        n_classes: int,
        n_prototypes_per_class: int = 3,
        random_state: int = 42
    ):
        """
        Args:
            n_classes: Number of classes
            n_prototypes_per_class: Number of prototypes per class
            random_state: Random seed
        """
        self.paf = PrototypeFeatures(
            n_classes=n_classes,
            n_prototypes_per_class=n_prototypes_per_class,
            random_state=random_state
        )

    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> 'PAFAugmentor':
        """Fit the PAF model."""
        self.paf.fit(embeddings, labels)
        return self

    def transform(self, embeddings: np.ndarray) -> np.ndarray:
        """Transform embeddings to augmented form."""
        return self.paf.get_augmented(embeddings)

    def fit_transform(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray
    ) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(embeddings, labels).transform(embeddings)

    def get_feature_names(self) -> list:
        """Get names of all features."""
        base_features = [f'emb_{i}' for i in range(self.paf.class_centroids.shape[1])]
        paf_features = self.paf.get_feature_names()
        return base_features + paf_features
