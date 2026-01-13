"""
Signal Extractor Module
Separates discriminative signal from noise in embeddings.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, Tuple, Optional, Union

from pearl.utils.device import get_device


class CentroidManager:
    """Manages class centroids for signal extraction."""

    def __init__(self, n_classes: int):
        """
        Args:
            n_classes: Number of classes
        """
        self.n_classes = n_classes
        self.centroids = None
        self.centroids_normalized = None
        self.centroids_t = None
        self.centroids_norm_t = None

    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> 'CentroidManager':
        """
        Compute class centroids from embeddings.

        Args:
            embeddings: Input embeddings [N, D]
            labels: Class labels [N]

        Returns:
            self
        """
        dim = embeddings.shape[1]
        self.centroids = np.zeros((self.n_classes, dim), dtype=np.float32)

        for c in range(self.n_classes):
            mask = labels == c
            if mask.sum() > 0:
                self.centroids[c] = embeddings[mask].mean(axis=0)

        norms = np.linalg.norm(self.centroids, axis=1, keepdims=True)
        self.centroids_normalized = self.centroids / (norms + 1e-8)

        return self

    def to_tensor(self, device: torch.device) -> 'CentroidManager':
        """Convert centroids to PyTorch tensors on specified device."""
        self.centroids_t = torch.tensor(
            self.centroids, dtype=torch.float32, device=device
        )
        self.centroids_norm_t = torch.tensor(
            self.centroids_normalized, dtype=torch.float32, device=device
        )
        return self


class SignalExtractor(nn.Module):
    """
    Neural network that extracts discriminative signal from embeddings.

    The model learns to separate:
    - Signal: Class-discriminative information
    - Noise: Non-discriminative variations

    Architecture:
        - Signal encoder: input_dim -> hidden -> signal_dim
        - Noise encoder: input_dim -> 256 -> 128
        - Decoder: signal_dim -> hidden -> input_dim
        - Full decoder: signal_dim + noise_dim -> input_dim
    """

    def __init__(
        self,
        input_dim: int,
        signal_dim: int = 256,
        hidden_dims: Tuple[int, ...] = (512, 384),
        n_classes: int = 10,
        dropout: float = 0.3
    ):
        """
        Args:
            input_dim: Dimension of input embeddings
            signal_dim: Dimension of signal representation
            hidden_dims: Hidden layer dimensions
            n_classes: Number of classes
            dropout: Dropout rate
        """
        super().__init__()
        self.n_classes = n_classes
        self.input_dim = input_dim
        self.signal_dim = signal_dim

        # Signal encoder
        self.signal_encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.LayerNorm(hidden_dims[1]),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dims[1], signal_dim),
            nn.LayerNorm(signal_dim),
        )

        # Noise encoder
        self.noise_encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout + 0.1),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
        )

        # Signal-only decoder
        self.decoder = nn.Sequential(
            nn.Linear(signal_dim, hidden_dims[1]),
            nn.LayerNorm(hidden_dims[1]),
            nn.GELU(),
            nn.Linear(hidden_dims[1], hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.GELU(),
            nn.Linear(hidden_dims[0], input_dim),
        )

        # Full reconstruction decoder
        self.full_decoder = nn.Sequential(
            nn.Linear(signal_dim + 128, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.GELU(),
            nn.Linear(hidden_dims[0], input_dim),
        )

        # Centroid prediction
        self.centroid_proj = nn.Linear(signal_dim, input_dim)

        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(signal_dim, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, n_classes)
        )

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode input into signal and noise components.

        Args:
            x: Input embeddings [B, input_dim]

        Returns:
            z_signal: Signal representation [B, signal_dim]
            z_noise: Noise representation [B, 128]
        """
        return self.signal_encoder(x), self.noise_encoder(x)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass returning all outputs for training.

        Args:
            x: Input embeddings [B, input_dim]

        Returns:
            Dictionary containing:
                - z_signal: Signal representation
                - z_noise: Noise representation
                - x_recon_signal: Reconstruction from signal only
                - x_recon_full: Full reconstruction
                - centroid_pred: Predicted centroid direction
                - logits: Classification logits
        """
        z_signal, z_noise = self.encode(x)

        return {
            'z_signal': z_signal,
            'z_noise': z_noise,
            'x_recon_signal': self.decoder(z_signal),
            'x_recon_full': self.full_decoder(torch.cat([z_signal, z_noise], dim=-1)),
            'centroid_pred': F.normalize(self.centroid_proj(z_signal), dim=-1),
            'logits': self.classifier(z_signal)
        }

    def get_enhanced_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract enhanced embedding (signal reconstruction).

        Args:
            x: Input embeddings [B, input_dim]

        Returns:
            Enhanced embeddings [B, input_dim]
        """
        z_signal, _ = self.encode(x)
        return self.decoder(z_signal)


