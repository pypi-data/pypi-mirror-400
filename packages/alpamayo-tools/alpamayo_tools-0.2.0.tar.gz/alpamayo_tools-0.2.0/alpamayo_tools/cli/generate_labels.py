"""CLI for generating teacher labels with Alpamayo-R1."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate teacher labels using Alpamayo-R1",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--clip-ids",
        type=str,
        nargs="+",
        help="List of clip IDs to process",
    )
    input_group.add_argument(
        "--clip-ids-file",
        type=Path,
        help="Path to parquet/txt file with clip IDs",
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to save output files",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="teacher_labels",
        help="Base name for output files",
    )

    # Sampling options
    parser.add_argument(
        "--t0-us",
        type=int,
        default=5_100_000,
        help="Timestamp (microseconds) for sampling",
    )

    # Model options
    parser.add_argument(
        "--model-id",
        type=str,
        default="nvidia/Alpamayo-R1-10B",
        help="HuggingFace model ID",
    )
    parser.add_argument(
        "--dtype",
        type=str,
        choices=["bf16", "fp16", "fp32"],
        default="bf16",
        help="Model dtype",
    )
    parser.add_argument(
        "--quantization",
        type=str,
        choices=["none", "8bit", "4bit"],
        default="none",
        help="Quantization mode",
    )

    # Embedding options
    parser.add_argument(
        "--embed-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence-transformers model for CoC embedding",
    )
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Skip CoC embedding",
    )

    # Processing options
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=100,
        help="Save checkpoint every N clips",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint if available",
    )

    # Sharding
    parser.add_argument(
        "--shard",
        type=str,
        default=None,
        help="Shard specification as 'i/n' (e.g., '0/2' for first half)",
    )

    # Limits
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of clips to process (for testing)",
    )

    return parser.parse_args()


def load_clip_ids(args: argparse.Namespace) -> list[str]:
    """Load clip IDs from arguments."""
    if args.clip_ids:
        return list(args.clip_ids)

    path = args.clip_ids_file
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
        if "clip_id" in df.columns:
            return df["clip_id"].tolist()
        else:
            return df.index.tolist()
    elif path.suffix == ".txt":
        return [
            line.strip()
            for line in path.read_text().strip().split("\n")
            if line.strip()
        ]
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def save_results(
    results: list[dict],
    path: Path,
    include_embeddings: bool = True,
) -> None:
    """Save results to npz file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    save_data = {
        "clip_ids": np.array([r["clip_id"] for r in results], dtype=object),
        "t0_us": np.array([r["t0_us"] for r in results], dtype=np.int64),
        "trajectory_xyz": np.stack([r["trajectory_xyz"] for r in results]).astype(
            np.float32
        ),
        "trajectory_rot": np.stack([r["trajectory_rot"] for r in results]).astype(
            np.float32
        ),
        "coc_texts": np.array([r["coc_text"] for r in results], dtype=object),
    }

    if include_embeddings and results and "coc_embedding" in results[0]:
        save_data["coc_embeddings"] = np.stack(
            [r["coc_embedding"] for r in results]
        ).astype(np.float32)

    np.savez_compressed(path, **save_data)
    logger.info(f"Saved {len(results)} samples to {path}")


def load_checkpoint(path: Path) -> tuple[set[str], list[dict]]:
    """Load checkpoint if exists."""
    if not path.exists():
        return set(), []

    logger.info(f"Loading checkpoint from {path}")
    data = np.load(path, allow_pickle=True)

    processed_ids = set(data["clip_ids"].tolist())
    results = []

    has_embeddings = "coc_embeddings" in data

    for i in range(len(data["clip_ids"])):
        result = {
            "clip_id": data["clip_ids"][i],
            "t0_us": int(data["t0_us"][i]),
            "trajectory_xyz": data["trajectory_xyz"][i],
            "trajectory_rot": data["trajectory_rot"][i],
            "coc_text": data["coc_texts"][i],
        }
        if has_embeddings:
            result["coc_embedding"] = data["coc_embeddings"][i]
        results.append(result)

    logger.info(f"Loaded {len(results)} samples from checkpoint")
    return processed_ids, results


