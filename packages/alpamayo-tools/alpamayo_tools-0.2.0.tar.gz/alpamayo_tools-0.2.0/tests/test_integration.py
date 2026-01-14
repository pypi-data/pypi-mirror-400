"""Integration tests using real PhysicalAI-AV data.

These tests are skipped by default. To run them:

    RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py -v

You need:
1. HuggingFace access to nvidia/PhysicalAI-Autonomous-Vehicles
2. Network access for streaming (or cached data)
3. For inference tests: alpamayo_r1 package + GPU with 24GB+ VRAM
"""

from __future__ import annotations

import os

import numpy as np
import pytest
import torch

# Skip all tests in this module unless RUN_INTEGRATION_TESTS=1 env var is set
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests require RUN_INTEGRATION_TESTS=1 environment variable",
)

# Sample clip IDs from PhysicalAI-AV (known to exist in US daytime subset)
SAMPLE_CLIP_IDS = [
    "f3985b66-6f95-4089-b455-b304cb5349ea",
    "a77719ff-c52d-48ac-afb3-ba48db2548f4",
]


class TestDataloaderIntegration:
    """Integration tests for PhysicalAIDataset with real data."""

    @pytest.fixture
    def real_dataset(self):
        """Create dataset with real clip IDs."""
        from alpamayo_tools import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(
            clip_ids=SAMPLE_CLIP_IDS[:1],  # Just one clip for speed
            cameras=("camera_front_wide_120fov",),
            num_frames=2,
            stream=True,
        )
        dataset = PhysicalAIDataset(config)
        yield dataset
        dataset.close()

    def test_load_real_clip(self, real_dataset):
        """Test loading a real clip from PhysicalAI-AV."""
        sample = real_dataset[0]

        # Verify structure
        assert "frames" in sample
        assert "ego_history_xyz" in sample
        assert "ego_future_xyz" in sample

        # Verify shapes
        assert sample["frames"].ndim == 5  # (N_cameras, num_frames, 3, H, W)
        assert sample["ego_history_xyz"].shape == (16, 3)
        assert sample["ego_future_xyz"].shape == (64, 3)

        # Verify frames are valid images
        assert sample["frames"].dtype == torch.uint8
        assert sample["frames"].min() >= 0
        assert sample["frames"].max() <= 255

        # Verify trajectory is in ego frame (t0 should be at origin)
        t0_pos = sample["ego_history_xyz"][-1]
        assert torch.allclose(t0_pos, torch.zeros(3), atol=1e-4)

    def test_multiple_cameras(self):
        """Test loading multiple cameras."""
        from alpamayo_tools import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(
            clip_ids=SAMPLE_CLIP_IDS[:1],
            cameras=(
                "camera_front_wide_120fov",
                "camera_front_tele_30fov",
            ),
            num_frames=2,
            stream=True,
        )

        with PhysicalAIDataset(config) as dataset:
            sample = dataset[0]
            assert sample["frames"].shape[0] == 2  # 2 cameras
            assert sample["camera_indices"].shape == (2,)

    def test_dataloader_with_real_data(self):
        """Test DataLoader integration."""
        from torch.utils.data import DataLoader

        from alpamayo_tools import DatasetConfig, PhysicalAIDataset, collate_fn

        config = DatasetConfig(
            clip_ids=SAMPLE_CLIP_IDS,
            cameras=("camera_front_wide_120fov",),
            num_frames=2,
            stream=True,
        )

        dataset = PhysicalAIDataset(config)
        loader = DataLoader(
            dataset,
            batch_size=2,
            shuffle=False,
            collate_fn=collate_fn,
        )

        batch = next(iter(loader))
        assert batch["frames"].shape[0] == 2  # batch size
        assert len(batch["clip_ids"]) == 2

        dataset.close()


class TestEmbeddingsIntegration:
    """Integration tests for CoCEmbedder with realistic inputs."""

    def test_embed_real_coc_samples(self):
        """Test embedding realistic CoC reasoning texts."""
        from alpamayo_tools import CoCEmbedder

        # Real-ish CoC examples (from Alpamayo paper)
        coc_samples = [
            "The vehicle ahead is braking sharply. Reduce speed immediately to maintain safe following distance.",
            "Construction zone detected on the right. Nudge left to increase clearance from cones.",
            "Pedestrian waiting at crosswalk. Slow down and prepare to yield.",
            "Green light ahead. Proceeding through intersection at current speed.",
            "Merging vehicle from on-ramp. Adjust speed to allow safe merge.",
        ]

        embedder = CoCEmbedder()
        embeddings = embedder.embed(coc_samples)

        # Check embeddings are valid
        assert embeddings.shape == (5, 384)
        assert not np.any(np.isnan(embeddings))

        # Check similarity matrix is valid
        sim_matrix = embeddings @ embeddings.T
        assert sim_matrix[0, 0] == pytest.approx(1.0, abs=1e-5)  # self-similarity = 1
        assert sim_matrix.shape == (5, 5)
        # All similarities should be between -1 and 1 (cosine similarity)
        assert sim_matrix.min() >= -1.0
        assert sim_matrix.max() <= 1.0 + 1e-5


class TestInferenceIntegration:
    """Integration tests for AlpamayoPredictor.

    These require:
    - alpamayo_r1 package installed
    - GPU with 24GB+ VRAM
    - HuggingFace access to nvidia/Alpamayo-R1-10B
    """

    @pytest.fixture
    def predictor(self):
        """Load predictor (skips if requirements not met)."""
        pytest.importorskip("alpamayo_r1")

        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        # Check VRAM
        props = torch.cuda.get_device_properties(0)
        if props.total_memory < 24 * 1024**3:  # 24GB
            pytest.skip(f"GPU has only {props.total_memory / 1024**3:.1f}GB VRAM, need 24GB+")

        from alpamayo_tools.inference import AlpamayoPredictor

        return AlpamayoPredictor.from_pretrained()

    def test_predict_from_real_clip(self, predictor):
        """Test inference on a real clip."""
        result = predictor.predict_from_clip(
            SAMPLE_CLIP_IDS[0],
            t0_us=5_100_000,
            num_samples=1,
        )

        # Check trajectory output
        assert result.trajectory_xyz.shape == (64, 3)
        assert result.trajectory_rot.shape == (64, 3, 3)

        # Check reasoning text is non-empty
        assert isinstance(result.reasoning_text, str)
        assert len(result.reasoning_text) > 0

        # Trajectory should be reasonable (not NaN, not huge)
        assert not np.any(np.isnan(result.trajectory_xyz))
        assert np.abs(result.trajectory_xyz).max() < 1000  # meters

    def test_predict_with_dataset_sample(self, predictor):
        """Test inference using PhysicalAIDataset sample."""
        from alpamayo_tools import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(
            clip_ids=SAMPLE_CLIP_IDS[:1],
            num_frames=4,
            stream=True,
        )

        with PhysicalAIDataset(config) as dataset:
            sample = dataset[0]
            result = predictor.predict_from_dataset_sample(sample)

            assert result.trajectory_xyz.shape == (64, 3)
            assert len(result.reasoning_text) > 0

    def test_multiple_trajectory_samples(self, predictor):
        """Test generating multiple trajectory samples."""
        result = predictor.predict_from_clip(
            SAMPLE_CLIP_IDS[0],
            t0_us=5_100_000,
            num_samples=3,
        )

        assert result.all_trajectories_xyz.shape == (3, 64, 3)
        assert result.all_trajectories_rot.shape == (3, 64, 3, 3)
