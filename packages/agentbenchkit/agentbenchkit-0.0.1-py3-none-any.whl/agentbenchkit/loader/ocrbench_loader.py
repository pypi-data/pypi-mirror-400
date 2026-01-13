
import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("OCRBench")
class OCRBench(BaseDatasetLoader):
    """Loads the 'echo840/OCRBench' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'echo840/OCRBench' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("echo840/OCRBench", split="test")
        except Exception as e:
            logger.error("Failed to load 'echo840/OCRBench': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the OCRBench dataset."""
        example = self.dataset[idx]
        question = example["question"] # + "\nPlease strictly distinguish between upper and lower case."
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answer"],
            "task_name": example["question_type"],  # Dataset has no specific category field
            "sample_id": f"ocrbench_{idx}",
        }
