import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("CountBenchQA")
class CountBenchLoader(BaseDatasetLoader):
    """Loads the Count-Bench dataset from the Hugging Face hub."""

    def __init__(self):  # Added **kwargs to ignore unused args
        try:
            count = load_dataset("vikhyatk/CountBenchQA")
            self.dataset = count["test"]
        except Exception as e:
            logger.error("Failed to load 'vikhyatk/CountBenchQA' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the CountBench dataset."""
        example = self.dataset[idx]
        task = "count"
        question = example["question"]
        correct_answer = example["number"]
        image = example["image"]

        return {
            "image": [image],
            "question": str(question),
            "correct_answer": str(correct_answer),
            "task_name": task,
            "sample_id": f"CountBench_{idx}"
        }