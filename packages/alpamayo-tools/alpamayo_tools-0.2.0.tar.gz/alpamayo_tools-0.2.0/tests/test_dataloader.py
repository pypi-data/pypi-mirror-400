"""Tests for alpamayo_tools.dataloader module."""

from __future__ import annotations

import numpy as np
import pytest
import torch


class TestDatasetConfig:
    """Tests for DatasetConfig."""

    def test_config_with_clip_ids(self, sample_clip_ids, mock_physical_ai_av):
        """Test creating config with clip_ids list."""
        from alpamayo_tools.dataloader import DatasetConfig

        config = DatasetConfig(clip_ids=sample_clip_ids)
        assert config.clip_ids == sample_clip_ids

    def test_config_with_clip_ids_file(self, temp_clip_ids_file, mock_physical_ai_av):
        """Test creating config with clip_ids_file."""
        from alpamayo_tools.dataloader import DatasetConfig

        config = DatasetConfig(clip_ids_file=temp_clip_ids_file)
        assert config.clip_ids is None
        assert config.clip_ids_file == temp_clip_ids_file

    def test_config_validation_no_clips(self, mock_physical_ai_av):
        """Test that config requires either clip_ids or clip_ids_file."""
        from alpamayo_tools.dataloader import DatasetConfig

        with pytest.raises(ValueError, match="Must specify either"):
            DatasetConfig()

    def test_config_validation_both_clips(self, sample_clip_ids, temp_clip_ids_file, mock_physical_ai_av):
        """Test that config rejects both clip_ids and clip_ids_file."""
        from alpamayo_tools.dataloader import DatasetConfig

        with pytest.raises(ValueError, match="Cannot specify both"):
            DatasetConfig(clip_ids=sample_clip_ids, clip_ids_file=temp_clip_ids_file)

    def test_config_default_values(self, sample_clip_ids, mock_physical_ai_av):
        """Test default configuration values."""
        from alpamayo_tools.dataloader import DatasetConfig, DEFAULT_CAMERAS

        config = DatasetConfig(clip_ids=sample_clip_ids)
        assert config.t0_us == 5_100_000
        assert config.num_history_steps == 16
        assert config.num_future_steps == 64
        assert config.time_step_s == 0.1
        assert config.num_frames == 4
        assert config.cameras == DEFAULT_CAMERAS
        assert config.include_future is True


class TestPhysicalAIDataset:
    """Tests for PhysicalAIDataset."""

    def test_dataset_length(self, mock_dataset_config, mock_physical_ai_av):
        """Test dataset length matches clip_ids."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        assert len(dataset) == len(mock_dataset_config.clip_ids)

    def test_dataset_getitem_keys(self, mock_dataset_config, mock_physical_ai_av):
        """Test that __getitem__ returns expected keys."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        expected_keys = {
            "clip_id",
            "t0_us",
            "frames",
            "camera_indices",
            "ego_history_xyz",
            "ego_history_rot",
            "ego_future_xyz",
            "ego_future_rot",
            "frame_timestamps",
        }
        assert set(sample.keys()) == expected_keys

    def test_dataset_getitem_shapes(self, mock_dataset_config, mock_physical_ai_av):
        """Test that __getitem__ returns correct tensor shapes."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        config = mock_dataset_config
        n_cameras = len(config.cameras)

        # frames: (N_cameras, num_frames, 3, H, W)
        assert sample["frames"].shape[0] == n_cameras
        assert sample["frames"].shape[1] == config.num_frames
        assert sample["frames"].shape[2] == 3  # RGB

        # camera_indices: (N_cameras,)
        assert sample["camera_indices"].shape == (n_cameras,)

        # ego_history_xyz: (num_history_steps, 3)
        assert sample["ego_history_xyz"].shape == (config.num_history_steps, 3)

        # ego_history_rot: (num_history_steps, 3, 3)
        assert sample["ego_history_rot"].shape == (config.num_history_steps, 3, 3)

        # ego_future_xyz: (num_future_steps, 3)
        assert sample["ego_future_xyz"].shape == (config.num_future_steps, 3)

        # ego_future_rot: (num_future_steps, 3, 3)
        assert sample["ego_future_rot"].shape == (config.num_future_steps, 3, 3)

    def test_dataset_getitem_types(self, mock_dataset_config, mock_physical_ai_av):
        """Test that __getitem__ returns correct types."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        assert isinstance(sample["clip_id"], str)
        assert isinstance(sample["t0_us"], int)
        assert isinstance(sample["frames"], torch.Tensor)
        assert isinstance(sample["camera_indices"], torch.Tensor)
        assert isinstance(sample["ego_history_xyz"], torch.Tensor)
        assert isinstance(sample["ego_history_rot"], torch.Tensor)

    def test_dataset_no_future(self, sample_clip_ids, mock_physical_ai_av):
        """Test dataset without future trajectory."""
        from alpamayo_tools.dataloader import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(clip_ids=sample_clip_ids, include_future=False)
        dataset = PhysicalAIDataset(config)
        sample = dataset[0]

        assert sample["ego_future_xyz"] is None
        assert sample["ego_future_rot"] is None

    def test_dataset_load_from_parquet(self, temp_clip_ids_file, mock_physical_ai_av):
        """Test loading clip IDs from parquet file."""
        from alpamayo_tools.dataloader import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(clip_ids_file=temp_clip_ids_file)
        dataset = PhysicalAIDataset(config)
        assert len(dataset) == 3  # SAMPLE_CLIP_IDS has 3 items

    def test_dataset_load_from_txt(self, temp_clip_ids_txt, mock_physical_ai_av):
        """Test loading clip IDs from text file."""
        from alpamayo_tools.dataloader import DatasetConfig, PhysicalAIDataset

        config = DatasetConfig(clip_ids_file=temp_clip_ids_txt)
        dataset = PhysicalAIDataset(config)
        assert len(dataset) == 3

    def test_dataset_context_manager(self, mock_dataset_config, mock_physical_ai_av):
        """Test dataset context manager."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        with PhysicalAIDataset(mock_dataset_config) as dataset:
            _ = dataset[0]
        # Should not raise after context exit

    def test_dataset_close(self, mock_dataset_config, mock_physical_ai_av):
        """Test dataset close method."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        _ = dataset[0]
        dataset.close()
        # Should be safe to close multiple times
        dataset.close()


