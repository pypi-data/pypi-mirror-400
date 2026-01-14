# alpamayo-tools

Community tools for NVIDIA's [Alpamayo-R1](https://developer.nvidia.com/drive/alpamayo) and [PhysicalAI-AV](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles) ecosystem.

## Overview

This package provides:

- **`PhysicalAIDataset`** — PyTorch Dataset that handles video decoding, egomotion interpolation, and coordinate transformation to ego-frame. Useful for training your own models on PhysicalAI-AV without writing the data loading boilerplate.

- **`alpamayo-generate-labels`** — CLI for running Alpamayo-R1 inference at scale. Supports checkpointing, resume, and multi-GPU sharding. Useful for distillation workflows where you need teacher labels for thousands of clips.

- **`CoCEmbedder`** — Sentence embedding for Chain-of-Cognition reasoning text. Useful for retrieval, clustering, or analyzing Alpamayo's reasoning outputs.

All trajectory data is automatically transformed to the ego vehicle's local frame at t0 (the coordinate system Alpamayo-R1 expects).

## Installation

```bash
pip install alpamayo-tools
```

With optional dependencies:
```bash
pip install alpamayo-tools[embeddings]  # CoC embeddings
pip install alpamayo-tools[inference]   # Alpamayo inference wrapper
pip install alpamayo-tools[all]         # Everything
```

For inference, also install alpamayo_r1:
```bash
pip install git+https://github.com/NVlabs/alpamayo.git
```

## Usage

### DataLoader

```python
from alpamayo_tools import PhysicalAIDataset, DatasetConfig, collate_fn
from torch.utils.data import DataLoader

config = DatasetConfig(
    clip_ids=["clip_001", "clip_002"],
    cameras=("camera_front_wide_120fov", "camera_front_tele_30fov"),
    num_frames=4,
)

dataset = PhysicalAIDataset(config)

# Recommended: Download all data upfront (MUCH faster than streaming)
dataset.download()  # Downloads by chunk, uses parallel workers

loader = DataLoader(dataset, batch_size=4, collate_fn=collate_fn)

for batch in loader:
    frames = batch["frames"]  # (B, N_cam, T, 3, H, W)
    history = batch["ego_history_xyz"]  # (B, 16, 3)
    future = batch["ego_future_xyz"]  # (B, 64, 3)
```

**Why download first?** The PhysicalAI-AV dataset is organized by chunks, each containing multiple clips. Downloading by chunk is much faster than streaming clip-by-clip (one HTTP request per chunk vs per clip). The `download()` method groups your clips by chunk and downloads them with parallel workers.

For quick testing with a few clips, you can still stream:
```python
config = DatasetConfig(clip_ids=["clip_001"], stream=True)
```

### Inference

```python
from alpamayo_tools.inference import AlpamayoPredictor
import torch

predictor = AlpamayoPredictor.from_pretrained("nvidia/Alpamayo-R1-10B", dtype=torch.bfloat16)
result = predictor.predict_from_clip("clip_001", t0_us=5_100_000)

print(result.trajectory_xyz.shape)  # (64, 3)
print(result.reasoning_text)
```

### Generate Teacher Labels

```bash
alpamayo-generate-labels \
    --clip-ids-file train_clips.parquet \
    --output-dir ./labels

# Multi-GPU
CUDA_VISIBLE_DEVICES=0 alpamayo-generate-labels --clip-ids-file clips.parquet --output-dir ./labels --shard 0/4
CUDA_VISIBLE_DEVICES=1 alpamayo-generate-labels --clip-ids-file clips.parquet --output-dir ./labels --shard 1/4

# Resume after interruption
alpamayo-generate-labels --clip-ids-file clips.parquet --output-dir ./labels --resume
```

### CoC Embeddings

```python
from alpamayo_tools import CoCEmbedder

embedder = CoCEmbedder()
embeddings = embedder.embed(["The vehicle ahead is braking."])  # (1, 384)
```

## Dataset Output

| Key | Shape | Description |
|-----|-------|-------------|
| `frames` | `(N_cam, T, 3, H, W)` | Camera frames (uint8) |
| `ego_history_xyz` | `(16, 3)` | Past 1.6s trajectory in ego frame |
| `ego_history_rot` | `(16, 3, 3)` | Past rotations in ego frame |
| `ego_future_xyz` | `(64, 3)` | Future 6.4s trajectory in ego frame |
| `ego_future_rot` | `(64, 3, 3)` | Future rotations in ego frame |
| `clip_id` | `str` | Clip identifier (`clip_ids` when batched) |
| `t0_us` | `int` | Reference timestamp (microseconds) |

## Requirements

- Python 3.12+
- PyTorch 2.0+
- For inference: GPU with 24GB+ VRAM

## Related

- [Alpamayo-R1 Model](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [PhysicalAI-AV Dataset](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)
- [Alpamayo GitHub](https://github.com/NVlabs/alpamayo)

## License

MIT
