"""Tests for alpamayo_tools.inference module."""

from __future__ import annotations

import numpy as np
import pytest


class TestPredictionResult:
    """Tests for PredictionResult dataclass."""

    def test_prediction_result_creation(self):
        """Test creating a PredictionResult."""
        from alpamayo_tools.inference import PredictionResult

        trajectory_xyz = np.random.randn(64, 3).astype(np.float32)
        trajectory_rot = np.random.randn(64, 3, 3).astype(np.float32)
        reasoning_text = "The vehicle ahead is braking."

        result = PredictionResult(
            trajectory_xyz=trajectory_xyz,
            trajectory_rot=trajectory_rot,
            reasoning_text=reasoning_text,
        )

        assert result.trajectory_xyz.shape == (64, 3)
        assert result.trajectory_rot.shape == (64, 3, 3)
        assert result.reasoning_text == reasoning_text
        assert result.all_trajectories_xyz is None
        assert result.all_trajectories_rot is None

    def test_prediction_result_with_samples(self):
        """Test PredictionResult with multiple trajectory samples."""
        from alpamayo_tools.inference import PredictionResult

        num_samples = 6
        trajectory_xyz = np.random.randn(64, 3).astype(np.float32)
        trajectory_rot = np.random.randn(64, 3, 3).astype(np.float32)
        all_xyz = np.random.randn(num_samples, 64, 3).astype(np.float32)
        all_rot = np.random.randn(num_samples, 64, 3, 3).astype(np.float32)

        result = PredictionResult(
            trajectory_xyz=trajectory_xyz,
            trajectory_rot=trajectory_rot,
            reasoning_text="Test reasoning",
            all_trajectories_xyz=all_xyz,
            all_trajectories_rot=all_rot,
        )

        assert result.all_trajectories_xyz.shape == (num_samples, 64, 3)
        assert result.all_trajectories_rot.shape == (num_samples, 64, 3, 3)


class TestAlpamayoPredictor:
    """Tests for AlpamayoPredictor.

    Note: These tests use mocks since the actual model requires
    ~24GB GPU and the alpamayo_r1 package.
    """

    def test_from_pretrained_import_error(self, monkeypatch):
        """Test helpful error when alpamayo_r1 not installed."""
        import sys
        import builtins

        # Remove alpamayo_r1 from modules if present
        modules_to_remove = [k for k in sys.modules if k.startswith("alpamayo_r1")]
        for mod in modules_to_remove:
            monkeypatch.delitem(sys.modules, mod, raising=False)

        # Mock the import to fail
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name.startswith("alpamayo_r1"):
                raise ImportError("No module named 'alpamayo_r1'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        from alpamayo_tools.inference import AlpamayoPredictor

        with pytest.raises(ImportError, match="alpamayo_r1"):
            AlpamayoPredictor.from_pretrained()

    def test_predictor_attributes(self):
        """Test AlpamayoPredictor attributes with mock model."""
        import torch
        from unittest.mock import MagicMock
        from alpamayo_tools.inference import AlpamayoPredictor

        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_tokenizer = MagicMock()

        predictor = AlpamayoPredictor(
            model=mock_model,
            processor=mock_processor,
            tokenizer=mock_tokenizer,
            device="cpu",
            dtype=torch.float32,
        )

        assert predictor.model is mock_model
        assert predictor.processor is mock_processor
        assert predictor.device == torch.device("cpu")
        assert predictor.dtype == torch.float32


class TestPredictorIntegration:
    """Integration tests for AlpamayoPredictor.

    These tests are skipped unless alpamayo_r1 is installed.
    """

    @pytest.fixture
    def predictor(self):
        """Fixture that skips if alpamayo_r1 not available."""
        pytest.importorskip("alpamayo_r1")
        pytest.importorskip("transformers")

        import torch

        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        from alpamayo_tools.inference import AlpamayoPredictor

        return AlpamayoPredictor.from_pretrained()

    @pytest.mark.skip(reason="Requires GPU and model download")
    def test_predict_from_clip(self, predictor):
        """Test full inference pipeline (requires model)."""
        result = predictor.predict_from_clip("test_clip_id")
        assert result.trajectory_xyz.shape == (64, 3)
        assert isinstance(result.reasoning_text, str)
