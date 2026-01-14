"""Alpamayo-R1 inference wrapper."""

from __future__ import annotations

import dataclasses
from typing import Any, Literal

import numpy as np
import numpy.typing as npt
import torch


@dataclasses.dataclass
class PredictionResult:
    """Result from Alpamayo-R1 inference.

    Attributes:
        trajectory_xyz: Predicted 3D positions, shape (64, 3)
        trajectory_rot: Predicted rotation matrices, shape (64, 3, 3)
        reasoning_text: Chain-of-Cognition reasoning text
        all_trajectories_xyz: All sampled trajectories if num_samples > 1, shape (num_samples, 64, 3)
        all_trajectories_rot: All sampled rotations if num_samples > 1, shape (num_samples, 64, 3, 3)
    """

    trajectory_xyz: npt.NDArray[np.float32]  # (64, 3)
    trajectory_rot: npt.NDArray[np.float32]  # (64, 3, 3)
    reasoning_text: str

    # Optional: multiple trajectory samples
    all_trajectories_xyz: npt.NDArray[np.float32] | None = None  # (num_samples, 64, 3)
    all_trajectories_rot: npt.NDArray[np.float32] | None = None  # (num_samples, 64, 3, 3)


class AlpamayoPredictor:
    """High-level wrapper for Alpamayo-R1 inference.

    This class provides a simple interface for running Alpamayo-R1 inference
    on PhysicalAI-AV data.

    Example:
        >>> predictor = AlpamayoPredictor.from_pretrained()
        >>> result = predictor.predict_from_clip("clip_001", t0_us=5_100_000)
        >>> print(result.reasoning_text)
        >>> print(result.trajectory_xyz.shape)  # (64, 3)

    Notes:
        - Requires ~24GB+ GPU memory for bf16 inference
        - First prediction is slower due to model warmup
        - Requires alpamayo_r1 package installed from GitHub
    """

    def __init__(
        self,
        model: Any,
        processor: Any,
        tokenizer: Any,
        device: torch.device | str = "cuda",
        dtype: torch.dtype = torch.bfloat16,
    ) -> None:
        """Initialize with pre-loaded model.

        Use `from_pretrained()` for the standard initialization path.

        Args:
            model: Loaded AlpamayoR1 model
            processor: Loaded AutoProcessor for tokenization
            tokenizer: Model tokenizer
            device: Device for inference
            dtype: Model dtype
        """
        self.model = model
        self.processor = processor
        self.tokenizer = tokenizer
        self.device = torch.device(device)
        self.dtype = dtype

        # Dataset interface for loading data
        self._avdi = None

    @classmethod
    def from_pretrained(
        cls,
        model_id: str = "nvidia/Alpamayo-R1-10B",
        device: str = "cuda",
        dtype: torch.dtype = torch.bfloat16,
        quantization: Literal["none", "8bit", "4bit"] = "none",
    ) -> "AlpamayoPredictor":
        """Load Alpamayo-R1 model from HuggingFace.

        Args:
            model_id: HuggingFace model ID
            device: Device to load model on
            dtype: Model dtype (bfloat16 recommended)
            quantization: Quantization mode (requires bitsandbytes)

        Returns:
            Initialized AlpamayoPredictor

        Raises:
            ImportError: If alpamayo_r1 package is not installed
        """
        try:
            from alpamayo_r1.models.alpamayo_r1 import AlpamayoR1
            from alpamayo_r1 import helper
        except ImportError as e:
            raise ImportError(
                "alpamayo_r1 is required for inference. "
                "Install with: pip install git+https://github.com/NVlabs/alpamayo.git"
            ) from e

        # Quantization config
        load_kwargs = {}
        if quantization == "8bit":
            from transformers import BitsAndBytesConfig

            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        elif quantization == "4bit":
            from transformers import BitsAndBytesConfig

            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=dtype,
            )

        model = AlpamayoR1.from_pretrained(model_id, dtype=dtype, **load_kwargs)
        model = model.to(device)
        model.eval()

        processor = helper.get_processor(model.tokenizer)

        return cls(model, processor, model.tokenizer, device, dtype)

    @property
    def avdi(self):
        """Lazily initialize PhysicalAIAVDatasetInterface."""
        if self._avdi is None:
            import physical_ai_av

            self._avdi = physical_ai_av.PhysicalAIAVDatasetInterface()
        return self._avdi

    def predict(
        self,
        frames: torch.Tensor,
        ego_history_xyz: torch.Tensor,
        ego_history_rot: torch.Tensor,
        num_samples: int = 1,
        top_p: float = 0.98,
        temperature: float = 0.6,
        max_generation_length: int = 256,
    ) -> PredictionResult:
        """Run inference on pre-loaded data.

        Args:
            frames: Camera frames, shape (N_cameras * num_frames, 3, H, W)
            ego_history_xyz: History positions, shape (1, 1, num_history, 3)
            ego_history_rot: History rotations, shape (1, 1, num_history, 3, 3)
            num_samples: Number of trajectory samples to generate
            top_p: Nucleus sampling parameter
            temperature: Sampling temperature
            max_generation_length: Max tokens to generate for reasoning

        Returns:
            PredictionResult with trajectory and reasoning
        """
        from alpamayo_r1 import helper

        # Create VLM messages
        messages = helper.create_message(frames)

        # Tokenize
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=False,
            continue_final_message=True,
            return_dict=True,
            return_tensors="pt",
        )

        # Prepare model inputs
        model_inputs = {
            "tokenized_data": inputs,
            "ego_history_xyz": ego_history_xyz,
            "ego_history_rot": ego_history_rot,
        }
        model_inputs = helper.to_device(model_inputs, self.device)

        # Run inference
        with torch.autocast("cuda", dtype=self.dtype):
            with torch.no_grad():
                pred_xyz, pred_rot, extra = self.model.sample_trajectories_from_data_with_vlm_rollout(
                    data=model_inputs,
                    top_p=top_p,
                    temperature=temperature,
                    num_traj_samples=num_samples,
                    max_generation_length=max_generation_length,
                    return_extra=True,
                )

        # Extract outputs
        # pred_xyz: (B=1, num_traj_sets=1, num_samples, 64, 3)
        trajectory_xyz = pred_xyz[0, 0, 0].cpu().numpy().astype(np.float32)
        trajectory_rot = pred_rot[0, 0, 0].cpu().numpy().astype(np.float32)

        # Extract CoC text
        coc_texts = extra.get("cot", [[[""]]])
        coc_text = coc_texts[0][0][0] if coc_texts else ""

        result = PredictionResult(
            trajectory_xyz=trajectory_xyz,
            trajectory_rot=trajectory_rot,
            reasoning_text=coc_text,
        )

        # Include all samples if multiple requested
        if num_samples > 1:
            result.all_trajectories_xyz = pred_xyz[0, 0].cpu().numpy().astype(np.float32)
            result.all_trajectories_rot = pred_rot[0, 0].cpu().numpy().astype(np.float32)

        return result

    def predict_from_clip(
        self,
        clip_id: str,
        t0_us: int = 5_100_000,
        num_samples: int = 1,
        stream: bool = True,
        **kwargs,
    ) -> PredictionResult:
        """Run inference on a PhysicalAI-AV clip.

        Args:
            clip_id: Clip ID from PhysicalAI-AV dataset
            t0_us: Timestamp in microseconds for prediction
            num_samples: Number of trajectory samples
            stream: Whether to stream data from HuggingFace
            **kwargs: Additional arguments passed to predict()

        Returns:
            PredictionResult with trajectory and reasoning
        """
        from alpamayo_r1.load_physical_aiavdataset import load_physical_aiavdataset

        # Load data using NVIDIA's loader
        data = load_physical_aiavdataset(
            clip_id=clip_id,
            t0_us=t0_us,
            avdi=self.avdi,
            maybe_stream=stream,
        )

        # Flatten frames for VLM input
        frames = data["image_frames"].flatten(0, 1)  # (N_cam * num_frames, 3, H, W)

        return self.predict(
            frames=frames,
            ego_history_xyz=data["ego_history_xyz"],
            ego_history_rot=data["ego_history_rot"],
            num_samples=num_samples,
            **kwargs,
        )

    def predict_from_dataset_sample(
        self,
        sample: dict[str, torch.Tensor],
        num_samples: int = 1,
        **kwargs,
    ) -> PredictionResult:
        """Run inference on a sample from PhysicalAIDataset.

        Args:
            sample: Output from PhysicalAIDataset.__getitem__()
            num_samples: Number of trajectory samples
            **kwargs: Additional arguments passed to predict()

        Returns:
            PredictionResult with trajectory and reasoning
        """
        # Flatten frames: (N_cameras, num_frames, 3, H, W) -> (N, 3, H, W)
        frames = sample["frames"].flatten(0, 1)

        # Add batch dimensions
        ego_history_xyz = sample["ego_history_xyz"].unsqueeze(0).unsqueeze(0)
        ego_history_rot = sample["ego_history_rot"].unsqueeze(0).unsqueeze(0)

        return self.predict(
            frames=frames,
            ego_history_xyz=ego_history_xyz,
            ego_history_rot=ego_history_rot,
            num_samples=num_samples,
            **kwargs,
        )
