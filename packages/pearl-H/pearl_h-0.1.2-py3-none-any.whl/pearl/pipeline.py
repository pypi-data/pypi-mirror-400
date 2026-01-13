"""
PEARL Pipeline - High-level API for end-to-end embedding enhancement.
"""
import numpy as np
import torch
from typing import Optional, Literal, Union

from pearl.core.signal_extractor import SignalExtractorTrainer, SignalExtractor
from pearl.core.paf import PAFAugmentor
from pearl.utils.device import get_device


class PEARLPipeline:
    """
    End-to-end PEARL pipeline for embedding enhancement.

    This class provides a simple API for the complete PEARL workflow:
    1. Signal extraction (separating signal from noise)
    2. PAF augmentation (adding prototype-based features)

    Example:
        ```python
        from pearl import PEARLPipeline

        # Initialize pipeline
        pipeline = PEARLPipeline(n_classes=10, device='cuda')

        # Fit on training data
        pipeline.fit(X_train, y_train, X_val, y_val)

        # Transform embeddings
        X_train_enhanced = pipeline.transform(X_train, mode='enhanced')
        X_train_paf = pipeline.transform(X_train, mode='paf')
        ```
    """

    def __init__(
        self,
        n_classes: int,
        input_dim: Optional[int] = None,
        signal_dim: int = 256,
        hidden_dims: tuple = (512, 384),
        n_prototypes_per_class: int = 3,
        device: Union[str, torch.device, None] = None,
        dropout: float = 0.3,
        random_state: int = 42
    ):
        """
        Initialize PEARL pipeline.

        Args:
            n_classes: Number of classes
            input_dim: Input embedding dimension (auto-detected if None)
            signal_dim: Dimension of signal representation
            hidden_dims: Hidden layer dimensions for signal extractor
            n_prototypes_per_class: Number of prototypes per class for PAF
            device: Device to use ('auto', 'cuda', 'mps', 'cpu', or torch.device)
            dropout: Dropout rate
            random_state: Random seed for reproducibility
        """
        self.n_classes = n_classes
        self.input_dim = input_dim
        self.signal_dim = signal_dim
        self.hidden_dims = hidden_dims
        self.n_prototypes_per_class = n_prototypes_per_class
        self.device = get_device(device)
        self.dropout = dropout
        self.random_state = random_state

        # Components (initialized during fit)
        self.signal_trainer = None
        self.paf_augmentor = None

        self._is_fitted = False

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        lr: float = 1e-3,
        weight_decay: float = 1e-4,
        batch_size: int = 128,
        epochs: int = 100,
        patience: int = 20,
        recon_weight: float = 1.0,
        centroid_weight: float = 2.0,
        contrast_weight: float = 0.5,
        ortho_weight: float = 0.5,
        verbose: bool = True
    ) -> 'PEARLPipeline':
        """
        Fit the PEARL pipeline on training data.

        Args:
            X_train: Training embeddings [N, D]
            y_train: Training labels [N]
            X_val: Validation embeddings (optional)
            y_val: Validation labels (optional)
            lr: Learning rate
            weight_decay: Weight decay
            batch_size: Batch size
            epochs: Maximum epochs
            patience: Early stopping patience
            recon_weight: Weight for reconstruction loss
            centroid_weight: Weight for centroid loss
            contrast_weight: Weight for contrastive loss
            ortho_weight: Weight for orthogonality loss
            verbose: Print training progress

        Returns:
            self
        """
        # Auto-detect input dimension
        if self.input_dim is None:
            self.input_dim = X_train.shape[1]

        if verbose:
            print("="*80)
            print("PEARL Pipeline Training")
            print("="*80)
            print(f"Input dim: {self.input_dim}")
            print(f"Signal dim: {self.signal_dim}")
            print(f"N classes: {self.n_classes}")
            print(f"Device: {self.device}")

        # Step 1: Train signal extractor
        if verbose:
            print("\n[1/2] Training Signal Extractor...")

        signal_model = SignalExtractor(
            input_dim=self.input_dim,
            signal_dim=self.signal_dim,
            hidden_dims=self.hidden_dims,
            n_classes=self.n_classes,
            dropout=self.dropout
        )

        self.signal_trainer = SignalExtractorTrainer(
            model=signal_model,
            device=self.device,
            lr=lr,
            weight_decay=weight_decay,
            batch_size=batch_size,
            epochs=epochs,
            patience=patience,
            recon_weight=recon_weight,
            centroid_weight=centroid_weight,
            contrast_weight=contrast_weight,
            ortho_weight=ortho_weight
        )

        self.signal_trainer.fit(X_train, y_train, X_val, y_val)

        if verbose:
            print("✓ Signal Extractor trained")

        # Step 2: Extract enhanced embeddings
        if verbose:
            print("\n[2/2] Fitting PAF on enhanced embeddings...")

        X_train_enhanced = self.signal_trainer.transform(X_train)

        # Step 3: Fit PAF augmentor
        self.paf_augmentor = PAFAugmentor(
            n_classes=self.n_classes,
            n_prototypes_per_class=self.n_prototypes_per_class,
            random_state=self.random_state
        )

        self.paf_augmentor.fit(X_train_enhanced, y_train)

        if verbose:
            print("✓ PAF fitted")
            print("\n" + "="*80)
            print("PEARL Pipeline Training Complete!")
            print("="*80)

        self._is_fitted = True
        return self

    def transform(
        self,
        X: np.ndarray,
        mode: Literal['raw', 'enhanced', 'paf'] = 'paf'
    ) -> np.ndarray:
        """
        Transform embeddings using PEARL.

        Args:
            X: Input embeddings [N, D]
            mode: Transformation mode:
                - 'raw': Return original embeddings (no-op)
                - 'enhanced': Return signal-extracted embeddings
                - 'paf': Return enhanced embeddings with PAF features (default)

        Returns:
            Transformed embeddings
        """
        if not self._is_fitted:
            raise ValueError("Pipeline must be fitted before transform. Call fit() first.")

        if mode == 'raw':
            return X

        # Extract signal
        X_enhanced = self.signal_trainer.transform(X)

        if mode == 'enhanced':
            return X_enhanced

        if mode == 'paf':
            return self.paf_augmentor.transform(X_enhanced)

        raise ValueError(f"Invalid mode: {mode}. Choose from 'raw', 'enhanced', 'paf'")

    def fit_transform(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        mode: Literal['raw', 'enhanced', 'paf'] = 'paf',
        **fit_params
    ) -> np.ndarray:
        """
        Fit the pipeline and transform training data in one step.

        Args:
            X_train: Training embeddings
            y_train: Training labels
            X_val: Validation embeddings (optional)
            y_val: Validation labels (optional)
            mode: Transformation mode
            **fit_params: Additional parameters passed to fit()

        Returns:
            Transformed training embeddings
        """
        self.fit(X_train, y_train, X_val, y_val, **fit_params)
        return self.transform(X_train, mode=mode)

    def get_signal_model(self) -> SignalExtractor:
        """Get the trained signal extractor model."""
        if not self._is_fitted:
            raise ValueError("Pipeline not fitted yet")
        return self.signal_trainer.model

    def get_paf_augmentor(self) -> PAFAugmentor:
        """Get the fitted PAF augmentor."""
        if not self._is_fitted:
            raise ValueError("Pipeline not fitted yet")
        return self.paf_augmentor

    def save(self, path: str):
        """
        Save the pipeline to disk.

        Args:
            path: Directory path to save the pipeline
        """
        import os
        import pickle

        if not self._is_fitted:
            raise ValueError("Cannot save unfitted pipeline")

        os.makedirs(path, exist_ok=True)

        # Save signal extractor model
        torch.save(
            self.signal_trainer.model.state_dict(),
            os.path.join(path, "signal_model.pt")
        )

        # Save PAF augmentor
        with open(os.path.join(path, "paf_augmentor.pkl"), 'wb') as f:
            pickle.dump(self.paf_augmentor, f)

        # Save config
        config = {
            'n_classes': self.n_classes,
            'input_dim': self.input_dim,
            'signal_dim': self.signal_dim,
            'hidden_dims': self.hidden_dims,
            'n_prototypes_per_class': self.n_prototypes_per_class,
            'dropout': self.dropout,
            'random_state': self.random_state
        }
        with open(os.path.join(path, "config.pkl"), 'wb') as f:
            pickle.dump(config, f)

        print(f"Pipeline saved to {path}")

    @classmethod
    def load(cls, path: str, device: Union[str, torch.device, None] = None) -> 'PEARLPipeline':
        """
        Load a saved pipeline from disk.

        Args:
            path: Directory path containing the saved pipeline
            device: Device to load the model on ('auto', 'cuda', 'mps', 'cpu')

        Returns:
            Loaded PEARLPipeline
        """
        import os
        import pickle

        # Load config
        with open(os.path.join(path, "config.pkl"), 'rb') as f:
            config = pickle.load(f)

        # Create pipeline
        pipeline = cls(**config, device=device)

        # Load signal extractor
        signal_model = SignalExtractor(
            input_dim=config['input_dim'],
            signal_dim=config['signal_dim'],
            hidden_dims=config['hidden_dims'],
            n_classes=config['n_classes'],
            dropout=config['dropout']
        )
        signal_model.load_state_dict(
            torch.load(os.path.join(path, "signal_model.pt"), map_location=pipeline.device)
        )
        signal_model.to(pipeline.device)

        pipeline.signal_trainer = SignalExtractorTrainer(
            model=signal_model,
            device=pipeline.device
        )

        # Load PAF augmentor
        with open(os.path.join(path, "paf_augmentor.pkl"), 'rb') as f:
            pipeline.paf_augmentor = pickle.load(f)

        pipeline._is_fitted = True

        print(f"Pipeline loaded from {path}")
        return pipeline
