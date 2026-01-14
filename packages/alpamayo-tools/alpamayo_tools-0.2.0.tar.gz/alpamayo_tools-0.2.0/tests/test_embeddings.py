"""Tests for alpamayo_tools.embeddings module."""

from __future__ import annotations

import numpy as np
import pytest


class TestCoCEmbedder:
    """Tests for CoCEmbedder."""

    @pytest.fixture
    def embedder(self):
        """Fixture to create embedder (skips if sentence-transformers not installed)."""
        pytest.importorskip("sentence_transformers")
        from alpamayo_tools.embeddings import CoCEmbedder

        return CoCEmbedder()

    def test_embed_single(self, embedder):
        """Test embedding a single text."""
        text = "The vehicle ahead is braking. Reduce speed."
        embedding = embedder.embed_single(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (embedder.embedding_dim,)
        assert embedding.dtype == np.float32

    def test_embed_batch(self, embedder):
        """Test embedding multiple texts."""
        texts = [
            "The vehicle ahead is braking.",
            "Clear road ahead, maintain speed.",
            "Pedestrian crossing detected.",
        ]
        embeddings = embedder.embed(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, embedder.embedding_dim)
        assert embeddings.dtype == np.float32

    def test_embed_empty_string(self, embedder):
        """Test handling of empty strings."""
        texts = ["Valid text", "", "Another valid text"]
        embeddings = embedder.embed(texts)

        # Should not raise, empty strings replaced with placeholder
        assert embeddings.shape == (3, embedder.embedding_dim)
        # All embeddings should be valid (not NaN)
        assert not np.any(np.isnan(embeddings))

    def test_embed_whitespace_only(self, embedder):
        """Test handling of whitespace-only strings."""
        texts = ["Valid text", "   ", "\t\n"]
        embeddings = embedder.embed(texts)

        assert embeddings.shape == (3, embedder.embedding_dim)
        assert not np.any(np.isnan(embeddings))

    def test_embedding_dimension(self, embedder):
        """Test that embedding dimension is correct."""
        assert embedder.embedding_dim == 384  # all-MiniLM-L6-v2 dimension

    def test_normalized_embeddings(self, embedder):
        """Test that embeddings are L2 normalized by default."""
        text = "Test text for normalization."
        embedding = embedder.embed_single(text, normalize=True)

        # L2 norm should be approximately 1
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-5)

    def test_unnormalized_embeddings(self, embedder):
        """Test unnormalized embeddings."""
        text = "Test text for normalization."
        embedding = embedder.embed_single(text, normalize=False)

        # L2 norm should NOT be exactly 1 (unless by coincidence)
        norm = np.linalg.norm(embedding)
        # Just check it's a valid vector
        assert not np.any(np.isnan(embedding))

    def test_device_property(self, embedder):
        """Test device property."""
        device = embedder.device
        # Device can be "cpu", "cuda", "cuda:0", "mps", "mps:0", etc.
        assert any(d in device for d in ["cpu", "cuda", "mps"])

    def test_embed_large_batch(self, embedder):
        """Test embedding a large batch (tests batching)."""
        texts = [f"Sample text number {i}" for i in range(100)]
        embeddings = embedder.embed(texts, show_progress=False)

        assert embeddings.shape == (100, embedder.embedding_dim)

    def test_embed_similar_texts(self, embedder):
        """Test that similar texts have similar embeddings."""
        text1 = "The car ahead is slowing down."
        text2 = "The vehicle in front is reducing speed."
        text3 = "The weather today is sunny and warm."

        embeddings = embedder.embed([text1, text2, text3], normalize=True)

        # Cosine similarity (since normalized, dot product = cosine)
        sim_12 = np.dot(embeddings[0], embeddings[1])
        sim_13 = np.dot(embeddings[0], embeddings[2])

        # Similar texts should have higher similarity
        assert sim_12 > sim_13


class TestCoCEmbedderImportError:
    """Tests for import error handling."""

    def test_import_error_message(self, monkeypatch):
        """Test that helpful error message is shown when sentence-transformers missing."""
        # Mock sentence_transformers to raise ImportError
        import sys

        monkeypatch.setitem(sys.modules, "sentence_transformers", None)

        # Need to reload the module to trigger the import
        import importlib
        import alpamayo_tools.embeddings

        # Force reimport
        importlib.reload(alpamayo_tools.embeddings)

        with pytest.raises(ImportError, match="sentence-transformers"):
            alpamayo_tools.embeddings.CoCEmbedder()
