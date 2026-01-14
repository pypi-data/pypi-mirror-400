"""Chain-of-Cognition text embedding utilities."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import numpy.typing as npt


class CoCEmbedder:
    """Embed Chain-of-Cognition reasoning text using sentence-transformers.

    This class provides a simple interface for embedding Alpamayo's CoC reasoning
    traces using sentence-transformers models.

    Example:
        >>> embedder = CoCEmbedder()
        >>> texts = ["The vehicle ahead is braking...", "Clear road ahead..."]
        >>> embeddings = embedder.embed(texts)
        >>> print(embeddings.shape)  # (2, 384)

    Notes:
        - Uses sentence-transformers/all-MiniLM-L6-v2 by default (384-dim embeddings)
        - Empty strings are replaced with a placeholder to avoid embedding errors
        - Supports GPU acceleration when available
    """

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str | None = None,
        batch_size: int = 32,
    ) -> None:
        """Initialize the embedder.

        Args:
            model_name: HuggingFace model ID for sentence-transformers
            device: Device for inference (None for auto-detect)
            batch_size: Batch size for embedding

        Raises:
            ImportError: If sentence-transformers is not installed
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required for CoCEmbedder. "
                "Install with: pip install alpamayo-tools[embeddings]"
            ) from e

        self.model_name = model_name
        self.batch_size = batch_size

        self.model = SentenceTransformer(model_name, device=device)
        self._embedding_dim = self.model.get_sentence_embedding_dimension()

    @property
    def embedding_dim(self) -> int:
        """Dimension of output embeddings."""
        return self._embedding_dim

    @property
    def device(self) -> str:
        """Device the model is running on."""
        return str(self.model.device)

    def embed(
        self,
        texts: Sequence[str],
        show_progress: bool = False,
        normalize: bool = True,
    ) -> npt.NDArray[np.float32]:
        """Embed a list of texts.

        Args:
            texts: List of reasoning texts to embed
            show_progress: Show progress bar during embedding
            normalize: L2 normalize embeddings (recommended for similarity)

        Returns:
            Array of shape (N, embedding_dim) with embeddings
        """
        # Handle empty strings - replace with placeholder
        processed_texts = [
            t if t and t.strip() else "No reasoning provided." for t in texts
        ]

        embeddings = self.model.encode(
            processed_texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
        )

        return embeddings.astype(np.float32)

    def embed_single(self, text: str, normalize: bool = True) -> npt.NDArray[np.float32]:
        """Embed a single text.

        Args:
            text: Reasoning text to embed
            normalize: L2 normalize embedding

        Returns:
            Array of shape (embedding_dim,) with embedding
        """
        return self.embed([text], normalize=normalize)[0]

    def to(self, device: str) -> "CoCEmbedder":
        """Move the model to a different device.

        Args:
            device: Target device (e.g., "cuda", "cpu", "cuda:0")

        Returns:
            Self for method chaining
        """
        self.model = self.model.to(device)
        return self
