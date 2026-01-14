"""Pytest fixtures and mocks for testing alpamayo-tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
import scipy.spatial.transform as spt


# Sample clip IDs for testing
SAMPLE_CLIP_IDS = ["clip_001", "clip_002", "clip_003"]


@dataclass
class MockPose:
    """Mock pose object with translation and rotation."""

    translation: np.ndarray
    rotation: spt.Rotation


@dataclass
class MockEgomotionState:
    """Mock egomotion state returned by interpolator."""

    pose: MockPose


class MockEgomotionInterpolator:
    """Mock egomotion interpolator."""

    def __init__(self, num_points: int = 100):
        # Generate a simple trajectory: moving forward in x direction
        self.num_points = num_points
        self._time_range = (0, 10_000_000)  # 0 to 10 seconds in microseconds

    def __call__(self, timestamps: np.ndarray) -> MockEgomotionState:
        """Interpolate egomotion at given timestamps."""
        n = len(timestamps)

        # Generate positions: moving forward in x
        t_normalized = (timestamps - timestamps[0]) / 1_000_000  # seconds
        positions = np.zeros((n, 3), dtype=np.float64)
        positions[:, 0] = t_normalized * 10  # 10 m/s forward
        positions[:, 1] = np.sin(t_normalized * 0.5)  # slight lateral motion
        positions[:, 2] = 0.0  # constant height

        # Generate rotations: identity (no rotation)
        quaternions = np.zeros((n, 4), dtype=np.float64)
        quaternions[:, 3] = 1.0  # [0, 0, 0, 1] = identity quaternion

        rotation = spt.Rotation.from_quat(quaternions)
        pose = MockPose(translation=positions, rotation=rotation)

        return MockEgomotionState(pose=pose)

    @property
    def time_range(self) -> tuple[int, int]:
        return self._time_range


class MockVideoReader:
    """Mock video reader for testing."""

    def __init__(self, height: int = 480, width: int = 640):
        self.height = height
        self.width = width
        self._closed = False

    def decode_images_from_timestamps(
        self, timestamps: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Decode frames at given timestamps."""
        n = len(timestamps)
        # Generate random frames
        frames = np.random.randint(0, 256, (n, self.height, self.width, 3), dtype=np.uint8)
        return frames, timestamps.astype(np.float64)

    def close(self):
        """Close the reader."""
        self._closed = True

    @property
    def timestamps(self) -> np.ndarray:
        """Available timestamps."""
        return np.arange(0, 10_000_000, 33333, dtype=np.int64)  # ~30 fps


class MockFeatures:
    """Mock features object."""

    class CAMERA:
        CAMERA_CROSS_LEFT_120FOV = "camera_cross_left_120fov"
        CAMERA_FRONT_WIDE_120FOV = "camera_front_wide_120fov"
        CAMERA_CROSS_RIGHT_120FOV = "camera_cross_right_120fov"
        CAMERA_FRONT_TELE_30FOV = "camera_front_tele_30fov"
        ALL = [
            "camera_cross_left_120fov",
            "camera_front_wide_120fov",
            "camera_cross_right_120fov",
            "camera_front_tele_30fov",
        ]

    class LABELS:
        EGOMOTION = "egomotion"


class MockPhysicalAIAVDatasetInterface:
    """Mock PhysicalAIAVDatasetInterface for testing."""

    def __init__(self, **kwargs):
        self.features = MockFeatures()
        self._video_readers: dict[tuple[str, str], MockVideoReader] = {}
        self._egomotion_interps: dict[str, MockEgomotionInterpolator] = {}

    def get_clip_feature(
        self, clip_id: str, feature: str, maybe_stream: bool = True
    ) -> Any:
        """Get a clip feature."""
        if feature == "egomotion":
            if clip_id not in self._egomotion_interps:
                self._egomotion_interps[clip_id] = MockEgomotionInterpolator()
            return self._egomotion_interps[clip_id]
        else:
            # Camera feature
            key = (clip_id, feature)
            if key not in self._video_readers:
                self._video_readers[key] = MockVideoReader()
            return self._video_readers[key]

    def download_clip_features(self, clip_id: str, features: list[str]) -> None:
        """Mock download - does nothing."""
        pass


@pytest.fixture
def mock_physical_ai_av(monkeypatch):
    """Fixture to mock physical_ai_av module."""
    mock_module = MagicMock()
    mock_module.PhysicalAIAVDatasetInterface = MockPhysicalAIAVDatasetInterface

    monkeypatch.setitem(
        __import__("sys").modules, "physical_ai_av", mock_module
    )
    return mock_module


@pytest.fixture
def sample_clip_ids() -> list[str]:
    """Fixture providing sample clip IDs."""
    return SAMPLE_CLIP_IDS.copy()


@pytest.fixture
def temp_clip_ids_file(tmp_path, sample_clip_ids) -> str:
    """Fixture creating a temporary clip IDs file."""
    import pandas as pd

    path = tmp_path / "clip_ids.parquet"
    df = pd.DataFrame({"clip_id": sample_clip_ids})
    df.to_parquet(path)
    return str(path)


@pytest.fixture
def temp_clip_ids_txt(tmp_path, sample_clip_ids) -> str:
    """Fixture creating a temporary clip IDs text file."""
    path = tmp_path / "clip_ids.txt"
    path.write_text("\n".join(sample_clip_ids))
    return str(path)


@pytest.fixture
def mock_dataset_config(sample_clip_ids, mock_physical_ai_av):
    """Fixture providing a mock DatasetConfig."""
    from alpamayo_tools.dataloader import DatasetConfig

    return DatasetConfig(
        clip_ids=sample_clip_ids,
        num_frames=4,
        num_history_steps=16,
        num_future_steps=64,
        stream=True,
    )
