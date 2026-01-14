"""PyTorch Dataset wrapper for PhysicalAI-AV dataset."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Callable, Literal, TypedDict

import numpy as np
import numpy.typing as npt
import pandas as pd
import scipy.spatial.transform as spt
import torch
from torch.utils.data import Dataset

# Camera name type
CameraName = Literal[
    "camera_cross_left_120fov",
    "camera_front_wide_120fov",
    "camera_cross_right_120fov",
    "camera_front_tele_30fov",
    "camera_rear_left_70fov",
    "camera_rear_right_70fov",
    "camera_rear_tele_30fov",
]

# Default cameras used by Alpamayo-R1
DEFAULT_CAMERAS: tuple[CameraName, ...] = (
    "camera_cross_left_120fov",
    "camera_front_wide_120fov",
    "camera_cross_right_120fov",
    "camera_front_tele_30fov",
)

# Camera name to index mapping (consistent with Alpamayo)
CAMERA_NAME_TO_INDEX: dict[str, int] = {
    "camera_cross_left_120fov": 0,
    "camera_front_wide_120fov": 1,
    "camera_cross_right_120fov": 2,
    "camera_rear_left_70fov": 3,
    "camera_rear_tele_30fov": 4,
    "camera_rear_right_70fov": 5,
    "camera_front_tele_30fov": 6,
}


class SampleOutput(TypedDict):
    """Output from PhysicalAIDataset.__getitem__."""

    clip_id: str
    t0_us: int
    frames: torch.Tensor  # (N_cameras, num_frames, 3, H, W)
    camera_indices: torch.Tensor  # (N_cameras,)
    ego_history_xyz: torch.Tensor  # (num_history_steps, 3)
    ego_history_rot: torch.Tensor  # (num_history_steps, 3, 3)
    ego_future_xyz: torch.Tensor | None  # (num_future_steps, 3) or None
    ego_future_rot: torch.Tensor | None  # (num_future_steps, 3, 3) or None
    frame_timestamps: torch.Tensor  # (N_cameras, num_frames) microseconds


@dataclasses.dataclass
class DatasetConfig:
    """Configuration for PhysicalAIDataset.

    Attributes:
        clip_ids: List of clip IDs to include in the dataset
        clip_ids_file: Path to parquet/txt file with clip IDs
        t0_us: Timestamp (microseconds) for sampling (default: 5.1s into clip)
        num_history_steps: Number of history trajectory steps (default: 16 = 1.6s @ 10Hz)
        num_future_steps: Number of future trajectory steps (default: 64 = 6.4s @ 10Hz)
        time_step_s: Time step between trajectory points in seconds (default: 0.1s)
        cameras: Tuple of camera names to load
        num_frames: Number of video frames per camera
        cache_dir: Local cache directory for downloaded data
        stream: Whether to stream from HuggingFace (True) or use cached data (False)
        hf_token: HuggingFace token for authenticated access
        include_future: Whether to include ground truth future trajectory
    """

    clip_ids: list[str] | None = None
    clip_ids_file: str | Path | None = None

    # Temporal sampling
    t0_us: int = 5_100_000  # Default: 5.1s into clip
    num_history_steps: int = 16  # 1.6s @ 10Hz
    num_future_steps: int = 64  # 6.4s @ 10Hz
    time_step_s: float = 0.1  # 10Hz

    # Camera configuration
    cameras: tuple[CameraName, ...] = DEFAULT_CAMERAS
    num_frames: int = 4  # Frames per camera

    # Data loading
    cache_dir: str | Path | None = None
    stream: bool = False  # Stream from HuggingFace vs. use cached (default: cache)
    hf_token: str | None = None
    download_workers: int = 4  # Parallel workers for downloading

    # Optional features
    include_future: bool = True  # Include ground truth future trajectory

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.clip_ids is None and self.clip_ids_file is None:
            raise ValueError("Must specify either clip_ids or clip_ids_file")
        if self.clip_ids is not None and self.clip_ids_file is not None:
            raise ValueError("Cannot specify both clip_ids and clip_ids_file")
        if self.num_frames < 1:
            raise ValueError("num_frames must be at least 1")
        if self.num_history_steps < 1:
            raise ValueError("num_history_steps must be at least 1")


class PhysicalAIDataset(Dataset):
    """PyTorch Dataset for PhysicalAI-AV with video and egomotion.

    This dataset provides:
    - Multi-camera video frames decoded from H.264
    - Egomotion (pose, velocity, acceleration) interpolated at any timestamp
    - Optional ground truth future trajectories for training

    Example:
        >>> config = DatasetConfig(
        ...     clip_ids=["clip_001", "clip_002"],
        ...     cameras=("camera_front_wide_120fov",),
        ...     num_frames=4,
        ... )
        >>> dataset = PhysicalAIDataset(config)
        >>> sample = dataset[0]
        >>> print(sample["frames"].shape)  # (1, 4, 3, H, W)

    Notes:
        - Video readers are opened lazily and cached per-worker
        - Call `dataset.close()` or use context manager to release resources
        - For DataLoader with num_workers>0, each worker gets its own readers
    """

    def __init__(
        self,
        config: DatasetConfig,
        transform: Callable[[SampleOutput], SampleOutput] | None = None,
    ) -> None:
        """Initialize the dataset.

        Args:
            config: Dataset configuration
            transform: Optional transform applied to each sample
        """
        self.config = config
        self.transform = transform

        # Initialize NVIDIA dataset interface lazily
        self._avdi = None

        # Load clip IDs
        self.clip_ids = self._load_clip_ids()

        # Per-worker caches for video readers and egomotion interpolators
        self._video_readers: dict[tuple[str, str], object] = {}
        self._egomotion_cache: dict[str, object] = {}

    @property
    def avdi(self):
        """Lazily initialize PhysicalAIAVDatasetInterface."""
        if self._avdi is None:
            import physical_ai_av

            kwargs = {}
            if self.config.hf_token:
                kwargs["token"] = self.config.hf_token
            if self.config.cache_dir:
                kwargs["cache_dir"] = str(self.config.cache_dir)

            self._avdi = physical_ai_av.PhysicalAIAVDatasetInterface(**kwargs)
        return self._avdi

    def _load_clip_ids(self) -> list[str]:
        """Load clip IDs from config."""
        if self.config.clip_ids is not None:
            return list(self.config.clip_ids)

        path = Path(self.config.clip_ids_file)
        if path.suffix == ".parquet":
            df = pd.read_parquet(path)
            # Handle both 'clip_id' column and index
            if "clip_id" in df.columns:
                return df["clip_id"].tolist()
            else:
                return df.index.tolist()
        elif path.suffix == ".txt":
            return [line.strip() for line in path.read_text().strip().split("\n") if line.strip()]
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def download(self, show_progress: bool = True) -> None:
        """Download all data for configured clips before iteration.

        This is MUCH faster than streaming clip-by-clip because it:
        1. Groups clips by chunk (dataset organization)
        2. Downloads entire chunks at once (one HTTP request per chunk)
        3. Uses parallel workers for concurrent downloads

        After calling this, all subsequent data access is from local cache.

        Args:
            show_progress: Whether to show progress bar

        Example:
            >>> dataset = PhysicalAIDataset(config)
            >>> dataset.download()  # Downloads all chunks containing your clips
            >>> for sample in dataset:  # All reads are now local
            ...     process(sample)
        """
        from tqdm import tqdm

        # Ensure avdi is initialized and has metadata
        self.avdi.download_metadata()

        # Get all features we need to download
        features_to_download = list(self.config.cameras) + [
            self.avdi.features.LABELS.EGOMOTION
        ]

        # Group clips by chunk for efficient downloading
        clip_to_chunk = {}
        for clip_id in self.clip_ids:
            chunk_id = self.avdi.get_clip_chunk(clip_id)
            clip_to_chunk[clip_id] = chunk_id

        unique_chunks = list(set(clip_to_chunk.values()))

        if show_progress:
            print(f"Downloading {len(unique_chunks)} chunks for {len(self.clip_ids)} clips...")

        # Download by chunk (much more efficient than per-clip)
        iterator = tqdm(unique_chunks, desc="Downloading chunks") if show_progress else unique_chunks
        for chunk_id in iterator:
            self.avdi.download_chunk_features(
                chunk_id,
                features=features_to_download,
                max_workers=self.config.download_workers,
            )

        if show_progress:
            print(f"Download complete. All data cached locally.")

    def __len__(self) -> int:
        return len(self.clip_ids)

    def __getitem__(self, idx: int) -> SampleOutput:
        """Get a sample from the dataset."""
        clip_id = self.clip_ids[idx]
        t0_us = self.config.t0_us

        # Load egomotion data
        ego_data = self._load_egomotion(clip_id, t0_us)

        # Load camera frames
        frames, camera_indices, frame_timestamps = self._load_frames(clip_id, t0_us)

        sample: SampleOutput = {
            "clip_id": clip_id,
            "t0_us": t0_us,
            "frames": frames,
            "camera_indices": camera_indices,
            "ego_history_xyz": ego_data["history_xyz"],
            "ego_history_rot": ego_data["history_rot"],
            "ego_future_xyz": ego_data.get("future_xyz"),
            "ego_future_rot": ego_data.get("future_rot"),
            "frame_timestamps": frame_timestamps,
        }

        if self.transform is not None:
            sample = self.transform(sample)

        return sample

    def _load_egomotion(self, clip_id: str, t0_us: int) -> dict[str, torch.Tensor]:
        """Load and interpolate egomotion data, transformed to ego frame at t0."""
        cfg = self.config

        # Get or create interpolator
        if clip_id not in self._egomotion_cache:
            egomotion_interp = self.avdi.get_clip_feature(
                clip_id,
                self.avdi.features.LABELS.EGOMOTION,
                maybe_stream=cfg.stream,
            )
            self._egomotion_cache[clip_id] = egomotion_interp
        else:
            egomotion_interp = self._egomotion_cache[clip_id]

        time_step_us = int(cfg.time_step_s * 1_000_000)

        # History timestamps: [..., t0-0.2s, t0-0.1s, t0]
        history_offsets = np.arange(
            -(cfg.num_history_steps - 1) * time_step_us,
            time_step_us // 2,
            time_step_us,
            dtype=np.int64,
        )
        history_ts = t0_us + history_offsets

        # Query egomotion at history timestamps
        ego_history = egomotion_interp(history_ts)
        history_xyz = ego_history.pose.translation  # (N, 3)
        history_quat = ego_history.pose.rotation.as_quat()  # (N, 4)

        # Transform to local frame at t0
        # Transformation: xyz_local = R_t0^{-1} @ (xyz_world - xyz_t0)
        t0_xyz = history_xyz[-1].copy()
        t0_rot = spt.Rotation.from_quat(history_quat[-1])
        t0_rot_inv = t0_rot.inv()

        history_xyz_local = t0_rot_inv.apply(history_xyz - t0_xyz)
        history_rot_local = (t0_rot_inv * spt.Rotation.from_quat(history_quat)).as_matrix()

        result = {
            "history_xyz": torch.from_numpy(history_xyz_local).float(),
            "history_rot": torch.from_numpy(history_rot_local).float(),
        }

        # Future trajectory (for training)
        if cfg.include_future:
            future_offsets = np.arange(
                time_step_us,
                int((cfg.num_future_steps + 0.5) * time_step_us),
                time_step_us,
                dtype=np.int64,
            )
            future_ts = t0_us + future_offsets

            ego_future = egomotion_interp(future_ts)
            future_xyz = ego_future.pose.translation
            future_quat = ego_future.pose.rotation.as_quat()

            future_xyz_local = t0_rot_inv.apply(future_xyz - t0_xyz)
            future_rot_local = (t0_rot_inv * spt.Rotation.from_quat(future_quat)).as_matrix()

            result["future_xyz"] = torch.from_numpy(future_xyz_local).float()
            result["future_rot"] = torch.from_numpy(future_rot_local).float()

        return result

    def _load_frames(
        self, clip_id: str, t0_us: int
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Load video frames from all configured cameras."""
        cfg = self.config
        time_step_us = int(cfg.time_step_s * 1_000_000)

        # Frame timestamps: [t0-(n-1)*dt, ..., t0-dt, t0]
        frame_ts = np.array(
            [t0_us - (cfg.num_frames - 1 - i) * time_step_us for i in range(cfg.num_frames)],
            dtype=np.int64,
        )

        frames_list = []
        indices_list = []
        timestamps_list = []

        for cam_name in cfg.cameras:
            # Get or create video reader
            cache_key = (clip_id, cam_name)
            if cache_key not in self._video_readers:
                reader = self.avdi.get_clip_feature(
                    clip_id,
                    cam_name,
                    maybe_stream=cfg.stream,
                )
                self._video_readers[cache_key] = reader
            else:
                reader = self._video_readers[cache_key]

            # Decode frames
            frames, actual_ts = reader.decode_images_from_timestamps(frame_ts)
            # frames: (num_frames, H, W, 3) uint8

            # Convert to (num_frames, 3, H, W) tensor
            frames_tensor = torch.from_numpy(frames).permute(0, 3, 1, 2)

            frames_list.append(frames_tensor)
            indices_list.append(CAMERA_NAME_TO_INDEX.get(cam_name, 0))
            timestamps_list.append(torch.from_numpy(actual_ts.astype(np.int64)))

        # Stack: (N_cameras, num_frames, 3, H, W)
        all_frames = torch.stack(frames_list, dim=0)
        camera_indices = torch.tensor(indices_list, dtype=torch.int64)
        all_timestamps = torch.stack(timestamps_list, dim=0)

        # Sort by camera index for consistent ordering
        sort_order = torch.argsort(camera_indices)
        all_frames = all_frames[sort_order]
        camera_indices = camera_indices[sort_order]
        all_timestamps = all_timestamps[sort_order]

        return all_frames, camera_indices, all_timestamps

    def close(self) -> None:
        """Close all video readers and release resources."""
        for reader in self._video_readers.values():
            if hasattr(reader, "close"):
                reader.close()
        self._video_readers.clear()
        self._egomotion_cache.clear()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup


