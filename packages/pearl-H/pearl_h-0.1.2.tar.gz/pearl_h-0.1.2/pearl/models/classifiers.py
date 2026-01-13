"""
Standard classifiers for PEARL evaluation.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class MLPClassifier(nn.Module):
    """Multi-layer perceptron classifier."""

    def __init__(
        self,
        input_dim: int,
        n_classes: int,
        hidden_dims: Tuple[int, ...] = (512, 256),
        dropout: float = 0.3
    ):
        """
        Args:
            input_dim: Input dimension
            n_classes: Number of classes
            hidden_dims: Hidden layer dimensions
            dropout: Dropout rate
        """
        super().__init__()

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, n_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.net(x)


class TransformerClassifier(nn.Module):
    """
    Transformer-based classifier.

    Splits input into chunks and uses transformer encoder.
    """

    def __init__(
        self,
        input_dim: int,
        n_classes: int,
        chunk_size: int = 64,
        n_heads: int = 8,
        n_layers: int = 2,
        dropout: float = 0.3
    ):
        """
        Args:
            input_dim: Input dimension
            n_classes: Number of classes
            chunk_size: Size of each chunk
            n_heads: Number of attention heads
            n_layers: Number of transformer layers
            dropout: Dropout rate
        """
        super().__init__()
        self.input_dim = input_dim
        self.chunk_size = chunk_size

        # Calculate number of chunks needed
        self.n_chunks = (input_dim + chunk_size - 1) // chunk_size
        self.padded_dim = self.n_chunks * chunk_size
        self.need_padding = self.padded_dim != input_dim

        # Input projection if padding needed
        self.input_proj = (
            nn.Linear(input_dim, self.padded_dim)
            if self.need_padding
            else nn.Identity()
        )

        # CLS token and positional embeddings
        self.cls_token = nn.Parameter(torch.randn(1, 1, chunk_size))
        self.pos_embed = nn.Parameter(
            torch.randn(1, self.n_chunks + 1, chunk_size) * 0.02
        )

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=chunk_size,
            nhead=n_heads,
            dim_feedforward=chunk_size * 4,
            dropout=dropout,
            activation='gelu',
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Classifier head
        self.classifier = nn.Sequential(
            nn.LayerNorm(chunk_size),
            nn.Linear(chunk_size, n_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor [B, input_dim]

        Returns:
            logits: [B, n_classes]
        """
        B = x.shape[0]

        # Project to padded dimension if needed
        x = self.input_proj(x)

        # Reshape to chunks [B, n_chunks, chunk_size]
        x = x.view(B, self.n_chunks, self.chunk_size)

        # Add CLS token
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)  # [B, n_chunks + 1, chunk_size]

        # Add positional embeddings
        x = x + self.pos_embed

        # Transform
        x = self.transformer(x)

        # Classify using CLS token
        return self.classifier(x[:, 0])
