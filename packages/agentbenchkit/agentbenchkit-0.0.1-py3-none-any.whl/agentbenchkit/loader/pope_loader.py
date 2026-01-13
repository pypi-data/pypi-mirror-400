import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("POPE")
class POPE(BaseDatasetLoader):
    """Loads the 'lmms-lab/POPE' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/POPE' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset = load_dataset("lmms-lab/POPE", "default", split="test")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/POPE': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the POPE dataset."""
        example = self.dataset[idx]
        question = example["question"] # + '\nPlease answer yes or no.'
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answer"],
            "task_name": "pope",  # Dataset has no specific category field
            "sample_id": f"pope_{idx}",
        }