def collate_fn(batch: list[SampleOutput]) -> dict[str, torch.Tensor | list]:
    """Custom collate function for DataLoader.

    Handles variable-sized outputs and None values.

    Args:
        batch: List of samples from PhysicalAIDataset

    Returns:
        Batched dictionary with tensors stacked along batch dimension
    """
    result = {}

    # String fields
    result["clip_ids"] = [s["clip_id"] for s in batch]
    result["t0_us"] = torch.tensor([s["t0_us"] for s in batch], dtype=torch.int64)

    # Tensor fields - stack along batch dimension
    result["frames"] = torch.stack([s["frames"] for s in batch])
    result["camera_indices"] = torch.stack([s["camera_indices"] for s in batch])
    result["ego_history_xyz"] = torch.stack([s["ego_history_xyz"] for s in batch])
    result["ego_history_rot"] = torch.stack([s["ego_history_rot"] for s in batch])
    result["frame_timestamps"] = torch.stack([s["frame_timestamps"] for s in batch])

    # Optional fields - only include if present in all samples
    if batch[0]["ego_future_xyz"] is not None:
        result["ego_future_xyz"] = torch.stack([s["ego_future_xyz"] for s in batch])
        result["ego_future_rot"] = torch.stack([s["ego_future_rot"] for s in batch])
    else:
        result["ego_future_xyz"] = None
        result["ego_future_rot"] = None

    return result