def main() -> int:
    """Main entry point."""
    args = parse_args()

    import torch

    from alpamayo_tools.inference import AlpamayoPredictor
    from alpamayo_tools.embeddings import CoCEmbedder

    # Setup output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load clip IDs
    clip_ids = load_clip_ids(args)
    logger.info(f"Loaded {len(clip_ids)} clip IDs")

    # Apply sharding
    shard_suffix = ""
    if args.shard:
        shard_idx, num_shards = map(int, args.shard.split("/"))
        shard_size = len(clip_ids) // num_shards
        start = shard_idx * shard_size
        end = (
            len(clip_ids) if shard_idx == num_shards - 1 else (shard_idx + 1) * shard_size
        )
        clip_ids = clip_ids[start:end]
        shard_suffix = f"_shard{shard_idx}"
        logger.info(f"Shard {shard_idx}/{num_shards}: {len(clip_ids)} clips")

    # Apply limit
    if args.limit:
        clip_ids = clip_ids[: args.limit]
        logger.info(f"Limited to {args.limit} clips")

    # Output paths
    output_path = args.output_dir / f"{args.output_name}{shard_suffix}.npz"
    checkpoint_path = args.output_dir / f"{args.output_name}{shard_suffix}_checkpoint.npz"

    # Load checkpoint if resuming
    processed_ids: set[str] = set()
    results: list[dict] = []
    if args.resume:
        processed_ids, results = load_checkpoint(checkpoint_path)

    remaining_clips = [c for c in clip_ids if c not in processed_ids]
    logger.info(f"Remaining clips to process: {len(remaining_clips)}")

    if not remaining_clips:
        logger.info("All clips already processed!")
        if results:
            save_results(results, output_path, include_embeddings=not args.no_embed)
        return 0

    # Load models
    dtype_map = {
        "bf16": torch.bfloat16,
        "fp16": torch.float16,
        "fp32": torch.float32,
    }
    logger.info(f"Loading model: {args.model_id}")
    predictor = AlpamayoPredictor.from_pretrained(
        model_id=args.model_id,
        dtype=dtype_map[args.dtype],
        quantization=args.quantization,
    )
    logger.info("Model loaded successfully")

    embedder = None
    if not args.no_embed:
        logger.info(f"Loading embedding model: {args.embed_model}")
        embedder = CoCEmbedder(model_name=args.embed_model)
        logger.info("Embedding model loaded")

    # Process clips
    start_time = time.time()
    failed_clips = []
    pending_results = []

    try:
        for i, clip_id in enumerate(tqdm(remaining_clips, desc="Processing clips")):
            try:
                result = predictor.predict_from_clip(clip_id, t0_us=args.t0_us)
                pending_results.append(
                    {
                        "clip_id": clip_id,
                        "t0_us": args.t0_us,
                        "trajectory_xyz": result.trajectory_xyz,
                        "trajectory_rot": result.trajectory_rot,
                        "coc_text": result.reasoning_text,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to process {clip_id}: {e}")
                failed_clips.append(clip_id)
                continue

            # Save checkpoint periodically
            if len(pending_results) >= args.checkpoint_interval:
                # Embed CoC texts
                if embedder:
                    coc_texts = [r["coc_text"] for r in pending_results]
                    embeddings = embedder.embed(coc_texts)
                    for j, emb in enumerate(embeddings):
                        pending_results[j]["coc_embedding"] = emb

                results.extend(pending_results)
                pending_results = []

                save_results(results, checkpoint_path, include_embeddings=embedder is not None)

                elapsed = time.time() - start_time
                clips_per_sec = (i + 1) / elapsed
                eta = (len(remaining_clips) - i - 1) / clips_per_sec / 3600
                logger.info(
                    f"Progress: {i + 1}/{len(remaining_clips)} | "
                    f"Speed: {clips_per_sec:.2f} clips/s | "
                    f"ETA: {eta:.1f}h"
                )

        # Process remaining pending results
        if pending_results:
            if embedder:
                coc_texts = [r["coc_text"] for r in pending_results]
                embeddings = embedder.embed(coc_texts)
                for j, emb in enumerate(embeddings):
                    pending_results[j]["coc_embedding"] = emb
            results.extend(pending_results)

    except KeyboardInterrupt:
        logger.info("Interrupted by user. Saving checkpoint...")
        if pending_results:
            if embedder:
                coc_texts = [r["coc_text"] for r in pending_results]
                embeddings = embedder.embed(coc_texts)
                for j, emb in enumerate(embeddings):
                    pending_results[j]["coc_embedding"] = emb
            results.extend(pending_results)
        save_results(results, checkpoint_path, include_embeddings=embedder is not None)
        return 1

    # Save final results
    save_results(results, output_path, include_embeddings=embedder is not None)

    # Summary
    elapsed = time.time() - start_time
    logger.info(f"=== Complete ===")
    logger.info(f"Total time: {elapsed / 3600:.2f}h")
    logger.info(f"Successful: {len(results)}")
    logger.info(f"Failed: {len(failed_clips)}")
    logger.info(f"Output: {output_path}")

    if failed_clips:
        failed_path = args.output_dir / f"{args.output_name}{shard_suffix}_failed.json"
        with open(failed_path, "w") as f:
            json.dump(failed_clips, f)
        logger.info(f"Failed clips saved to: {failed_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
