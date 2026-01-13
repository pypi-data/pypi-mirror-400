import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MME")
class MME(BaseDatasetLoader):
    """Loads the 'lmms-lab/MME' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/MME' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/MME")
            self.dataset = load_dataset("lmms-lab/MME", split="test")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/MME': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MME dataset."""
        example = self.dataset[idx]
        question = example["question"]
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answer"].lower(),
            "task_name": example["category"],  # Dataset has no specific category field
            "sample_id": example["question_id"],
        }