class TestCollateFn:
    """Tests for collate_fn."""

    def test_collate_fn_batches(self, mock_dataset_config, mock_physical_ai_av):
        """Test collate_fn produces correct batch."""
        from alpamayo_tools.dataloader import PhysicalAIDataset, collate_fn

        dataset = PhysicalAIDataset(mock_dataset_config)
        samples = [dataset[i] for i in range(2)]
        batch = collate_fn(samples)

        assert len(batch["clip_ids"]) == 2
        assert batch["t0_us"].shape == (2,)
        assert batch["frames"].shape[0] == 2
        assert batch["ego_history_xyz"].shape[0] == 2

    def test_collate_fn_with_none_future(self, sample_clip_ids, mock_physical_ai_av):
        """Test collate_fn with no future trajectory."""
        from alpamayo_tools.dataloader import DatasetConfig, PhysicalAIDataset, collate_fn

        config = DatasetConfig(clip_ids=sample_clip_ids, include_future=False)
        dataset = PhysicalAIDataset(config)
        samples = [dataset[i] for i in range(2)]
        batch = collate_fn(samples)

        assert batch["ego_future_xyz"] is None
        assert batch["ego_future_rot"] is None


class TestEgomotionTransformation:
    """Tests for egomotion coordinate transformation."""

    def test_history_at_t0_is_origin(self, mock_dataset_config, mock_physical_ai_av):
        """Test that history trajectory at t0 is at origin."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        # Last history point (t0) should be at origin
        t0_position = sample["ego_history_xyz"][-1]
        assert torch.allclose(t0_position, torch.zeros(3), atol=1e-5)

    def test_history_rotation_at_t0_is_identity(self, mock_dataset_config, mock_physical_ai_av):
        """Test that history rotation at t0 is identity."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        # Last history rotation (t0) should be identity
        t0_rotation = sample["ego_history_rot"][-1]
        identity = torch.eye(3)
        assert torch.allclose(t0_rotation, identity, atol=1e-5)


class TestCameraOrdering:
    """Tests for camera ordering."""

    def test_cameras_sorted_by_index(self, mock_dataset_config, mock_physical_ai_av):
        """Test that cameras are sorted by index."""
        from alpamayo_tools.dataloader import PhysicalAIDataset

        dataset = PhysicalAIDataset(mock_dataset_config)
        sample = dataset[0]

        indices = sample["camera_indices"].numpy()
        assert np.all(indices[:-1] <= indices[1:]), "Camera indices should be sorted"
