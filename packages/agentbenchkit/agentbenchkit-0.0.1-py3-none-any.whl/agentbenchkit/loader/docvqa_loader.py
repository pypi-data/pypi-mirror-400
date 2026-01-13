
import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("DocVQA")
class DocVQA(BaseDatasetLoader):
    """Loads the 'lmms-lab/DocVQA' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/DocVQA' (validation split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset = load_dataset("lmms-lab/DocVQA", "DocVQA", split="validation")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/DocVQA': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the DocVQA dataset."""
        example = self.dataset[idx]
        question = example["question"]
        task_name = "|".join(example["question_types"])
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answers"],
            "task_name": task_name,  # Dataset has no specific category field
            "sample_id": f"docvqa_{idx}",
        }
