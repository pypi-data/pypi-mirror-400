"""alpamayo-tools: Community tools for NVIDIA's Alpamayo/PhysicalAI-AV ecosystem."""

__version__ = "0.1.0"

from alpamayo_tools.dataloader import DatasetConfig, PhysicalAIDataset, collate_fn
from alpamayo_tools.embeddings import CoCEmbedder

__all__ = [
    "DatasetConfig",
    "PhysicalAIDataset",
    "collate_fn",
    "CoCEmbedder",
]


def get_alpamayo_predictor():
    """Lazy import for AlpamayoPredictor (heavy dependencies).

    Returns:
        AlpamayoPredictor class

    Raises:
        ImportError: If inference dependencies are not installed
    """
    from alpamayo_tools.inference import AlpamayoPredictor
    return AlpamayoPredictor
