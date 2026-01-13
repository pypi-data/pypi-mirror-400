"""
RAG Classifier: Retrieval-Augmented Generation for Classification
Uses cross-attention over retrieved neighbors for enhanced prediction.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import f1_score
from typing import Optional, Tuple, Union

from pearl.utils.device import get_device


class RAGClassifier(nn.Module):
    """
    Retrieval-Augmented Classification with Cross-Attention.

    For each query, retrieves k nearest neighbors from training set
    and uses cross-attention to aggregate their information for prediction.
    """

    def __init__(
        self,
        embed_dim: int,
        n_classes: int,
        hidden_dim: int = 256,
        n_heads: int = 4,
        n_layers: int = 2,
        k: int = 8,
        dropout: float = 0.3
    ):
        """
        Args:
            embed_dim: Dimension of input embeddings
            n_classes: Number of classes
            hidden_dim: Hidden dimension for transformers
            n_heads: Number of attention heads
            n_layers: Number of cross-attention layers
            k: Number of neighbors to retrieve
            dropout: Dropout rate
        """
        super().__init__()
        self.embed_dim = embed_dim
        self.n_classes = n_classes
        self.hidden_dim = hidden_dim
        self.k = k

        # Project query embedding to hidden space
        self.query_proj = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )

        # Project neighbor embeddings + labels to hidden space
        self.neighbor_proj = nn.Sequential(
            nn.Linear(embed_dim + n_classes, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
        )

        # Project similarity scores
        self.sim_proj = nn.Sequential(
            nn.Linear(1, hidden_dim // 4),
            nn.GELU(),
        )

        # Cross-attention layers (query attends to neighbors)
        self.cross_attention_layers = nn.ModuleList([
            nn.MultiheadAttention(
                hidden_dim, n_heads, dropout=dropout, batch_first=True
            )
            for _ in range(n_layers)
        ])

        self.cross_norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(n_layers)
        ])

        self.cross_ffn = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim * 2),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.Dropout(dropout),
            )
            for _ in range(n_layers)
        ])

        self.ffn_norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(n_layers)
        ])

        # Self-attention for neighbors
        self.neighbor_self_attn = nn.MultiheadAttention(
            hidden_dim, n_heads, dropout=dropout, batch_first=True
        )
        self.neighbor_norm = nn.LayerNorm(hidden_dim)

        # Final classifier
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_classes)
        )

        # Retrieval index (set during training)
        self.knn_index = None
        self.train_embeddings = None
        self.train_labels = None

    def set_retrieval_index(
        self,
        train_embeddings: np.ndarray,
        train_labels: np.ndarray
    ):
        """
        Set up retrieval index from training data.

        Args:
            train_embeddings: Training embeddings [N, D]
            train_labels: Training labels [N]
        """
        self.train_embeddings = train_embeddings
        self.train_labels = train_labels

        # Build KNN index
        self.knn_index = NearestNeighbors(
            n_neighbors=self.k,
            metric='cosine',
            n_jobs=-1
        )

        if isinstance(train_embeddings, torch.Tensor):
            self.knn_index.fit(train_embeddings.cpu().numpy())
        else:
            self.knn_index.fit(train_embeddings)

    def retrieve_neighbors(
        self,
        query_embeddings: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Retrieve k nearest neighbors for each query.

        Args:
            query_embeddings: Query embeddings [B, D]

        Returns:
            indices: Neighbor indices [B, k]
            similarities: Cosine similarities [B, k]
        """
        if isinstance(query_embeddings, torch.Tensor):
            query_np = query_embeddings.detach().cpu().numpy()
        else:
            query_np = query_embeddings

        distances, indices = self.knn_index.kneighbors(query_np)
        similarities = 1 - distances

        return indices, similarities

    def forward(
        self,
        query_embed: torch.Tensor,
        neighbor_embeds: Optional[torch.Tensor] = None,
        neighbor_labels: Optional[torch.Tensor] = None,
        neighbor_sims: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            query_embed: Query embeddings [B, embed_dim]
            neighbor_embeds: Neighbor embeddings [B, k, embed_dim] (optional)
            neighbor_labels: Neighbor labels [B, k] (optional)
            neighbor_sims: Neighbor similarities [B, k] (optional)

        Returns:
            logits: Classification logits [B, n_classes]
        """
        B = query_embed.shape[0]
        device = query_embed.device

        # Retrieve neighbors if not provided
        if neighbor_embeds is None:
            indices, sims = self.retrieve_neighbors(query_embed)

            # Get neighbor embeddings
            if isinstance(self.train_embeddings, torch.Tensor):
                neighbor_embeds = self.train_embeddings[indices.flatten()].view(
                    B, self.k, -1
                )
            else:
                neighbor_embeds = torch.tensor(
                    self.train_embeddings[indices.flatten()].reshape(B, self.k, -1),
                    dtype=torch.float32,
                    device=device
                )

            # Get neighbor labels
            if isinstance(self.train_labels, torch.Tensor):
                neighbor_labels = self.train_labels[indices.flatten()].view(B, self.k)
            else:
                neighbor_labels = torch.tensor(
                    self.train_labels[indices.flatten()].reshape(B, self.k),
                    dtype=torch.long,
                    device=device
                )

            neighbor_sims = torch.tensor(sims, dtype=torch.float32, device=device)

        # Ensure everything is on the right device
        neighbor_embeds = neighbor_embeds.to(device)
        neighbor_labels = neighbor_labels.to(device)
        neighbor_sims = neighbor_sims.to(device)

        # Project query to hidden space [B, 1, hidden_dim]
        query_hidden = self.query_proj(query_embed).unsqueeze(1)

        # Encode neighbor information
        # Concatenate embeddings with one-hot labels
        label_onehot = F.one_hot(neighbor_labels, self.n_classes).float()
        neighbor_features = torch.cat([neighbor_embeds, label_onehot], dim=-1)
        neighbor_hidden = self.neighbor_proj(neighbor_features)

        # Add similarity information
        sim_features = self.sim_proj(neighbor_sims.unsqueeze(-1))
        neighbor_hidden = neighbor_hidden + F.pad(
            sim_features,
            (0, self.hidden_dim - self.hidden_dim // 4)
        )

        # Self-attention among neighbors
        neighbor_attended, _ = self.neighbor_self_attn(
            neighbor_hidden, neighbor_hidden, neighbor_hidden
        )
        neighbor_hidden = self.neighbor_norm(neighbor_hidden + neighbor_attended)

        # Cross-attention: query attends to neighbors
        for attn, norm, ffn, ffn_norm in zip(
            self.cross_attention_layers,
            self.cross_norms,
            self.cross_ffn,
            self.ffn_norms
        ):
            attended, _ = attn(query_hidden, neighbor_hidden, neighbor_hidden)
            query_hidden = norm(query_hidden + attended)
            query_hidden = ffn_norm(query_hidden + ffn(query_hidden))

        # Classify
        query_hidden = query_hidden.squeeze(1)  # [B, hidden_dim]
        logits = self.classifier(query_hidden)

        return logits


class RAGClassifierWrapper:
    """
    Wrapper for training and using RAG classifier.

    Provides sklearn-like interface.
    """

    def __init__(
        self,
        embed_dim: int,
        n_classes: int,
        k: int = 8,
        hidden_dim: int = 256,
        n_heads: int = 4,
        n_layers: int = 2,
        dropout: float = 0.3,
        device: Union[str, torch.device, None] = None
    ):
        """
        Args:
            embed_dim: Dimension of input embeddings
            n_classes: Number of classes
            k: Number of neighbors to retrieve
            hidden_dim: Hidden dimension
            n_heads: Number of attention heads
            n_layers: Number of transformer layers
            dropout: Dropout rate
            device: Device to use ('auto', 'cuda', 'mps', 'cpu', or torch.device)
        """
        self.embed_dim = embed_dim
        self.n_classes = n_classes
        self.k = k
        self.device = get_device(device)

        self.model = RAGClassifier(
            embed_dim=embed_dim,
            n_classes=n_classes,
            hidden_dim=hidden_dim,
            n_heads=n_heads,
            n_layers=n_layers,
            k=k,
            dropout=dropout
        ).to(self.device)

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
        patience: int = 20
    ) -> 'RAGClassifierWrapper':
        """
        Train the RAG classifier.

        Args:
            X_train: Training embeddings
            y_train: Training labels
            X_val: Validation embeddings (optional)
            y_val: Validation labels (optional)
            lr: Learning rate
            weight_decay: Weight decay
            batch_size: Batch size
            epochs: Maximum epochs
            patience: Early stopping patience

        Returns:
            self
        """
        # Set up retrieval index
        train_embeds_t = torch.tensor(X_train, dtype=torch.float32, device=self.device)
        train_labels_t = torch.tensor(y_train, dtype=torch.long, device=self.device)
        self.model.set_retrieval_index(train_embeds_t, train_labels_t)

        # Optimizer
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=lr,
            weight_decay=weight_decay
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=epochs
        )

        # Data loader
        train_dataset = TensorDataset(train_embeds_t, train_labels_t)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        best_f1 = 0
        best_state = None
        patience_counter = 0

        for epoch in range(epochs):
            # Training
            self.model.train()
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                logits = self.model(batch_x)
                loss = F.cross_entropy(logits, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()

            scheduler.step()

            # Validation
            if X_val is not None and y_val is not None:
                val_f1 = self.evaluate_f1(X_val, y_val)

                if val_f1 > best_f1 + 1e-4:
                    best_f1 = val_f1
                    best_state = {
                        k: v.cpu().clone() for k, v in self.model.state_dict().items()
                    }
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        break

        # Restore best model
        if best_state is not None:
            self.model.load_state_dict({
                k: v.to(self.device) for k, v in best_state.items()
            })

        return self

    def evaluate_f1(self, X: np.ndarray, y: np.ndarray) -> float:
        """Evaluate macro F1 score."""
        preds = self.predict(X)
        return f1_score(y, preds, average='macro')

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.predict_proba(X).argmax(axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        self.model.eval()

        if isinstance(X, np.ndarray):
            X = torch.tensor(X, dtype=torch.float32)

        all_probs = []
        with torch.no_grad():
            for i in range(0, len(X), 256):
                batch = X[i:i + 256].to(self.device)
                logits = self.model(batch)
                probs = F.softmax(logits, dim=-1).cpu().numpy()
                all_probs.append(probs)

        return np.vstack(all_probs)
