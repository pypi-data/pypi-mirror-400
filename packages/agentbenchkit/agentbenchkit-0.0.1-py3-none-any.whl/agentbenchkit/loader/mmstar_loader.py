import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MMStar")
class MMStar(BaseDatasetLoader):
    """Loads the 'Lin-Chen/MMStar' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'Lin-Chen/MMStar' (val split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("Lin-Chen/MMStar", split="val")
        except Exception as e:
            logger.error("Failed to load 'Lin-Chen/MMStar': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MMStar dataset."""
        example = self.dataset[idx]
        question = example["question"]
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answer"],
            "task_name": example["category"],  # Dataset has no specific category field
            "sample_id": f"mmstar_{idx}",
        }