class SignalExtractorTrainer:
    """Trainer for SignalExtractor model."""

    def __init__(
        self,
        model: SignalExtractor,
        device: Union[str, torch.device, None] = None,
        lr: float = 1e-3,
        weight_decay: float = 1e-4,
        batch_size: int = 128,
        epochs: int = 100,
        patience: int = 20,
        recon_weight: float = 1.0,
        centroid_weight: float = 2.0,
        contrast_weight: float = 0.5,
        ortho_weight: float = 0.5
    ):
        """
        Args:
            model: SignalExtractor model
            device: Device to train on ('auto', 'cuda', 'mps', 'cpu', or torch.device)
            lr: Learning rate
            weight_decay: Weight decay for optimizer
            batch_size: Batch size
            epochs: Maximum epochs
            patience: Early stopping patience
            recon_weight: Weight for reconstruction loss
            centroid_weight: Weight for centroid prediction loss
            contrast_weight: Weight for contrastive loss
            ortho_weight: Weight for orthogonality loss
        """
        self.device = get_device(device)
        self.model = model.to(self.device)
        self.batch_size = batch_size
        self.epochs = epochs
        self.patience = patience

        # Loss weights
        self.recon_weight = recon_weight
        self.centroid_weight = centroid_weight
        self.contrast_weight = contrast_weight
        self.ortho_weight = ortho_weight

        # Optimizer and scheduler
        self.optimizer = torch.optim.AdamW(
            model.parameters(), lr=lr, weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=epochs
        )

        self.centroid_mgr = None

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> 'SignalExtractorTrainer':
        """
        Train the signal extractor.

        Args:
            X_train: Training embeddings [N, D]
            y_train: Training labels [N]
            X_val: Validation embeddings (optional)
            y_val: Validation labels (optional)

        Returns:
            self
        """
        # Initialize centroid manager
        self.centroid_mgr = CentroidManager(self.model.n_classes)
        self.centroid_mgr.fit(X_train, y_train)
        self.centroid_mgr.to_tensor(self.device)

        # Create data loader
        train_loader = DataLoader(
            TensorDataset(
                torch.tensor(X_train, dtype=torch.float32),
                torch.tensor(y_train, dtype=torch.long)
            ),
            batch_size=self.batch_size,
            shuffle=True
        )

        best_f1 = 0
        best_state = None
        patience_counter = 0

        for epoch in range(self.epochs):
            # Training
            self.model.train()
            epoch_loss = 0

            for x, y in train_loader:
                x, y = x.to(self.device), y.to(self.device)

                self.optimizer.zero_grad()
                out = self.model(x)

                # Compute losses
                loss = self._compute_loss(out, x, y)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

                epoch_loss += loss.item()

            self.scheduler.step()

            # Validation
            if X_val is not None and y_val is not None:
                val_f1 = self._evaluate(X_val, y_val)

                if val_f1 > best_f1 + 1e-4:
                    best_f1 = val_f1
                    best_state = {
                        k: v.cpu().clone() for k, v in self.model.state_dict().items()
                    }
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.patience:
                        print(f"Early stopping at epoch {epoch + 1}")
                        break

        # Restore best model
        if best_state is not None:
            self.model.load_state_dict({
                k: v.to(self.device) for k, v in best_state.items()
            })

        return self

    def _compute_loss(
        self,
        outputs: Dict[str, torch.Tensor],
        x: torch.Tensor,
        y: torch.Tensor
    ) -> torch.Tensor:
        """Compute combined training loss."""
        # Reconstruction losses
        recon_loss = F.mse_loss(outputs['x_recon_signal'], x)
        full_recon_loss = F.mse_loss(outputs['x_recon_full'], x)

        # Centroid alignment loss
        true_cent = self.centroid_mgr.centroids_norm_t[y]
        cent_loss = 1 - F.cosine_similarity(outputs['centroid_pred'], true_cent).mean()

        # Contrastive loss
        all_sims = torch.mm(
            outputs['centroid_pred'],
            self.centroid_mgr.centroids_norm_t.T
        )
        contrast_loss = F.cross_entropy(all_sims / 0.1, y)

        # Classification loss
        cls_loss = F.cross_entropy(outputs['logits'], y)

        # Orthogonality loss (signal and noise should be orthogonal)
        z_s = F.normalize(outputs['z_signal'], dim=-1)
        z_n = F.normalize(outputs['z_noise'], dim=-1)
        ortho_loss = torch.abs(torch.mm(z_s.T, z_n)).mean()

        # Combined loss
        total_loss = (
            self.recon_weight * recon_loss +
            0.5 * full_recon_loss +
            self.centroid_weight * cent_loss +
            self.contrast_weight * contrast_loss +
            cls_loss +
            self.ortho_weight * ortho_loss
        )

        return total_loss

    def _evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Evaluate model on validation set."""
        from sklearn.metrics import f1_score

        self.model.eval()
        with torch.no_grad():
            X_val_t = torch.tensor(X_val, dtype=torch.float32, device=self.device)
            outputs = self.model(X_val_t)
            preds = outputs['logits'].argmax(-1).cpu().numpy()

        return f1_score(y_val, preds, average='macro')

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform embeddings to enhanced representations.

        Args:
            X: Input embeddings [N, D]

        Returns:
            Enhanced embeddings [N, D]
        """
        self.model.eval()

        loader = DataLoader(
            torch.tensor(X, dtype=torch.float32),
            batch_size=256
        )

        enhanced = []
        with torch.no_grad():
            for batch_x in loader:
                batch_x = batch_x.to(self.device)
                enhanced_batch = self.model.get_enhanced_embedding(batch_x)
                enhanced.append(enhanced_batch.cpu())

        enhanced = torch.cat(enhanced, 0).numpy()

        # Normalize
        enhanced = enhanced / (np.linalg.norm(enhanced, axis=1, keepdims=True) + 1e-8)

        return enhanced
